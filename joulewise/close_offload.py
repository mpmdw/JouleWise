"""Close-interval byte custody. No measurement file is decoded or parsed.

Only this tool's own JSON metadata is parsed. Python 3.14 supplies zstd;
imports stay lazy so structural tests also run on the repository's 3.13 CI.
"""
from __future__ import annotations

import argparse
import contextlib
from dataclasses import dataclass
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import signal
import stat
import subprocess
import sys
import tarfile
import time

OK, UPLOAD_PENDING, VERIFY_FAILED, DEADLINE, BUSY = 0, 20, 21, 22, 23
SCHEMA = "joulewise.close-offload.v1"
RUNNERS = r"(^|/|[[:space:]])(run_align_r1_smoke|cadence_legs_runner|launch_cadence_span|align_r1_runtime|align_r0_checks|align_v4_session|align_r1_rehearsal)([.]py)?([[:space:]]|$)"
SAFE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
BLOCK = 1024 * 1024


class Refusal(Exception):
    code = VERIFY_FAILED


class OutOfTime(Refusal):
    code = DEADLINE


class HostBusy(Refusal):
    code = BUSY


class Pending(Refusal):
    code = UPLOAD_PENDING


@dataclass
class Config:
    deadline: float
    campaign_root: Path = Path("/Users/edr/campaign-out")
    work_root: Path = Path("/Users/edr/code/jw-wt")
    cloud_root: Path = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/JouleWise-offload/spans"
    state_root: Path = Path("/Users/Shared/JouleWise/close-offload")
    marker_root: Path = Path("/Users/Shared/JouleWise/desk-copy")
    fence: Path = Path("/Users/edr/night-custody/magistrate/desk_fence.json")
    air_root: Path = Path("/Volumes/JW-EXT/cadence-desk")
    catch_up: bool = False
    cloud_only_allowed: bool = True
    poll_seconds: float = 5.0
    air_pull: str | None = None
    receipt_sha256: str | None = None


class Guard:
    def __init__(self, config):
        self.config = config
        # Leave the supervisor a short exit/reap margin. It still enforces the exact deadline.
        self.end = time.monotonic() + max(0, config.deadline - time.time() - 0.2)

    def remaining(self):
        left = min(self.config.deadline - time.time(), self.end - time.monotonic())
        if left <= 0:
            raise OutOfTime("DEADLINE")
        return left

    def command(self, args):
        try:
            return subprocess.run(args, capture_output=True, timeout=self.remaining(), check=False)
        except subprocess.TimeoutExpired:
            raise OutOfTime("DEADLINE") from None

    def quiet(self):
        self.remaining()
        if os.path.lexists(self.config.fence):
            raise HostBusy("DESK_FENCE_PRESENT")
        probe = self.command(["pgrep", "-f", RUNNERS])
        if probe.returncode == 0:
            raise HostBusy("RUNNER_PRESENT")
        if probe.returncode != 1:
            raise HostBusy("RUNNER_CENSUS_FAILED")


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    part = path.with_name(path.name + ".tmp")
    with part.open("wb") as handle:
        handle.write(canonical(value))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(part, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def regular(path):
    return stat.S_ISREG(path.lstat().st_mode)


def safe_name(name):
    if not SAFE.fullmatch(name) or name in (".", ".."):
        raise Refusal("UNSAFE_NAME")
    return name


def file_hash(path, guard):
    h = hashlib.sha256()
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as handle:
        before = os.fstat(handle.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise Refusal("NONREGULAR_FILE")
        while True:
            guard.remaining()
            chunk = handle.read(BLOCK)
            if not chunk:
                break
            h.update(chunk)
        after = os.fstat(handle.fileno())
        if (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise Refusal("SOURCE_CHANGED")
    return h.hexdigest()


def member_name(name):
    p = PurePosixPath(name)
    if name != "." and (p.is_absolute() or ".." in p.parts or str(p) != name):
        raise Refusal("UNSAFE_ARCHIVE_MEMBER")
    return name


def link_safe(name, link):
    if os.path.normpath(link) != link:
        raise Refusal("NONCANONICAL_SYMLINK")
    target = PurePosixPath(link)
    if target.is_absolute():
        raise Refusal("ABSOLUTE_SYMLINK")
    depth = len(PurePosixPath(name).parent.parts)
    for part in target.parts:
        depth += -1 if part == ".." else (0 if part == "." else 1)
        if depth < 0:
            raise Refusal("ESCAPING_SYMLINK")


def manifest(root, guard):
    if root.is_symlink() or not root.is_dir():
        raise Refusal("SOURCE_NOT_DIRECTORY")
    entries = {}
    def visit(path, name):
        guard.remaining()
        st = path.lstat()
        if stat.S_ISLNK(st.st_mode):
            link = os.readlink(path)
            link_safe(name, link)
            # The 3.14 data extraction filter normalizes links. Accept only
            # canonical, resolvable internal links so restoration is proved
            # before removing the source (including chains and cycles).
            try:
                resolved = path.resolve(strict=True)
            except (OSError, RuntimeError):
                raise Refusal("UNRESOLVED_SYMLINK") from None
            if not resolved.is_relative_to(root.resolve()):
                raise Refusal("ESCAPING_SYMLINK")
            entries[name] = {"type": "link", "target": link}
        elif stat.S_ISREG(st.st_mode):
            entries[name] = {"type": "file", "size": st.st_size, "sha256": file_hash(path, guard)}
        elif stat.S_ISDIR(st.st_mode):
            entries[name] = {"type": "dir"}
            for child in sorted(path.iterdir()):
                visit(child, child.name if name == "." else name + "/" + child.name)
        else:
            raise Refusal("SPECIAL_FILE")
    visit(root, ".")
    return entries


class CheckedReader:
    def __init__(self, reader, guard):
        self.reader, self.guard = reader, guard

    def read(self, size=-1):
        self.guard.remaining()
        return self.reader.read(min(size, BLOCK) if size >= 0 else BLOCK)


def pack(root, archive, entries, guard):
    # Lazy import: no third-party zstandard package or external compressor.
    from compression import zstd
    part = archive.with_suffix(archive.suffix + ".part")
    with tarfile.open(part, "w:zst", options={zstd.CompressionParameter.compression_level: 6}) as tar:
        for name in sorted(entries):
            guard.remaining()
            path = root if name == "." else root / name
            info = tar.gettarinfo(str(path), arcname=name)
            # gettarinfo otherwise emits hardlink aliases; store every file's bytes.
            if entries[name]["type"] == "file":
                if not regular(path):
                    raise Refusal("SOURCE_CHANGED")
                info.type, info.linkname = tarfile.REGTYPE, ""
                info.size = entries[name]["size"]
                with path.open("rb") as handle:
                    tar.addfile(info, CheckedReader(handle, guard))
            else:
                tar.addfile(info)
    os.replace(part, archive)
    verify_archive(archive, entries, guard)
    if manifest(root, guard) != entries:
        raise Refusal("SOURCE_CHANGED")


def verify_archive(archive, expected, guard):
    seen = {}
    with tarfile.open(archive, "r|zst") as tar:
        for info in tar:
            guard.remaining()
            name = member_name(info.name)
            if name in seen:
                raise Refusal("DUPLICATE_ARCHIVE_MEMBER")
            if info.isdir():
                entry = {"type": "dir"}
            elif info.issym():
                link_safe(name, info.linkname)
                entry = {"type": "link", "target": info.linkname}
            elif info.isfile():
                h = hashlib.sha256()
                handle = tar.extractfile(info)
                while True:
                    guard.remaining()
                    chunk = handle.read(BLOCK)
                    if not chunk:
                        break
                    h.update(chunk)
                entry = {"type": "file", "size": info.size, "sha256": h.hexdigest()}
            else:
                raise Refusal("SPECIAL_ARCHIVE_MEMBER")
            seen[name] = entry
    if seen != expected:
        raise Refusal("ARCHIVE_MANIFEST_MISMATCH")


def closed_outputs(config, guard):
    found = []
    for root in (config.campaign_root, config.work_root):
        if root.is_symlink() or not root.is_dir():
            raise Refusal("RECEIPT_ROOT_MISSING_OR_SYMLINK")
    for kit in sorted(config.campaign_root.iterdir()):
        guard.remaining()
        if kit.is_symlink() or not kit.is_dir():
            continue
        for path in sorted(kit.iterdir()):
            guard.remaining()
            if path.is_dir() and not path.is_symlink():
                receipt = path / "runner_receipt.json"
                if receipt.exists():
                    if not regular(receipt):
                        raise Refusal("NONREGULAR_RECEIPT")
                    if not re.fullmatch(r".+-\d{8}T\d{6}Z", path.name):
                        raise Refusal("UNRECOGNIZED_CAMPAIGN_NAME")
                    found.append(("campaign", path, receipt.stat().st_mtime_ns))
    for tree in sorted(config.work_root.iterdir()):
        guard.remaining()
        desk = tree / ".desk"
        if tree.is_symlink() or not tree.is_dir() or desk.is_symlink() or not desk.is_dir():
            continue
        for path in sorted(desk.iterdir()):
            guard.remaining()
            if path.name.startswith("r1-partc-") and path.is_dir() and not path.is_symlink():
                receipt = path / "runner_receipt.json"
                if receipt.exists():
                    if not regular(receipt):
                        raise Refusal("NONREGULAR_RECEIPT")
                    found.append(("partc", path, receipt.stat().st_mtime_ns))
    return found


def candidates(config, guard):
    found = closed_outputs(config, guard)
    newest = {kind: max(t for k, _, t in found if k == kind) for kind, _, _ in found}
    eligible = [r for r in found if r[2] < newest[r[0]]]
    names = [(k, p.name) for k, p, _ in found]
    if len(set(names)) != len(names):
        raise Refusal("CLOUD_NAME_COLLISION")
    if not config.catch_up:
        latest = {kind: max(t for k, _, t in eligible if k == kind) for kind, _, _ in eligible}
        eligible = [r for r in eligible if r[2] == latest[r[0]] or record_path(config, r[1]).exists()]
    return sorted(eligible, key=lambda r: (r[2], r[0], str(r[1])))


def record_path(config, source):
    return config.state_root / "records" / (hashlib.sha256(str(source).encode()).hexdigest() + ".json")


def air_marker(config, kind, source):
    plan = re.sub(r"-\d{8}T\d{6}Z$", "", source.name) if kind == "campaign" else source.name
    return any((config.marker_root / (plan + suffix)).is_file()
               and (config.marker_root / (plan + suffix)).stat().st_size > 0
               for suffix in (".air.ok", ".ok"))


def dataless(path, guard):
    # Native macOS file flags, never the sparse-file heuristic (unsafe for small receipts).
    result = guard.command(["stat", "-f", "%Sf", str(path)])
    if result.returncode != 0:
        raise Refusal("FILE_FLAGS_UNREADABLE")
    flags = result.stdout.decode("ascii", errors="replace").strip().split(",")
    return "dataless" in flags


def provider_evict(path, size, guard):
    result = guard.command(["brctl", "evict", str(path)])
    if result.returncode != 0:
        if b"NSFileProviderErrorDomain" in result.stderr + result.stdout and b"-2008" in result.stderr + result.stdout:
            return None
        raise Refusal("PROVIDER_EVICT_FAILED")
    if path.stat().st_size != size:
        raise Refusal("PROVIDER_SIZE_MISMATCH")
    if not dataless(path, guard):
        return None
    return {"provider": "iCloud Drive", "confirmation": "brctl evict rc=0; dataless; logical size read back",
            "logical_bytes": size, "confirmed_epoch_s": time.time()}


def install_cloud(local, target, expected_hash, guard):
    if target.exists():
        if file_hash(target, guard) != expected_hash:
            raise Refusal("CLOUD_HASH_MISMATCH")
        return
    part = target.with_name(target.name + ".part")
    with local.open("rb") as src, part.open("wb") as dst:
        while True:
            guard.remaining()
            chunk = src.read(BLOCK)
            if not chunk:
                break
            dst.write(chunk)
        dst.flush()
        os.fsync(dst.fileno())
    if file_hash(part, guard) != expected_hash:
        raise Refusal("CLOUD_HASH_MISMATCH")
    os.replace(part, target)
    if file_hash(target, guard) != expected_hash:
        raise Refusal("CLOUD_HASH_MISMATCH")


def remove_original(source, guard):
    # Some runner outputs are read-only. Do not follow links while adding owner write.
    for root, dirs, _ in os.walk(source, followlinks=False):
        guard.remaining()
        path = Path(root)
        os.chmod(path, path.stat().st_mode | stat.S_IWUSR | stat.S_IXUSR)
    guard.quiet()
    if source.exists():
        shutil.rmtree(source)


def offload(config, kind, source, guard):
    safe_name(source.name)
    record_file = record_path(config, source)
    copied = air_marker(config, kind, source)
    if not copied and not config.cloud_only_allowed and not record_file.exists():
        return "AIR_COPY_REQUIRED"
    cloud = config.cloud_root / kind
    cloud.mkdir(parents=True, exist_ok=True, mode=0o700)
    archive = cloud / (source.name + ".tar.zst")
    cloud_receipt = cloud / (source.name + ".receipt.json")
    stage = config.state_root / "stage" / record_file.stem
    stage.mkdir(parents=True, exist_ok=True, mode=0o700)
    local_archive, local_receipt = stage / "span.tar.zst", stage / "receipt.json"
    if record_file.exists():
        record = json.loads(record_file.read_bytes())
        if (record["schema"], record["source"], record["kind"], record["archive"]) != (
                SCHEMA, str(source), kind, str(archive)):
            raise Refusal("RECORD_IDENTITY_MISMATCH")
        receipt = json.loads(local_receipt.read_bytes())
        if digest(receipt) != record["receipt_sha256"] or digest(receipt["manifest"]) != receipt["manifest_sha256"]:
            raise Refusal("RECEIPT_HASH_MISMATCH")
    else:
        if archive.exists() or cloud_receipt.exists():
            raise Refusal("UNOWNED_CLOUD_ARCHIVE")
        guard.quiet()
        entries = manifest(source, guard)
        pack(source, local_archive, entries, guard)
        receipt = {"schema": SCHEMA, "source": str(source), "kind": kind, "name": source.name,
                   "manifest": entries, "manifest_sha256": digest(entries),
                   "archive_sha256": file_hash(local_archive, guard), "archive_bytes": local_archive.stat().st_size,
                   "format": "tar.zst", "application_encryption": False}
        atomic_json(local_receipt, receipt)
        record = {"schema": SCHEMA, "source": str(source), "kind": kind, "archive": str(archive),
                  "manifest_sha256": receipt["manifest_sha256"], "archive_sha256": receipt["archive_sha256"],
                  "archive_bytes": receipt["archive_bytes"], "receipt_sha256": digest(receipt),
                  "cloud_only_allowed": config.cloud_only_allowed, "prior_copy_marker_observed": copied,
                  "copy_basis": "prior-copy-marker-and-cloud" if copied else "cloud-only", "state": "PACKED", "provider": {}}
        atomic_json(record_file, record)
    if record["state"] == "COMPLETE":
        if source.exists():
            raise Refusal("COMPLETED_SOURCE_REAPPEARED")
        return "COMPLETE"
    guard.quiet()
    if record["state"] not in ("DELETING", "EVICTED"):
        if "archive" not in record["provider"]:
            install_cloud(local_archive, archive, receipt["archive_sha256"], guard)
            verify_archive(archive, receipt["manifest"], guard)
        if "receipt" not in record["provider"]:
            install_cloud(local_receipt, cloud_receipt, record["receipt_sha256"], guard)
        local_archive.unlink(missing_ok=True)
        record["state"] = "UPLOAD_PENDING"
        atomic_json(record_file, record)
        try:
            while len(record["provider"]) < 2:
                guard.quiet()
                for label, path, size in (("archive", archive, receipt["archive_bytes"]),
                                          ("receipt", cloud_receipt, local_receipt.stat().st_size)):
                    if label not in record["provider"]:
                        evidence = provider_evict(path, size, guard)
                        if evidence:
                            record["provider"][label] = evidence
                            atomic_json(record_file, record)
                if len(record["provider"]) < 2:
                    time.sleep(min(config.poll_seconds, guard.remaining()))
        except OutOfTime:
            raise Pending("UPLOAD_PENDING") from None
        record["state"] = "EVICTED"
        atomic_json(record_file, record)
    for label, path, size in (("archive", archive, receipt["archive_bytes"]),
                              ("receipt", cloud_receipt, local_receipt.stat().st_size)):
        if not record["provider"].get(label) or path.stat().st_size != size or not dataless(path, guard):
            raise Refusal("PROVIDER_CONFIRMATION_LOST")
    guard.quiet()
    if record["state"] != "DELETING":
        if manifest(source, guard) != receipt["manifest"]:
            raise Refusal("SOURCE_CHANGED")
        record["state"] = "DELETING"
        atomic_json(record_file, record)
    # After an interrupted deletion, remaining entries must still be a subset
    # of the verified manifest. Never sweep up new files added during downtime.
    if source.exists():
        remaining = manifest(source, guard)
        if any(receipt["manifest"].get(name) != entry for name, entry in remaining.items()):
            raise Refusal("SOURCE_CHANGED_DURING_DELETE")
    remove_original(source, guard)
    record["state"], record["completed_epoch_s"] = "COMPLETE", time.time()
    atomic_json(record_file, record)
    return "COMPLETE"


def air_pull(config, guard):
    parts = config.air_pull.split("/")
    if len(parts) != 2 or parts[0] not in ("campaign", "partc"):
        raise Refusal("AIR_PULL_EXPECTS_KIND_NAME")
    kind, name = parts[0], safe_name(parts[1])
    if not config.receipt_sha256 or not re.fullmatch(r"[0-9a-f]{64}", config.receipt_sha256):
        raise Refusal("AIR_PULL_REQUIRES_MARKER_RECEIPT_SHA256")
    cloud_receipt = config.cloud_root / kind / (name + ".receipt.json")
    archive = config.cloud_root / kind / (name + ".tar.zst")
    for path in (cloud_receipt, archive):
        if guard.command(["brctl", "download", str(path)]).returncode:
            raise Refusal("CLOUD_DOWNLOAD_FAILED")
    # Reads hydrate synchronously, under the CLI's hard deadline supervisor.
    receipt = json.loads(cloud_receipt.read_bytes())
    if (receipt["schema"], receipt["kind"], receipt["name"]) != (SCHEMA, kind, name):
        raise Refusal("RECEIPT_IDENTITY_MISMATCH")
    if (not config.receipt_sha256 or not re.fullmatch(r"[0-9a-f]{64}", config.receipt_sha256)
            or file_hash(cloud_receipt, guard) != config.receipt_sha256
            or digest(receipt["manifest"]) != receipt["manifest_sha256"]):
        raise Refusal("RECEIPT_HASH_MISMATCH")
    if archive.stat().st_size != receipt["archive_bytes"] or file_hash(archive, guard) != receipt["archive_sha256"]:
        raise Refusal("CLOUD_HASH_MISMATCH")
    verify_archive(archive, receipt["manifest"], guard)
    destination = config.air_root / kind / name
    temporary = destination.with_name(name + ".pull-part")
    if destination.exists():
        if manifest(destination, guard) != receipt["manifest"]:
            raise Refusal("AIR_DESTINATION_MISMATCH")
    else:
        if temporary.exists():
            shutil.rmtree(temporary)
        temporary.mkdir(parents=True, mode=0o700)
        with tarfile.open(archive, "r|zst") as tar:
            # Built-in data filter also refuses writes through symlink parents.
            tar.extractall(temporary, filter="data")
        if manifest(temporary, guard) != receipt["manifest"]:
            raise Refusal("AIR_EXTRACT_MISMATCH")
        os.replace(temporary, destination)
    # A pull leaves bytes only on the external SSD, and releases the Air's cloud cache.
    for path, size in ((archive, receipt["archive_bytes"]), (cloud_receipt, cloud_receipt.stat().st_size)):
        while not provider_evict(path, size, guard):
            time.sleep(min(config.poll_seconds, guard.remaining()))
    return {"status": "AIR_VERIFIED", "holds_next_arm": False, "manifest_sha256": receipt["manifest_sha256"]}


@contextlib.contextmanager
def close_lock(config, guard):
    guard.quiet()
    config.fence.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = config.fence.parent / ".desk-fence.lock"
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise HostBusy("DESK_LOCK_BUSY") from None
        guard.quiet()
        yield
    finally:
        os.close(fd)


def run(config):
    guard = Guard(config)
    completed = skipped = 0
    try:
        with close_lock(config, guard):
            # Refuse destinations within the public checkout or measured roots.
            repo = Path(__file__).resolve().parents[1]
            for destination in (config.cloud_root, config.state_root, config.marker_root, config.air_root):
                for forbidden in (repo, config.campaign_root, config.work_root):
                    if destination.resolve().is_relative_to(forbidden.resolve()):
                        raise Refusal("DESTINATION_OVERLAPS_REPO_OR_SOURCE")
            if config.air_pull:
                return OK, air_pull(config, guard)
            selected = candidates(config, guard)
            found = closed_outputs(config, guard)
            protected = {str(p) for kind, p, stamp in found
                         if stamp == max(t for k, _, t in found if k == kind)}
            # A hard deadline can interrupt rmtree after the source receipt is removed.
            # DELETING is durable only after the complete tree and cloud were verified.
            records = config.state_root / "records"
            selected_sources = {str(p) for _, p, _ in selected}
            if records.is_dir():
                for path in sorted(records.iterdir()):
                    if path.suffix != ".json":
                        continue
                    record = json.loads(path.read_bytes())
                    if (record.get("state") == "DELETING" and record["source"] not in selected_sources
                            and record["source"] not in protected):
                        source = Path(record["source"])
                        kind = record["kind"]
                        rel = source.relative_to(config.campaign_root if kind == "campaign" else config.work_root)
                        valid = (kind == "campaign" and len(rel.parts) == 2 or kind == "partc"
                                 and len(rel.parts) == 3 and rel.parts[1] == ".desk"
                                 and rel.parts[2].startswith("r1-partc-"))
                        if not valid or path != record_path(config, source):
                            raise Refusal("RECORD_IDENTITY_MISMATCH")
                        selected.append((kind, source, 0))
            for kind, source, _ in selected:
                guard.quiet()
                status = offload(config, kind, source, guard)
                completed += status == "COMPLETE"
                skipped += status == "AIR_COPY_REQUIRED"
        result = {"status": "AIR_COPY_REQUIRED" if skipped else "COMPLETE", "completed": completed,
                  "skipped": skipped, "holds_next_arm": bool(skipped)}
        return (VERIFY_FAILED if skipped else OK), result
    except Exception as exc:
        # zstd has its own exception type on 3.14; unexpected metadata shapes
        # also fail closed without emitting decoder or measurement bytes.
        code = exc.code if isinstance(exc, Refusal) else VERIFY_FAILED
        # Never echo exception text from a decoder, archive, or subprocess.
        return code, {"status": str(exc) if isinstance(exc, Refusal) else "IO_OR_METADATA_FAILURE",
                      "completed": completed, "holds_next_arm": code != UPLOAD_PENDING}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--deadline", type=float, required=True, help="hard UTC epoch seconds; never a duration")
    for name in ("campaign-root", "work-root", "cloud-root", "state-root", "marker-root", "fence", "air-root"):
        p.add_argument("--" + name, type=Path)
    p.add_argument("--catch-up", action="store_true", help="all older closed outputs; newest of each kind still kept")
    p.add_argument("--cloud-only-allowed", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--poll-seconds", type=float, default=5)
    p.add_argument("--air-pull", metavar="KIND/NAME")
    p.add_argument("--receipt-sha256", help="independent receipt_sha256 from the MBP offload record; required for Air pull")
    p.add_argument("--_worker", action="store_true", help=argparse.SUPPRESS)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    if not math.isfinite(args.deadline) or not math.isfinite(args.poll_seconds) or args.poll_seconds <= 0:
        parser().error("deadline must be finite and poll-seconds positive and finite")
    if args._worker:
        kwargs = {k: v for k, v in vars(args).items() if k != "_worker" and v is not None}
        os.umask(0o077)
        code, result = run(Config(**kwargs))
        print(json.dumps(result, sort_keys=True), flush=True)
        return code
    # A separate process group bounds blocking filesystem I/O and tarfile, too.
    # No child or brctl may survive into the next soak.
    left = args.deadline - time.time()
    if left <= 0:
        print('{"status":"DEADLINE","holds_next_arm":true}')
        return DEADLINE
    script = Path(__file__).resolve().parents[1] / "scripts/close_offload.py"
    worker = subprocess.Popen([sys.executable, "-B", str(script), *(sys.argv[1:] if argv is None else argv), "--_worker"],
                              start_new_session=True)
    try:
        return worker.wait(timeout=left)
    except (subprocess.TimeoutExpired, KeyboardInterrupt):
        print('{"status":"DEADLINE","holds_next_arm":true}', flush=True)
        return DEADLINE
    finally:
        # subprocess.run kills only its direct child on timeout. The worker
        # can exit normally with UPLOAD_PENDING while a provider grandchild
        # still lives. Always clear the group, including successful exits.
        try:
            os.killpg(worker.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        worker.wait()
