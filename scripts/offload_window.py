#!/usr/bin/env python3
"""Offload one closed measurement-window record from the MBP to the Air's external SSD.

Design: docs/ops/AIR-OFFLOAD.md (the merged Opus+Sol build; the comparison is
docs/ops/AIR-OFFLOAD-AGREEMENT.md). Standard library only (Python >= 3.11).

MBP side (runs right after finalize, commit and push, at the START of cool-down):
  run         [adopt the harvest-off pack | pack] -> push -> Air verify -> release older windows, inside a
              monotonic deadline. One pack per window: a finalized_manifest.v2 record is packed once by the
              harvest-off lane (--harvest-pack); --pack is the fallback for R1 and legacy manifests only
  release     delete the MBP copy only after a FRESH Air receipt (the Air re-hashes the
              compressed parts against the MBP's nonce) AND a sealed second-copy receipt
  triage      evidence for the pre-arm `quiet_start_state` entry
Air side:
  init-store  bind the landing store to one APFS volume (by volume UUID); run once
  air-gate    the SSH forced command; the only thing the MBP's key can run
  air-icloud  second-copy worker: iCloud Drive, server-confirmed by an evict/re-download round trip
  air-second-disk  alternative second copy on a physically independent, bound disk

Preconditions on the record (fail closed): the record's own manifest, authenticated by the
sha256 pinned in the committed record, lists the WHOLE closed envelope (no unlisted file,
no hard link, no `.git` or `restricted` member, no unlisted symlink); the terminal evidence
(result.json verdict and ended_epoch_s, chain.started/chain.exited, no chain.unkilled,
courier.sent) is present and listed. The MBP does not re-hash raw files by default: the Air
checks every raw file against the manifest digests, end to end.

Interlock: the magistrate's cool-down lease and shared loop lock (`--lease`, `--watchdog-state`,
`--loop-lock`) are used when the magistrate passes them; the LaunchAgent/ps probe always runs
as well (today it is the only active exclusion).

Exit codes: 0 ok, 2 refused, 3 integrity mismatch (fail closed), 4 deadline (resumable),
5 transport or Air store unavailable (resumable), 6 local I/O error.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import plistlib
import re
import secrets
import shlex
import shutil
import signal
import socket
import stat
import subprocess
import sys
import tarfile
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PLAN = "joulewise.ops.offload_plan.v2"
SCHEMA_MANIFEST = "joulewise.ops.offload_manifest.v2"
SCHEMA_AIR = "joulewise.ops.offload_air_receipt.v2"
SCHEMA_SECOND = "joulewise.ops.offload_second_copy.v2"
SCHEMA_FRESH = "joulewise.ops.offload_fresh_receipt.v1"
SCHEMA_SPAN = "joulewise.ops.offload_span.v1"
SCHEMA_TRIAGE = "joulewise.ops.offload_triage.v1"
SCHEMA_DELETING = "joulewise.ops.offload_deletion_journal.v1"
SCHEMA_BINDING = "joulewise.ops.offload_store_binding.v1"
SCHEMA_MARKER = "joulewise.ops.offload_store_marker.v1"
SCHEMA_LEASE = "joulewise.air_offload_gate.v1"  # magistrate-owned cool-down lease (Sol build)
# Record manifests accepted (agreement item 8, plus the harvest-off lane's finalize manifest).
SCHEMA_FINALIZED_V2 = "joulewise.align_v4.finalized_manifest.v2"
SCHEMA_R1 = "joulewise.align.r1_harvest_manifest.v1"
SCHEMA_SSD = "joulewise.ssd_closed_record.v1"
SCHEMA_CLOSED = "joulewise.closed_record.v1"
SCHEMA_HARVEST = "joulewise.harvest_window.v1"
GATE_VERSION = 2
WINDOW_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
PART_NAME = re.compile(r"(?:part-\d{4}\.tar\.(?:zst|gz)|payload\.tar\.zst)\Z")
# The harvest-off lane's canonical pack of a v4 session root (joulewise/align/apple/harvest_offload.py on
# origin/align/2026-11-08-harvest-off-fix): <dir>/payload.tar.zst + <dir>/MANIFEST.json. Kept under the same
# names on the Air, so the harvest restore (`unpack --offload <store>/inbox/<K>`) reads the verified copy.
SCHEMA_HARVEST_PACK = "joulewise.align_v4.harvest_offload.v1"
HARVEST_PAYLOAD, HARVEST_MANIFEST = "payload.tar.zst", "MANIFEST.json"
HARVEST_EXTERNAL = re.compile(r"\.external/\d{4}\Z")
EXTRA_NAMES = frozenset({HARVEST_MANIFEST})
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
NONCE = re.compile(r"[0-9a-f]{32}\Z")
HOST = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.@:-]*\Z")
MANIFEST_NAME = "offload-manifest.json"
RECORD_MANIFEST_NAME = "record-manifest.bin"
AIR_RECEIPT = "air-receipt.json"
SECOND_RECEIPT = "second-copy-receipt.json"
MARKER_NAME = ".jw-offload-store.json"
SEALED_COMPONENTS = frozenset({".git", "restricted"})
TERMINAL_VERDICTS = frozenset({"GO", "ABORTED", "COLLECTED", "CHAIN_STOPPED", "REFUSED"})
NO_TERMINAL_PREFIXES = ("smoke-", "bench-")  # only synthetic windows may skip the terminal check
SECOND_METHODS = ("icloud_evict_download_roundtrip", "second_disk_verified_copy")
DEFAULT_STORE_ROOT = Path("/Volumes/JW-EXT/jw-offload")
DEFAULT_BINDING = Path("/usr/local/etc/jw-offload/store-binding.json")
RATES_SEED = ROOT / "configs/ops/air_offload_rates.json"
CHUNK = 1 << 20
DATALESS = 0x40000000  # SF_DATALESS: iCloud placeholder without local bytes
# LaunchAgents whose presence means a window is armed (the magistrate's watchdog is not).
ARMED_PREFIXES = ("com.joulewise.night", "com.joulewise.align-", "com.joulewise.b6")
MEASURING = re.compile(r"(^|[\s/])(powermetrics|run_night\.py|align_v4_session\.py|align_r1_rehearsal\.py|"
                       r"align_r0_checks\.py|run_campaign\.py|mlx_lm)(\s|$|\.)")
DEFAULT_RATES = {"pack_raw_mb_s": 250.0, "push_mb_s": 40.0, "verify_raw_mb_s": 150.0, "ratio": 8.0,
                 "recheck_mb_s": 250.0, "release_hash_mb_s": 250.0}


class Refusal(Exception):
    """A precondition failed; nothing unsafe was done."""
    code = 2


class Mismatch(Refusal):
    """Integrity failure: fail closed, delete nothing."""
    code = 3


class DeadlineStop(Refusal):
    """The dwell deadline would be or was reached; state is resumable."""
    code = 4


class Interrupted(DeadlineStop):
    """SIGTERM: unwind, keep state, resumable."""


class TransportError(Refusal):
    code = 5


def require(ok, reason, kind=Refusal):
    if not ok:
        raise kind(reason)


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sealed(body: dict) -> dict:
    """A receipt carries the sha256 of its own canonical body."""
    return {**body, "receipt_sha256": sha_bytes(canonical(body))}


def check_sealed(receipt) -> dict:
    require(isinstance(receipt, dict) and HEX64.match(str(receipt.get("receipt_sha256", ""))),
            "receipt_malformed", Mismatch)
    body = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    require(sha_bytes(canonical(body)) == receipt["receipt_sha256"], "receipt_hash_mismatch", Mismatch)
    return body


def valid_window(window_id: str) -> str:
    require(isinstance(window_id, str) and WINDOW_ID.match(window_id) is not None, "bad_window_id")
    return window_id


def safe_relpath(path) -> str:
    require(isinstance(path, str) and path and not path.startswith("/")
            and not any(c in path for c in "\\\x00\n\r"), f"unsafe_path:{path!r}", Mismatch)
    parts = path.split("/")
    require(all(p not in ("", ".", "..") for p in parts), f"unsafe_path:{path!r}", Mismatch)
    require(not SEALED_COMPONENTS.intersection(parts), f"envelope_sealed_member:{path}")
    return path


def plain_path(path) -> Path:
    """Absolute path whose existing components are not symlinks (checked lexically, never resolved)."""
    path = Path(os.path.abspath(path))
    for item in (*reversed(path.parents), path):
        try:
            info = os.lstat(item)
        except FileNotFoundError:
            continue
        require(not stat.S_ISLNK(info.st_mode), f"symlink_path:{item}", Mismatch)
    return path


def _no_duplicate_keys(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate_json_key:{key}", Mismatch)
        out[key] = value
    return out


# -- no-follow file access ------------------------------------------------------------

def parent_fd(root: Path, rel: str, make_dirs=False) -> tuple[int, str]:
    """(fd of rel's parent directory, leaf name), walked without following ANY symlink."""
    rel = safe_relpath(rel)
    require(not os.path.islink(root), f"symlink_root:{root}", Mismatch)
    dirfd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    parts = rel.split("/")
    try:
        for part in parts[:-1]:
            try:
                nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dirfd)
            except FileNotFoundError:
                if not make_dirs:
                    raise
                os.mkdir(part, 0o755, dir_fd=dirfd)
                nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dirfd)
            except OSError as exc:  # ELOOP/ENOTDIR: a symlinked or non-directory component
                raise Mismatch(f"symlink_or_nondir_component:{rel}") from exc
            os.close(dirfd)
            dirfd = nxt
    except BaseException:
        os.close(dirfd)
        raise
    return dirfd, parts[-1]


def open_nofollow(root: Path, rel: str, flags=os.O_RDONLY, mode=0o644, make_dirs=False) -> int:
    """Open root/rel without following a symlink at ANY component (root included)."""
    dirfd, leaf = parent_fd(root, rel, make_dirs)
    try:
        return os.open(leaf, flags | os.O_NOFOLLOW, mode, dir_fd=dirfd)
    except (FileNotFoundError, FileExistsError):
        raise
    except OSError as exc:
        raise Mismatch(f"symlink_or_unreadable:{rel}") from exc
    finally:
        os.close(dirfd)


def lstat_rel(root: Path, rel: str) -> os.stat_result:
    dirfd, leaf = parent_fd(root, rel)
    try:
        return os.stat(leaf, dir_fd=dirfd, follow_symlinks=False)
    finally:
        os.close(dirfd)


def readlink_rel(root: Path, rel: str) -> str:
    dirfd, leaf = parent_fd(root, rel)
    try:
        return os.readlink(leaf, dir_fd=dirfd)
    finally:
        os.close(dirfd)


def hash_file(path: Path, nocache=False) -> tuple[str, int]:
    digest, size = hashlib.sha256(), 0
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    if nocache and hasattr(fcntl, "F_NOCACHE"):
        with contextlib.suppress(OSError):
            fcntl.fcntl(fd, fcntl.F_NOCACHE, 1)
    with os.fdopen(fd, "rb") as stream:
        for chunk in iter(lambda: stream.read(4 * CHUNK), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_atomic(path: Path, raw: bytes) -> None:
    require(not os.path.islink(path), f"symlink_target:{path}", Mismatch)
    tmp = path.with_name(path.name + ".tmp")
    with contextlib.suppress(FileNotFoundError):
        os.unlink(tmp)
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)
    fsync_dir(path.parent)


def write_once(path: Path, raw: bytes, conflict: str) -> None:
    """Idempotent seal: identical bytes are fine, different bytes are a conflict."""
    if os.path.lexists(path):
        require(not os.path.islink(path), f"symlink_target:{path}", Mismatch)
        require(path.read_bytes() == raw, conflict, Mismatch)
        return
    write_atomic(path, raw)


def append_jsonl(path: Path, row: dict) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "ab") as stream:
        stream.write(canonical(row))
        stream.flush()
        os.fsync(stream.fileno())


def read_json(path: Path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        return json.loads(stream.read())


def free_bytes(path: Path) -> int:
    value = os.statvfs(path)
    return value.f_bavail * value.f_frsize


def make_dir(path: Path, mode=0o755) -> Path:
    require(not os.path.islink(path), f"symlink_dir:{path}", Mismatch)
    path.mkdir(mode=mode, exist_ok=True)
    return path


# -- processes, deadline backstop -------------------------------------------------------

def run_process_group(argv, *, stdin=None, timeout=None, env=None) -> tuple[int, bytes, bytes]:
    """Run argv in its own process group; on any exit path (timeout, alarm, SIGTERM) kill the
    whole group, so an ssh grandchild cannot outlive the deadline. No shell."""
    proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL if stdin is None else stdin,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True, env=env)
    try:
        out, err = proc.communicate(timeout=timeout)
        return proc.returncode, out, err
    finally:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(proc.pid, signal.SIGKILL)
        if proc.returncode is None:
            with contextlib.suppress(Exception):
                proc.communicate(timeout=10)
            if proc.returncode is None:
                proc.wait()


@contextlib.contextmanager
def alarm_guard(seconds):
    """SIGALRM backstop at the deadline for blocking Python I/O; SIGTERM unwinds the same way."""
    if seconds is None or threading.current_thread() is not threading.main_thread():
        yield
        return
    require(signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0), "existing_process_timer")

    def expired(signum, frame):
        raise DeadlineStop("deadline_alarm")

    def terminated(signum, frame):
        raise Interrupted("interrupted_sigterm")
    old_alarm = signal.signal(signal.SIGALRM, expired)
    old_term = signal.signal(signal.SIGTERM, terminated)
    signal.setitimer(signal.ITIMER_REAL, max(float(seconds), 0.001))
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_alarm)
        signal.signal(signal.SIGTERM, old_term)


# -- codecs ---------------------------------------------------------------------------

def zstd_cli():
    return shutil.which("zstd") or next((p for p in ("/opt/homebrew/bin/zstd", "/usr/local/bin/zstd")
                                         if os.access(p, os.X_OK)), None)


def stdlib_zstd():
    try:
        import compression.zstd as module  # Python >= 3.14
        return module
    except ImportError:
        return None


def choose_codec(preference: str, level: int, threads: int) -> dict:
    """zstd CLI, else stdlib zstd (same format), else stdlib gzip."""
    require(1 <= level <= 19 and 1 <= threads <= 64, "bad_level_or_threads")
    if preference in ("auto", "zstd-cli") and zstd_cli():
        version = subprocess.run([zstd_cli(), "--version"], capture_output=True, text=True).stdout.strip()
        return {"name": "zstd", "impl": "zstd-cli", "version": version, "level": level, "threads": threads}
    if preference in ("auto", "zstd-stdlib") and stdlib_zstd():
        return {"name": "zstd", "impl": "zstd-stdlib", "version": str(stdlib_zstd().zstd_version_info),
                "level": level, "threads": threads}
    if preference in ("auto", "gzip"):
        return {"name": "gzip", "impl": "gzip-stdlib", "version": sys.version.split()[0],
                "level": min(level, 9), "threads": 1}
    raise Refusal(f"codec_unavailable:{preference}")


class CompressedWriter:
    """A writable stream that compresses into `out` with the chosen codec."""

    def __init__(self, codec: dict, out: Path):
        self.codec, self.out, self.proc, self.stream = codec, out, None, None
        if codec["impl"] == "zstd-cli":
            self.proc = subprocess.Popen([zstd_cli(), f"-{codec['level']}", f"-T{codec['threads']}", "-q",
                                          "--no-progress", "-", "-o", str(out)],
                                         stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                         stderr=subprocess.PIPE, start_new_session=True)
            self.stream = self.proc.stdin
        elif codec["impl"] == "zstd-stdlib":
            module = stdlib_zstd()
            options = {module.CompressionParameter.compression_level: codec["level"]}
            if codec["threads"] > 1:
                options[module.CompressionParameter.nb_workers] = codec["threads"]
            self.stream = module.ZstdFile(out, "wb", options=options)
        else:
            import gzip
            self.stream = gzip.GzipFile(filename=str(out), mode="wb", compresslevel=codec["level"], mtime=0)

    def write(self, data):
        return self.stream.write(data)

    def close(self):
        self.stream.close()
        if self.proc is not None:
            err = self.proc.stderr.read()
            self.proc.stderr.close()
            require(self.proc.wait() == 0, f"compressor_failed:{err[:200]!r}", Mismatch)

    def abort(self):
        if self.proc is not None:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(self.proc.pid, signal.SIGKILL)
            self.proc.wait()
            for pipe in (self.proc.stdin, self.proc.stderr):
                with contextlib.suppress(OSError):
                    pipe.close()
        else:
            with contextlib.suppress(Exception):
                self.stream.close()


@contextlib.contextmanager
def decompressed(codec: dict, path: Path):
    """Yield a readable stream of the decompressed part; a codec failure is a Mismatch."""
    if codec["name"] == "zstd" and zstd_cli():
        proc = subprocess.Popen([zstd_cli(), "-d", "-q", "-c", str(path)], stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
        try:
            yield proc.stdout
            proc.stdout.read()  # drain trailing bytes so the exit status is final
            require(proc.wait() == 0, f"decompress_failed:{path.name}", Mismatch)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
            proc.stdout.close()
    elif codec["name"] == "zstd":
        require(stdlib_zstd() is not None, "zstd_unavailable_on_reader", Mismatch)
        with stdlib_zstd().open(path, "rb") as stream:
            yield stream
    elif codec["name"] == "gzip":
        import gzip
        with gzip.open(path, "rb") as stream:
            yield stream
    else:
        raise Mismatch(f"unknown_codec:{codec.get('name')}")


# -- the record's own manifest and its closed envelope -------------------------------------

def read_record_manifest(path, expected_sha256: str) -> bytes:
    """The record manifest's bytes, authenticated by the sha256 pinned in the committed record."""
    require(isinstance(expected_sha256, str) and HEX64.match(expected_sha256) is not None,
            "record_manifest_sha256_required")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        raw = stream.read()
    require(sha_bytes(raw) == expected_sha256, "record_manifest_sha256_mismatch", Mismatch)
    return raw


class Envelope:
    """What the record's own manifest says the closed record is: files (sha256, size or None),
    literal symlinks (finalized_manifest.v2 only) and directories (v2 lists every one)."""

    def __init__(self, fmt: str):
        self.fmt = fmt
        self.files: dict[str, dict] = {}
        self.links: dict[str, str] = {}
        self.dirs: set[str] = set()
        self.strict_dirs = False
        self.closure_external = 0  # v2: external inputs bound by the manifest, never moved here
        self.closure_inputs: dict[str, dict] = {}  # v2: declared absolute inputs -> {sha256, size}
        self.doc = None

    def add_file(self, rel, digest, size=None):
        rel = safe_relpath(rel)
        require(isinstance(digest, str) and HEX64.match(digest) is not None, f"bad_digest:{rel}", Mismatch)
        require(size is None or (type(size) is int and size >= 0), f"bad_size:{rel}", Mismatch)
        require(rel not in self.files and rel not in self.links and rel not in self.dirs,
                f"duplicate_manifest_path:{rel}", Mismatch)
        self.files[rel] = {"sha256": digest, "size": size}


def parse_record_manifest(raw: bytes, record_root: Path, manifest_path: Path | None = None) -> Envelope:
    """Envelope from a supported record manifest; digests are never recomputed here."""
    record_root = Path(os.path.abspath(record_root))
    text = raw.decode("utf-8")
    if not text.lstrip().startswith("{"):  # sha256sum / SHA256SUMS: "<hex>  <path>" ('*' binary marker)
        env = Envelope("sha256sums")
        for line in text.splitlines():
            if not line.strip():
                continue
            match = re.fullmatch(r"([0-9a-f]{64}) [ *](.+)", line)
            require(match is not None, "record_manifest_line_malformed", Mismatch)
            env.add_file(match.group(2), match.group(1))
    else:
        doc = json.loads(text, object_pairs_hook=_no_duplicate_keys)
        require(isinstance(doc, dict), "record_manifest_unsupported")
        schema = doc.get("schema")
        if schema == SCHEMA_FINALIZED_V2:  # joulewise/align/apple/harvest_offload.py finalized_manifest()
            env = Envelope("finalized_manifest.v2")
            require(set(doc) == {"schema", "source_root", "entries", "closure"}
                    and isinstance(doc["entries"], dict) and isinstance(doc["closure"], dict)
                    and isinstance(doc["source_root"], str), "finalized_manifest_malformed", Mismatch)
            require(os.path.abspath(doc["source_root"]) == str(record_root), "record_root_differs_from_manifest_root")
            env.strict_dirs = True
            for rel, row in sorted(doc["entries"].items()):
                if isinstance(row, dict) and set(row) == {"sha256", "size"}:
                    env.add_file(rel, row["sha256"], row["size"])
                elif isinstance(row, dict) and set(row) == {"link"} and isinstance(row["link"], str) and row["link"]:
                    rel = safe_relpath(rel)
                    require(rel not in env.files and rel not in env.dirs, f"duplicate_manifest_path:{rel}", Mismatch)
                    env.links[rel] = row["link"]
                elif row == {"directory": True}:
                    env.dirs.add(safe_relpath(rel))
                else:
                    raise Mismatch(f"finalized_manifest_bad_entry:{rel}")
            closure = doc["closure"]
            env.closure_external = sum(len(closure.get(k) or {}) for k in ("files", "ignored"))
            bound = closure.get("files") or {}
            for name in closure.get("inputs") or {}:
                row = bound.get(name)
                if isinstance(row, dict) and isinstance(row.get("sha256"), str) and type(row.get("size")) is int:
                    env.closure_inputs[name] = {"sha256": row["sha256"], "size": row["size"]}
            env.doc = doc
        elif schema == SCHEMA_R1:  # joulewise/align/apple/r1_runtime.py k_harvest
            env = Envelope("r1_harvest_manifest.v1")
            require(os.path.abspath(str(doc.get("root", ""))) == str(record_root),
                    "record_root_differs_from_manifest_root")
            require(isinstance(doc.get("files"), dict), "record_manifest_unsupported")
            for rel, digest in doc["files"].items():
                env.add_file(rel, digest)
        elif schema == SCHEMA_SSD:  # origin/align/2026-11-08-ssd-hooks scripts/ssd_permanent.py
            env = Envelope("ssd_closed_record.v1")
            require(doc.get("state") == "closed" and isinstance(doc.get("window_id"), str)
                    and isinstance(doc.get("files"), dict) and doc["files"], "ssd_closed_record_not_closed")
            for rel, digest in doc["files"].items():
                env.add_file(rel, digest)
        elif schema == SCHEMA_CLOSED:
            env = Envelope("closed_record.v1")
            require(doc.get("closed") is True and isinstance(doc.get("files"), dict), "closed_record_not_closed")
            for rel, row in doc["files"].items():
                require(isinstance(row, dict), f"bad_row:{rel}", Mismatch)
                env.add_file(rel, row.get("sha256"), row.get("size"))
        elif schema == SCHEMA_HARVEST:  # scripts/harvest_window.py; absolute custody_root never opened
            env = Envelope("harvest_window.v1")
            inventory = doc.get("inventory")
            require(isinstance(inventory, dict) and inventory, "harvest_lacks_inventory")
            for prefix, members in inventory.items():
                safe_relpath(prefix)
                require(isinstance(members, dict), "harvest_inventory_malformed", Mismatch)
                for member, row in members.items():
                    require(isinstance(row, dict) and type(row.get("mode")) is int, "harvest_inventory_row", Mismatch)
                    require(stat.S_ISDIR(row["mode"]) or stat.S_ISREG(row["mode"]), "harvest_inventory_link_or_device")
                    if stat.S_ISREG(row["mode"]):
                        env.add_file(f"{prefix}/{safe_relpath(member)}", row.get("sha256"), row.get("size"))
            extra = doc.get("r9_window")  # Revision 6 adds this file after the source inventory
            if extra is not None:
                require(isinstance(extra, dict), "harvest_r9_reference", Mismatch)
                key = safe_relpath("custody-root/" + str(extra.get("path", "")))
                if key in env.files:
                    require(env.files[key]["sha256"] == extra.get("sha256"), "harvest_r9_collision", Mismatch)
                else:
                    env.add_file(key, extra.get("sha256"))
        else:
            raise Refusal(f"record_manifest_unsupported:{schema}")
    require(env.files, "record_manifest_empty")
    if manifest_path is not None:  # a manifest inside the record travels with it, under its pinned digest
        with contextlib.suppress(ValueError):
            rel = Path(os.path.abspath(manifest_path)).relative_to(record_root).as_posix()
            require(rel not in env.files and rel not in env.links, "manifest_digests_itself", Mismatch)
            env.add_file(rel, sha_bytes(raw), len(raw))
    return env


def scan_tree(root: Path) -> dict[str, tuple[str, object]]:
    """Every entry under root, never following a link and never entering a sealed member."""
    out: dict[str, tuple[str, object]] = {}

    def walk(dirfd, prefix):
        with os.scandir(dirfd) as entries:
            names = sorted(entry.name for entry in entries)
        for name in names:
            rel = prefix + name
            require(name not in SEALED_COMPONENTS, f"envelope_sealed_member:{rel}")
            info = os.stat(name, dir_fd=dirfd, follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode):
                out[rel] = ("link", os.readlink(name, dir_fd=dirfd))
            elif stat.S_ISDIR(info.st_mode):
                out[rel] = ("dir", info)
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dirfd)
                try:
                    walk(child, rel + "/")
                finally:
                    os.close(child)
            elif stat.S_ISREG(info.st_mode):
                out[rel] = ("file", info)
            else:
                out[rel] = ("other", info)
    fd = os.open(plain_path(root), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        walk(fd, "")
    finally:
        os.close(fd)
    return out


def check_envelope(root: Path, env: Envelope) -> dict[str, os.stat_result]:
    """The record is exactly the manifest's closed envelope (agreement item 3). Listed entries
    are checked first (a changed listed entry is a Mismatch); then any unlisted file, symlink,
    special file or hard link refuses: the finalize manifest is a hard precondition."""
    tree = scan_tree(root)
    infos = {}
    for rel, row in env.files.items():
        kind, info = tree.get(rel, ("missing", None))
        require(kind == "file", f"listed_file_missing_or_not_regular:{rel}", Mismatch)
        require(row["size"] is None or row["size"] == info.st_size, f"size_mismatch:{rel}", Mismatch)
        infos[rel] = info
    for rel, target in env.links.items():
        kind, value = tree.get(rel, ("missing", None))
        require(kind == "link" and value == target, f"listed_link_missing_or_changed:{rel}", Mismatch)
    for rel in env.dirs:
        require(tree.get(rel, ("missing",))[0] == "dir", f"listed_dir_missing:{rel}", Mismatch)
    for rel, (kind, info) in tree.items():
        if kind == "file":
            require(rel in env.files, f"envelope_unlisted_file:{rel}")
            require(info.st_nlink == 1, f"envelope_hard_link:{rel}")
        elif kind == "link":
            require(rel in env.links, f"envelope_unlisted_symlink:{rel}")
        elif kind == "dir":
            require(not env.strict_dirs or rel in env.dirs, f"envelope_unlisted_dir:{rel}")
        else:
            raise Refusal(f"envelope_special_file:{rel}")
    return infos


def terminal_check(root: Path, ref: str, env: Envelope, now) -> dict:
    """The window is terminal (agreement item 2): result.json names a plan, a known verdict and a past
    ended_epoch_s; chain.started has chain.exited; no chain.unkilled; courier.sent present.

    `ref` is record-relative (then it and its sibling markers are files of the envelope), or absolute:
    then it and its siblings must be declared inputs of the finalized_manifest.v2 closure, bound by bytes
    (lead ruling 2026-11-08: the terminal evidence is inside the finalized manifest's closure). Every
    marker's bytes are checked; a marker present but not bound refuses, one bound but absent is a mismatch."""
    if ref.startswith("/"):
        path = plain_path(ref)
        bound = env.closure_inputs
        require(str(path) in bound, f"terminal_not_in_closure:{ref}")

        def read(p: Path) -> bytes:
            row = bound[str(p)]
            try:
                fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW)
            except OSError as exc:
                raise Mismatch(f"terminal_marker_unreadable:{p}") from exc
            with os.fdopen(fd, "rb") as stream:
                require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), f"terminal_marker_not_regular:{p}")
                raw = stream.read()
            require(sha_bytes(raw) == row["sha256"] and len(raw) == row["size"], f"terminal_digest_mismatch:{p}",
                    Mismatch)
            return raw

        def present(name):
            p = path.parent / name
            on_disk, declared = os.path.lexists(p), str(p) in bound
            require(not on_disk or declared, f"terminal_marker_not_in_closure:{p}")
            require(on_disk or not declared, f"terminal_marker_bound_but_absent:{p}", Mismatch)
            if on_disk:
                read(p)
            return on_disk
        raw, label = read(path), str(path)
    else:
        rel = safe_relpath(ref)
        require(rel in env.files, f"terminal_not_in_manifest:{rel}")
        fd = open_nofollow(root, rel)
        with os.fdopen(fd, "rb") as stream:
            raw = stream.read()
        require(sha_bytes(raw) == env.files[rel]["sha256"], f"terminal_digest_mismatch:{rel}", Mismatch)
        folder = rel.rpartition("/")[0]

        def present(name):
            p = f"{folder}/{name}" if folder else name
            require(p not in env.links, f"terminal_marker_is_symlink:{p}")
            return p in env.files  # the envelope check proved listed == present, unlisted == absent
        label = rel
    try:
        result = json.loads(raw)
    except ValueError:
        raise Refusal(f"terminal_not_json:{label}") from None
    require(isinstance(result, dict) and isinstance(result.get("plan_id"), str) and result["plan_id"],
            "terminal_plan_absent")
    ended = result.get("ended_epoch_s")
    require(result.get("verdict") in TERMINAL_VERDICTS and type(ended) in (int, float) and math.isfinite(ended)
            and ended <= now(), "record_is_not_terminal")
    require(not present("chain.unkilled"), "terminal_chain_unkilled")
    started, exited = present("chain.started"), present("chain.exited")
    require((started and exited) or (not started and not exited and result["verdict"] == "REFUSED"
                                     and result.get("chain_exit_code") is None and result.get("chain_sha256") is None),
            "terminal_chain_open_or_ambiguous")
    require(present("courier.sent"), "terminal_courier_not_sent")
    return {"terminal": label, "verdict": result["verdict"], "ended_epoch_s": ended, "plan_id": result["plan_id"]}


def restore_gaps(env: Envelope, externals: list[dict]) -> list[str]:
    """Byte-bound closure inputs of a finalize manifest that do not travel in the pack (review S1-04).
    The harvest restore needs each of them; a copy missing one is not restorable on its own."""
    closure = (env.doc or {}).get("closure") or {}
    required = {}
    for group in ("files", "ignored"):
        for name, row in (closure.get(group) or {}).items():
            if isinstance(row, dict):
                required[name] = (row.get("sha256"), row.get("size"))
    carried = {row["path"]: (row["sha256"], row["size"]) for row in externals}
    return sorted(name for name, bound in required.items() if carried.get(name) != bound)


def harvest_entries(entries) -> dict:
    """harvest_offload's transport rows in finalized_manifest.v2 form (its own `_as_finalized`)."""
    require(isinstance(entries, dict), "harvest_pack_entries_malformed", Mismatch)
    out = {}
    for name, row in entries.items():
        require(isinstance(row, dict), f"harvest_pack_entry_malformed:{name}", Mismatch)
        if "link" in row:
            out[name] = {"link": row["link"]}
        elif row.get("dir"):
            out[name] = {"directory": True}
        else:
            out[name] = {"sha256": row.get("sha256"), "size": row.get("size")}
    return out


# -- interlock: the magistrate's lease and shared loop lock (agreement item 1) ---------------

class Lease:
    """Client for the magistrate-owned cool-down lease (`joulewise.air_offload_gate.v1`), the watchdog
    state (`fenced_checkouts == []`) and the persistent loop lock the magistrate takes for every
    arm/measure/dwell transition. Used only when the magistrate passes all three paths."""

    def __init__(self, lease_path, watchdog_path, loop_lock_path, record_manifest_sha256, *, margin_s=120.0,
                 now=time.time):
        self.lease_path, self.watchdog_path = Path(lease_path), Path(watchdog_path)
        self.loop_lock_path = Path(loop_lock_path)
        self.record_sha, self.margin_s, self.now = record_manifest_sha256, margin_s, now
        self.generation, self.deadline_epoch, self.fd = None, None, None

    def acquire(self):
        path = plain_path(self.loop_lock_path)
        # Never create the lock: an offload-created file would not be the magistrate's lock.
        require(path.is_file(), "loop_lock_absent")
        fd = os.open(path, os.O_RDWR | os.O_NOFOLLOW)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(fd)
            raise Refusal("loop_lock_busy") from None
        self.fd = fd

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def check(self):
        try:
            gate, watch = read_json(self.lease_path), read_json(self.watchdog_path)
        except (OSError, ValueError) as exc:
            raise Refusal(f"lease_unreadable:{type(exc).__name__}") from None
        require(isinstance(watch, dict) and watch.get("fenced_checkouts") == [], "lease_watchdog_fenced")
        require(isinstance(gate, dict) and gate.get("schema") == SCHEMA_LEASE and gate.get("phase") == "cooldown"
                and gate.get("armed") is False and gate.get("measuring") is False, "lease_not_cooldown")
        require(gate.get("record_manifest_sha256") == self.record_sha, "lease_record_mismatch")
        require(gate.get("record_committed") is True and gate.get("record_pushed") is True,
                "lease_record_not_committed_and_pushed")
        generation = gate.get("generation")
        require(isinstance(generation, str) and generation, "lease_generation_absent")
        if self.generation is None:
            self.generation = generation
        require(generation == self.generation, "lease_generation_changed")
        ends = [gate.get(k) for k in ("quiet_dwell_epoch_s", "expires_epoch_s")]
        require(all(type(v) in (int, float) and math.isfinite(v) for v in ends), "lease_deadline_malformed")
        self.deadline_epoch = min(ends) - self.margin_s
        if self.now() >= self.deadline_epoch:
            raise DeadlineStop("deadline:lease_expired_or_inside_dwell_margin")
        return gate


# -- MBP side -----------------------------------------------------------------------------

class Offload:
    """State for one window on the MBP: <state_root>/<window_id>/."""

    def __init__(self, state_root: Path, window_id: str, *, runner=None, now=time.time, mono=time.monotonic,
                 deadline_epoch: float | None = None, state_probe=None, lease: Lease | None = None, log=None):
        self.window_id = valid_window(window_id)
        self.state_root = plain_path(state_root)
        self.dir = self.state_root / window_id
        self.parts_dir = self.dir / "parts"
        self.runner, self.now, self.mono = runner, now, mono
        # The deadline is held on the monotonic clock: a wall-clock step cannot extend it.
        self.mono_deadline = None if deadline_epoch is None else mono() + (deadline_epoch - now())
        self.state_probe, self.lease = state_probe, lease
        self.log = log or (lambda message: None)
        self.unlink = os.unlink  # tests inject an interruption here

    # -- guards
    def ensure_dirs(self):
        for path in (self.state_root, self.dir, self.parts_dir, self.dir / "timing"):
            make_dir(path)

    def check_quiet_allowed(self):
        """Refuse when a window is armed or measuring (re-checked before every stage). The lease is the
        primary exclusion once the magistrate wires it; the probe always runs as a second opinion."""
        if self.lease is not None:
            self.lease.check()
        if self.state_probe is None:
            return
        state = self.state_probe()
        require(not state.get("armed"), f"window_armed:{state.get('armed')}")
        require(not state.get("measuring"), f"window_measuring:{state.get('measuring')}")

    def check_deadline(self, need_s: float = 0.0, what: str = ""):
        if self.mono_deadline is not None and self.mono() + need_s > self.mono_deadline:
            raise DeadlineStop(f"deadline:{what}")

    def remaining_s(self) -> float | None:
        return None if self.mono_deadline is None else max(0.0, self.mono_deadline - self.mono())

    def journal(self, row: dict):
        append_jsonl(self.dir / "offload-journal.jsonl", {"t": self.now(), "window_id": self.window_id, **row})

    # -- the record: closed envelope and terminal evidence (both modes)
    def preflight(self, record_root, record_manifest, record_manifest_sha256, terminal):
        record_root = plain_path(record_root)
        require(record_root.is_dir(), "record_root_missing")
        raw = read_record_manifest(record_manifest, record_manifest_sha256)
        env = parse_record_manifest(raw, record_root, Path(record_manifest))
        infos = check_envelope(record_root, env)
        if terminal is None:
            require(self.window_id.startswith(NO_TERMINAL_PREFIXES), "terminal_evidence_required")
            term = {"terminal": None, "skipped_for_synthetic_window": True}
        else:
            term = terminal_check(record_root, terminal, env, self.now)
        return record_root, raw, env, infos, term

    def _local_parts(self, manifest: dict) -> Path:
        return Path(manifest.get("local_parts_dir") or self.parts_dir)

    # -- pack (fallback for R1 and legacy manifests)
    def build_plan(self, record_root: Path, record_manifest: Path, record_manifest_sha256: str,
                   codec: dict, part_bytes: int, duplicate_roots=(), terminal: str | None = None) -> dict:
        record_root, _, env, infos, term = self.preflight(record_root, record_manifest, record_manifest_sha256,
                                                          terminal)
        # Lead ruling 2026-11-08: one pack per window. A v4 session is packed once, by the harvest-off lane.
        require(env.fmt != "finalized_manifest.v2", "finalized_manifest_v2_is_packed_once_by_harvest_off:use_--harvest-pack")
        files, parts, current, current_bytes = [], [], [], 0
        suffix = "zst" if codec["name"] == "zstd" else "gz"
        for rel in sorted(env.files):
            info = infos[rel]
            if current and current_bytes + info.st_size > part_bytes:
                parts.append(current)
                current, current_bytes = [], 0
            current.append(rel)
            current_bytes += info.st_size
            files.append({"path": rel, "size": info.st_size, "mtime_ns": info.st_mtime_ns,
                          "mode": stat.S_IMODE(info.st_mode), "sha256": env.files[rel]["sha256"],
                          "part": f"part-{len(parts):04d}.tar.{suffix}"})
        parts.append(current)
        last = f"part-{len(parts) - 1:04d}.tar.{suffix}"
        links = [{"path": rel, "target": env.links[rel], "part": last} for rel in sorted(env.links)]
        dirs = [{"path": rel, "part": last} for rel in sorted(env.dirs)]
        names = [f"part-{i:04d}.tar.{suffix}" for i in range(len(parts))]
        return {"schema": SCHEMA_PLAN, "window_id": self.window_id, "record_root": str(record_root),
                "record_manifest_sha256": record_manifest_sha256, "record_format": env.fmt, "codec": codec,
                "part_bytes": part_bytes, "files": files, "links": links, "dirs": dirs,
                "raw_bytes": sum(f["size"] for f in files), "terminal": term,
                "closure_external_not_offloaded": env.closure_external,
                "parts": [{"name": name, "files": sum(1 for f in files if f["part"] == name),
                           "raw_bytes": sum(f["size"] for f in files if f["part"] == name)} for name in names],
                "duplicate_roots": [str(plain_path(p)) for p in duplicate_roots],
                "pack_format": "offload_window.v2", "extra_objects": [], "externals": [],
                "local_parts_dir": str(self.parts_dir)}

    def pack(self, record_root, record_manifest, record_manifest_sha256, *, codec, part_bytes=2 << 30,
             duplicate_roots=(), hash_on_mbp=False, terminal=None) -> dict:
        self.ensure_dirs()
        manifest_path = self.dir / MANIFEST_NAME
        if os.path.lexists(manifest_path):  # sealed earlier (the raw files may be released by now)
            manifest = read_json(manifest_path)
            require(manifest["record_manifest_sha256"] == record_manifest_sha256
                    and manifest["record_root"] == str(plain_path(record_root)), "duplicate_run_conflict", Mismatch)
            return manifest
        plan = self.build_plan(Path(record_root), Path(record_manifest), record_manifest_sha256, codec,
                               part_bytes, duplicate_roots, terminal)
        plan_path = self.dir / "plan.json"
        identity = ("window_id", "record_root", "record_manifest_sha256", "part_bytes", "files", "links", "dirs",
                    "parts", "duplicate_roots")
        if os.path.lexists(plan_path):
            old = read_json(plan_path)
            # The codec implementation may differ on resume; the content identity may not.
            require(old.get("schema") == SCHEMA_PLAN and all(old[k] == plan[k] for k in identity)
                    and old["codec"]["name"] == codec["name"], "duplicate_run_conflict", Mismatch)
            plan = old
        else:
            write_once(plan_path, canonical(plan), "duplicate_run_conflict")
        write_once(self.dir / RECORD_MANIFEST_NAME, read_record_manifest(record_manifest, record_manifest_sha256),
                   "record_manifest_changed")
        by_part: dict[str, dict] = {p["name"]: {"files": [], "links": [], "dirs": []} for p in plan["parts"]}
        for key in ("files", "links", "dirs"):
            for row in plan[key]:
                by_part[row["part"]][key].append(row)
        sealed_parts = []
        for part in plan["parts"]:
            self.check_quiet_allowed()
            sealed_parts.append(self._pack_part(Path(plan["record_root"]), part, by_part[part["name"]],
                                                plan["codec"], hash_on_mbp))
        manifest = {**{k: v for k, v in plan.items() if k != "schema"}, "schema": SCHEMA_MANIFEST,
                    "parts": sealed_parts, "compressed_bytes": sum(p["bytes"] for p in sealed_parts)}
        write_once(manifest_path, canonical(manifest), "duplicate_run_conflict")
        return manifest

    # -- one pack per window: consume the harvest-off lane's pack of a finalized_manifest.v2 record
    def adopt_harvest_pack(self, record_root, record_manifest, record_manifest_sha256, harvest_pack, *,
                           duplicate_roots=(), terminal=None) -> dict:
        """The record's single canonical pack is harvest_offload.pack, bound to the committed finalize
        manifest. Its parts are consumed, never repacked: the transport manifest must carry the committed
        pin, the same restore namespace, exactly the finalize entries and only bound external inputs; the
        payload must have its recorded size. Its bytes are verified end to end on the Air (commit digest,
        then every member against the pinned finalize manifest). No raw or payload hashing on the MBP."""
        self.ensure_dirs()
        manifest_path = self.dir / MANIFEST_NAME
        if os.path.lexists(manifest_path):  # sealed earlier (the raw files may be released by now)
            manifest = read_json(manifest_path)
            require(manifest["record_manifest_sha256"] == record_manifest_sha256
                    and manifest["record_root"] == str(plain_path(record_root))
                    and manifest.get("pack_format") == SCHEMA_HARVEST_PACK
                    and manifest.get("local_parts_dir") == str(plain_path(harvest_pack)), "duplicate_run_conflict",
                    Mismatch)
            return manifest
        record_root, raw, env, infos, term = self.preflight(record_root, record_manifest, record_manifest_sha256,
                                                            terminal)
        require(env.fmt == "finalized_manifest.v2", "harvest_pack_needs_finalized_manifest_v2")
        pack_dir = plain_path(harvest_pack)
        require(pack_dir.is_dir(), "harvest_pack_missing")
        require(pack_dir != record_root and record_root not in pack_dir.parents, "harvest_pack_inside_record")
        try:
            fd = os.open(pack_dir / HARVEST_MANIFEST, os.O_RDONLY | os.O_NOFOLLOW)
        except FileNotFoundError:
            raise Refusal("harvest_pack_manifest_missing") from None
        with os.fdopen(fd, "rb") as stream:
            hraw = stream.read()
        hdoc = json.loads(hraw, object_pairs_hook=_no_duplicate_keys)
        require(isinstance(hdoc, dict) and hdoc.get("schema") == SCHEMA_HARVEST_PACK, "harvest_pack_schema")
        require(hdoc.get("finalized_manifest_sha256") == record_manifest_sha256,
                "harvest_pack_bound_to_another_finalize", Mismatch)
        require(hdoc.get("source_root") == str(record_root), "harvest_pack_namespace_differs", Mismatch)
        require(harvest_entries(hdoc.get("entries")) == env.doc["entries"], "harvest_pack_entries_differ_from_finalize",
                Mismatch)
        externals = []
        for member, row in sorted((hdoc.get("external") or {}).items()):
            require(HARVEST_EXTERNAL.match(member) is not None and isinstance(row, dict)
                    and env.closure_inputs.get(row.get("path")) == {"sha256": row.get("sha256"), "size": row.get("size")},
                    f"harvest_pack_external_not_bound:{member}", Mismatch)
            externals.append({"member": member, "path": row["path"], "sha256": row["sha256"], "size": row["size"]})
        payload = hdoc.get("payload")
        require(isinstance(payload, dict) and payload.get("name") == HARVEST_PAYLOAD
                and HEX64.match(str(payload.get("sha256", ""))) is not None and type(payload.get("size")) is int,
                "harvest_pack_payload_malformed", Mismatch)
        info = os.lstat(pack_dir / HARVEST_PAYLOAD)
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_size == payload["size"],
                "harvest_pack_payload_size", Mismatch)
        gaps = restore_gaps(env, externals)
        require(not gaps, f"harvest_pack_not_restorable:missing_external:{gaps[:1]}")
        self._claim_pack_path(pack_dir, record_manifest_sha256, payload["sha256"])
        files = [{"path": rel, "size": infos[rel].st_size, "mtime_ns": infos[rel].st_mtime_ns,
                  "mode": stat.S_IMODE(infos[rel].st_mode), "sha256": env.files[rel]["sha256"], "part": HARVEST_PAYLOAD}
                 for rel in sorted(env.files)]
        raw_bytes = sum(f["size"] for f in files)
        write_once(self.dir / RECORD_MANIFEST_NAME, raw, "record_manifest_changed")
        manifest = {"schema": SCHEMA_MANIFEST, "window_id": self.window_id, "record_root": str(record_root),
                    "record_manifest_sha256": record_manifest_sha256, "record_format": env.fmt,
                    "pack_format": SCHEMA_HARVEST_PACK,
                    "codec": {"name": "zstd", "impl": "harvest_offload", "level": hdoc.get("zstd_level")},
                    "part_bytes": None, "files": files,
                    "links": [{"path": rel, "target": env.links[rel], "part": HARVEST_PAYLOAD} for rel in sorted(env.links)],
                    "dirs": [{"path": rel, "part": HARVEST_PAYLOAD} for rel in sorted(env.dirs)],
                    "externals": externals, "raw_bytes": raw_bytes, "terminal": term,
                    "closure_external_not_offloaded": env.closure_external - len(externals),
                    "parts": [{"name": HARVEST_PAYLOAD, "sha256": payload["sha256"], "bytes": payload["size"],
                               "raw_bytes": raw_bytes, "files": len(files)}],
                    "extra_objects": [{"name": HARVEST_MANIFEST, "sha256": sha_bytes(hraw), "bytes": len(hraw)}],
                    "local_parts_dir": str(pack_dir), "compressed_bytes": payload["size"],
                    "duplicate_roots": [str(plain_path(p)) for p in duplicate_roots]}
        write_once(manifest_path, canonical(manifest), "duplicate_run_conflict")
        self.journal({"event": "harvest_pack_adopted", "payload_sha256": payload["sha256"], "bytes": payload["size"]})
        return manifest

    def _claim_pack_path(self, pack_dir: Path, finalized_sha256: str, payload_sha256: str):
        """Review F2: one pack directory serves one window at a time. The claim binds the path to
        (window_id, finalize digest, payload digest); another window's unreleased claim refuses."""
        claims = make_dir(self.state_root / "pack-claims")
        path = claims / (sha_bytes(str(pack_dir).encode()) + ".json")
        mine = {"path": str(pack_dir), "window_id": self.window_id, "finalized_manifest_sha256": finalized_sha256,
                "payload_sha256": payload_sha256}
        if os.path.lexists(path):
            old = read_json(path)
            if old != mine:
                holder = old.get("window_id")
                released = (isinstance(holder, str) and WINDOW_ID.match(holder) is not None
                            and os.path.lexists(self.state_root / holder / "released.json"))
                require(released and holder != self.window_id, f"harvest_pack_path_held_by:{holder}", Mismatch)
        write_atomic(path, canonical(mine))

    def _pack_part(self, record_root: Path, part: dict, rows: dict, codec: dict, hash_on_mbp: bool) -> dict:
        final, side = self.parts_dir / part["name"], self.parts_dir / (part["name"] + ".json")
        if os.path.lexists(final) and os.path.lexists(side):
            info = read_json(side)
            digest, size = hash_file(final)
            require(digest == info["sha256"] and size == info["bytes"], f"local_part_corrupt:{part['name']}", Mismatch)
            return info
        partial = self.parts_dir / (part["name"] + ".partial")
        for leftover in (partial, final, side):
            with contextlib.suppress(FileNotFoundError):
                os.unlink(leftover)
        self.check_deadline(0, "pack_part")
        started, cpu0 = time.monotonic(), os.times()
        writer = CompressedWriter(codec, partial)
        try:
            with tarfile.open(fileobj=writer, mode="w|", format=tarfile.PAX_FORMAT) as tar:
                for row in rows["dirs"]:
                    member = tarfile.TarInfo(row["path"])
                    member.type, member.mode, member.mtime = tarfile.DIRTYPE, 0o755, 0
                    tar.addfile(member)
                for row in rows["files"]:
                    fd = open_nofollow(record_root, row["path"])
                    with os.fdopen(fd, "rb") as stream:
                        info = os.fstat(stream.fileno())
                        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_size == row["size"]
                                and info.st_mtime_ns == row["mtime_ns"], f"record_changed:{row['path']}", Mismatch)
                        member = tarfile.TarInfo(row["path"])
                        member.size, member.mode, member.mtime = row["size"], row["mode"], row["mtime_ns"] / 1e9
                        member.uid = member.gid = 0
                        member.uname = member.gname = ""
                        tar.addfile(member, _GuardedReader(stream, self, row, hash_on_mbp))
                for row in rows["links"]:
                    require(readlink_rel(record_root, row["path"]) == row["target"],
                            f"record_changed:{row['path']}", Mismatch)
                    member = tarfile.TarInfo(row["path"])
                    member.type, member.linkname, member.mode, member.mtime = tarfile.SYMTYPE, row["target"], 0o755, 0
                    tar.addfile(member)
            writer.close()
        except BaseException:
            writer.abort()
            with contextlib.suppress(FileNotFoundError):
                os.unlink(partial)
            raise
        with open(partial, "rb") as stream:
            os.fsync(stream.fileno())
        digest, size = hash_file(partial)
        os.replace(partial, final)
        cpu1 = os.times()
        info = {"name": part["name"], "sha256": digest, "bytes": size, "raw_bytes": part["raw_bytes"],
                "files": part["files"], "wall_s": round(time.monotonic() - started, 3),
                "cpu_s": round((cpu1.user + cpu1.system + cpu1.children_user + cpu1.children_system)
                               - (cpu0.user + cpu0.system + cpu0.children_user + cpu0.children_system), 3)}
        write_atomic(side, canonical(info))
        self.journal({"event": "part_packed", **info})
        return info

    # -- transport
    def call(self, command: str, *, stdin_path: Path | None = None, offset: int = 0, timeout=None) -> dict:
        require(self.runner is not None, "no_transport")
        remaining = self.remaining_s()
        if remaining is not None:
            timeout = remaining if timeout is None else min(timeout, remaining)
            if timeout <= 0:
                raise DeadlineStop(f"deadline:{command.split()[0]}")
        try:
            rc, out, err = self.runner(command, stdin_path=stdin_path, offset=offset, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            raise DeadlineStop(f"deadline_in_transport:{command.split()[0]}") from exc
        except OSError as exc:
            raise TransportError(f"transport_os_error:{exc}") from exc
        try:
            reply = json.loads(out.decode() or "{}")
        except ValueError:
            reply = {}
        if rc != 0:
            reason = reply.get("error", f"rc={rc}:{err[:200]!r}")
            raise (Mismatch if reply.get("kind") == "mismatch" else TransportError)(f"air:{reason}")
        return reply

    def push(self, manifest: dict) -> dict:
        hello = self.call("hello")
        require(hello.get("gate_version") == GATE_VERSION, "gate_version_mismatch")
        status = self.call(f"stat {self.window_id}")
        manifest_raw = (self.dir / MANIFEST_NAME).read_bytes()
        msha = sha_bytes(manifest_raw)
        if status.get("manifest_sha256") not in (None, msha):
            raise Mismatch("window_id_conflict_on_air")
        if status.get("receipt_manifest_sha256") == msha:
            return status  # already verified on the Air: idempotent
        need = manifest["compressed_bytes"] + (manifest["raw_bytes"] if hello.get("extract") else 0)
        require(hello.get("free_bytes", 0) - need >= hello.get("floor_bytes", 0), "air_ssd_space", TransportError)
        local = self._local_parts(manifest)
        # The sealed digests are sent (the MBP does not re-hash the payload); the Air's commit checks each.
        uploads = [(RECORD_MANIFEST_NAME, self.dir / RECORD_MANIFEST_NAME, manifest["record_manifest_sha256"])]
        uploads += [(p["name"], local / p["name"], p["sha256"]) for p in manifest["parts"]]
        uploads += [(x["name"], local / x["name"], x["sha256"]) for x in manifest.get("extra_objects", [])]
        uploads.append((MANIFEST_NAME, self.dir / MANIFEST_NAME, msha))  # last: its arrival marks completeness
        for name, path, digest in uploads:
            self.check_quiet_allowed()
            info = os.lstat(path)
            require(stat.S_ISREG(info.st_mode), f"upload_not_regular:{name}", Mismatch)
            size = info.st_size
            remote = status.get("files", {}).get(name, {})
            if remote.get("final") == size:
                continue  # committed earlier; commit checked the digest
            offset = remote.get("partial") or 0
            require(offset <= size, f"remote_partial_larger:{name}", Mismatch)
            if offset < size:
                self.check_deadline(0, "push")  # the transport timeout is the remaining budget
                self.call(f"put {self.window_id} {name} {offset} {size - offset}", stdin_path=path, offset=offset)
            self.call(f"commit {self.window_id} {name} {size} {digest}")
            self.journal({"event": "pushed", "name": name, "bytes": size, "sha256": digest})
        return self.call(f"stat {self.window_id}")

    def verify(self, manifest: dict) -> dict:
        self.check_quiet_allowed()
        receipt = self.call(f"verify {self.window_id}")
        self.check_air_receipt(receipt, manifest)
        write_once(self.dir / "receipt-air.json", canonical(receipt), "air_receipt_changed")
        self.journal({"event": "air_verified", "receipt_sha256": receipt["receipt_sha256"]})
        return receipt

    def _manifest_identity(self) -> tuple[str, int]:
        return hash_file(self.dir / MANIFEST_NAME)

    def check_air_receipt(self, receipt, manifest: dict) -> dict:
        body = check_sealed(receipt)
        msha, _ = self._manifest_identity()
        require(body.get("schema") == SCHEMA_AIR and body.get("window_id") == self.window_id
                and body.get("offload_manifest_sha256") == msha
                and body.get("record_manifest_sha256") == manifest["record_manifest_sha256"]
                and body.get("files_verified") == len(manifest["files"])
                and body.get("links_verified") == len(manifest["links"])
                and body.get("dirs_verified") == len(manifest["dirs"])
                and body.get("externals_verified", 0) == len(manifest.get("externals", []))
                and body.get("extra_objects", []) == manifest.get("extra_objects", [])
                and body.get("raw_bytes") == manifest["raw_bytes"]
                and isinstance(body.get("store_volume_uuid"), str)
                and body.get("parts") == [{"name": p["name"], "sha256": p["sha256"], "bytes": p["bytes"]}
                                          for p in manifest["parts"]],
                "air_receipt_does_not_match", Mismatch)
        return body

    def _custody_objects(self, manifest: dict) -> list[dict]:
        msha, msize = self._manifest_identity()
        rsize = (self.dir / RECORD_MANIFEST_NAME).stat().st_size
        rows = [{"name": p["name"], "sha256": p["sha256"], "bytes": p["bytes"]} for p in manifest["parts"]]
        rows += [dict(x) for x in manifest.get("extra_objects", [])]
        rows += [{"name": MANIFEST_NAME, "sha256": msha, "bytes": msize},
                 {"name": RECORD_MANIFEST_NAME, "sha256": manifest["record_manifest_sha256"], "bytes": rsize}]
        return sorted(rows, key=lambda r: r["name"])

    def check_second_receipt(self, receipt, manifest: dict, air_body: dict):
        body = check_sealed(receipt)
        msha, _ = self._manifest_identity()
        require(body.get("schema") == SCHEMA_SECOND and body.get("window_id") == self.window_id
                and body.get("offload_manifest_sha256") == msha and body.get("confirmed") is True
                and body.get("method") in SECOND_METHODS
                and body.get("primary_volume_uuid") == air_body["store_volume_uuid"]
                and sorted(body.get("files", []), key=lambda r: r["name"]) == self._custody_objects(manifest),
                "second_copy_receipt_does_not_match", Mismatch)
        if body["method"] == "second_disk_verified_copy":
            require(body.get("second_volume_uuid") not in (None, body["primary_volume_uuid"]),
                    "second_copy_not_independent", Mismatch)

    def check_fresh(self, fresh, nonce: str, air: dict, second, manifest: dict) -> dict:
        """The Air re-hashed the custody objects (compressed parts, both manifests) just now, for this nonce."""
        body = check_sealed(fresh)
        msha, _ = self._manifest_identity()
        require(body.get("schema") == SCHEMA_FRESH and body.get("window_id") == self.window_id
                and body.get("nonce") == nonce and body.get("offload_manifest_sha256") == msha
                and body.get("air_receipt_sha256") == air["receipt_sha256"]
                and body.get("second_receipt_sha256") == (None if second is None else second["receipt_sha256"])
                and body.get("rechecked") == self._custody_objects(manifest),
                "fresh_receipt_does_not_match", Mismatch)
        return body

    # -- release
    def check_restorable(self, manifest: dict):
        """Review S1-04: before any deletion, the Air copy must be restorable on its own. For a consumed
        harvest pack, every byte-bound closure input of the pinned finalize manifest (external terminal
        evidence, the calibration ledger, any byte-bound link target) must travel in the pack."""
        if manifest.get("pack_format") != SCHEMA_HARVEST_PACK:
            return
        raw = read_record_manifest(self.dir / RECORD_MANIFEST_NAME, manifest["record_manifest_sha256"])
        env = parse_record_manifest(raw, Path(manifest["record_root"]))
        gaps = restore_gaps(env, manifest.get("externals", []))
        require(not gaps, f"not_restorable_from_the_copy:missing_external:{gaps[:1]}")

    def release(self, *, pressure_compressed_local=False) -> dict:
        """Delete the MBP copy only after a FRESH Air receipt and a sealed second-copy receipt, and only bytes
        proven equal to their own bound digests (review F1). Never rmtree."""
        manifest = read_json(self.dir / MANIFEST_NAME)
        if os.path.lexists(self.dir / "released.json"):
            return read_json(self.dir / "released.json")
        self.check_quiet_allowed()
        self.check_restorable(manifest)
        nonce = secrets.token_hex(16)
        receipts = self.call(f"receipts {self.window_id} {nonce}")
        air, second, fresh = receipts.get("air"), receipts.get("second"), receipts.get("fresh")
        require(air is not None, "no_air_receipt")
        air_body = self.check_air_receipt(air, manifest)
        write_once(self.dir / "receipt-air.json", canonical(air), "air_receipt_changed")
        require(fresh is not None, "no_fresh_receipt", Mismatch)
        self.check_fresh(fresh, nonce, air, second, manifest)
        write_atomic(self.dir / "receipt-fresh.json", canonical(fresh))
        self.check_quiet_allowed()  # again after the receipt round trip: an arm in between stops the release
        if second is None:
            if not pressure_compressed_local:
                raise Refusal("second_copy_not_confirmed")
            if os.path.lexists(self.dir / "raw-released.json"):
                return read_json(self.dir / "raw-released.json")
            # Pressure rule: raw goes, the Air-verified compressed parts stay on the MBP,
            # so two verified copies still exist (MBP parts + Air SSD).
            self._local_pack_rows(manifest, require_all=True)
            result = self._delete_raw(manifest, "pressure_compressed_local", fresh)
            write_atomic(self.dir / "raw-released.json", canonical(result))
            return result
        self.check_second_receipt(second, manifest, air_body)
        write_once(self.dir / "receipt-second.json", canonical(second), "second_receipt_changed")
        # Review F2: every local pack object must still be THIS window's sealed object before anything goes.
        pack_rows = None if os.path.lexists(self.dir / "deleting-parts.json") else self._local_pack_rows(manifest)
        result = self._delete_raw(manifest, "two_verified_copies", fresh) if not os.path.lexists(
            self.dir / "raw-released.json") else read_json(self.dir / "raw-released.json")
        parts = self._delete_parts(manifest, pack_rows)
        result = {**result, "parts_deleted": True, "pack_objects_deleted": parts, "rule": "two_verified_copies"}
        write_atomic(self.dir / "released.json", canonical(result))
        self.journal({"event": "released", **{k: result[k] for k in ("files_deleted", "rule")}})
        return result

    def _hash_guarded(self, root: Path, rel: str | None = None) -> tuple[str, int, os.stat_result]:
        """sha256 of one file opened without following links; the deadline is checked per chunk."""
        fd = open_nofollow(root, rel) if rel is not None else os.open(root, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            require(stat.S_ISREG(info.st_mode), f"not_regular:{rel or root}", Mismatch)
            digest, size = hashlib.sha256(), 0
            for chunk in iter(lambda: stream.read(4 * CHUNK), b""):
                digest.update(chunk)
                size += len(chunk)
                self.check_deadline(0, "release_hash")
        return digest.hexdigest(), size, info

    def _local_pack_rows(self, manifest: dict, require_all=False) -> list[dict]:
        """Each local pack object (parts, extra objects) proven to be this window's sealed object."""
        local, rows = self._local_parts(manifest), []
        objects = [(p["name"], p["sha256"], p["bytes"]) for p in manifest["parts"]]
        objects += [(x["name"], x["sha256"], x["bytes"]) for x in manifest.get("extra_objects", [])]
        for name, digest, size in objects:
            path = local / name
            if not os.path.lexists(path):
                require(not require_all, f"local_part_missing:{name}", Mismatch)
                continue
            got, got_size, info = self._hash_guarded(path)
            require((got, got_size) == (digest, size), f"local_pack_changed:{name}", Mismatch)
            rows.append({"path": str(path), "name": name, "sha256": digest, "size": size,
                         "mtime_ns": info.st_mtime_ns})
        return rows

    def _delete_parts(self, manifest: dict, rows: list[dict] | None) -> int:
        """Journaled deletion of the local pack objects (review F2). Fresh rows were just hashed: a stat
        check suffices before unlink; a resumed deletion re-hashes every remaining object first."""
        path = self.dir / "deleting-parts.json"
        if rows is None:
            journal = read_json(path)
            require(journal.get("window_id") == self.window_id, "parts_journal_mismatch", Mismatch)
            if journal["state"] == "deleted":
                return len(journal["rows"])
            rows, rehash = journal["rows"], True
        else:
            journal = {"schema": SCHEMA_DELETING, "window_id": self.window_id, "state": "deleting", "rows": rows}
            write_atomic(path, canonical(journal))
            rehash = False
        remaining = []
        for row in rows:
            target = Path(row["path"])
            if not os.path.lexists(target):
                continue
            if rehash:
                got, size, _ = self._hash_guarded(target)
                require((got, size) == (row["sha256"], row["size"]), f"local_pack_changed:{row['name']}", Mismatch)
            else:
                info = os.lstat(target)
                require(stat.S_ISREG(info.st_mode) and info.st_size == row["size"]
                        and info.st_mtime_ns == row["mtime_ns"], f"local_pack_changed:{row['name']}", Mismatch)
            remaining.append(target)
        for target in remaining:
            with contextlib.suppress(FileNotFoundError):
                self.unlink(target)
        local = self._local_parts(manifest)
        if local != self.parts_dir:
            with contextlib.suppress(OSError):
                os.rmdir(local)  # only when empty (the harvest lane's copy of the finalize manifest may stay)
        write_atomic(path, canonical({**journal, "state": "deleted"}))
        return len(rows)

    def _inventory(self, manifest: dict) -> tuple[list[dict], list[dict]]:
        """What this release will delete. Every present file of the record AND of each duplicate root must be
        the sealed path with the sealed size (and, in the record, the sealed mtime); its content is proven
        against its own bound digest before any unlink (review F1). A difference refuses the release."""
        roots = [manifest["record_root"]] + list(manifest.get("duplicate_roots", []))
        rows, skipped = [], []
        for index, root_s in enumerate(roots):
            root = Path(root_s)
            if not root.is_dir() or root.is_symlink():
                skipped.append({"root": root_s, "reason": "absent_or_symlink"})
                continue
            differs = "record_changed_since_offload" if index == 0 else f"duplicate_differs:{root_s}"
            for row in manifest["files"]:
                try:
                    info = lstat_rel(root, row["path"])
                except FileNotFoundError:
                    continue
                require(stat.S_ISREG(info.st_mode) and info.st_size == row["size"]
                        and (index > 0 or info.st_mtime_ns == row["mtime_ns"]), f"{differs}:{row['path']}", Mismatch)
                rows.append({"root": root_s, "path": row["path"], "kind": "file", "size": info.st_size,
                             "mtime_ns": info.st_mtime_ns, "sha256": row["sha256"]})
            for row in manifest["links"]:
                try:
                    target = readlink_rel(root, row["path"])
                except (FileNotFoundError, OSError):
                    continue
                require(target == row["target"], f"{differs}:{row['path']}", Mismatch)
                rows.append({"root": root_s, "path": row["path"], "kind": "link", "target": target})
        return rows, skipped

    def _delete_raw(self, manifest: dict, rule: str, fresh: dict) -> dict:
        """Journal `deleting` (the inventory, outside the record), prove every remaining file's content against
        its own bound digest and every link's text, unlink, remove now-empty directories, journal `deleted`."""
        path = self.dir / "deleting.json"
        resumed = os.path.lexists(path)
        if resumed:
            journal = read_json(path)
            require(journal.get("schema") == SCHEMA_DELETING and journal.get("window_id") == self.window_id
                    and journal.get("record_manifest_sha256") == manifest["record_manifest_sha256"],
                    "deletion_journal_mismatch", Mismatch)
            if journal["state"] == "deleted":
                return journal["result"]
        else:
            rows, skipped = self._inventory(manifest)
            journal = {"schema": SCHEMA_DELETING, "window_id": self.window_id, "state": "deleting", "rule": rule,
                       "record_manifest_sha256": manifest["record_manifest_sha256"],
                       "fresh_receipt_sha256": fresh["receipt_sha256"], "started_epoch_s": self.now(),
                       "inventory": rows, "skipped": skipped}
            write_atomic(path, canonical(journal))
        rows = journal["inventory"]
        record_root = manifest["record_root"]
        # Pass 1: every remaining entry is the bound content (by path and digest), and the record holds nothing new.
        remaining = []
        for row in rows:
            root = Path(row["root"])
            try:
                if row["kind"] == "file":
                    got, size, info = self._hash_guarded(root, row["path"])
                    require(got == row["sha256"] and size == row["size"] and info.st_mtime_ns == row["mtime_ns"]
                            and info.st_nlink == 1, f"content_differs_from_bound_digest:{row['root']}:{row['path']}",
                            Mismatch)
                else:
                    require(readlink_rel(root, row["path"]) == row["target"],
                            f"changed_during_deletion:{row['path']}", Mismatch)
            except FileNotFoundError:
                continue  # deleted by the interrupted run
            remaining.append(row)
        if Path(record_root).is_dir():
            listed = {row["path"] for row in rows if row["root"] == record_root}
            for rel, (kind, _) in scan_tree(Path(record_root)).items():
                require(kind == "dir" or rel in listed, f"record_changed_since_offload:new:{rel}", Mismatch)
        self.check_quiet_allowed()
        # Pass 2: unlink (files first, links last), each file re-stat'ed right before; then empty directories.
        for row in sorted(remaining, key=lambda r: r["kind"] != "file"):
            fd, leaf = parent_fd(Path(row["root"]), row["path"])
            try:
                if row["kind"] == "file":
                    info = os.stat(leaf, dir_fd=fd, follow_symlinks=False)
                    require(stat.S_ISREG(info.st_mode) and info.st_size == row["size"]
                            and info.st_mtime_ns == row["mtime_ns"], f"changed_during_deletion:{row['path']}", Mismatch)
                self.unlink(leaf, dir_fd=fd)
            finally:
                os.close(fd)
        for root in sorted({row["root"] for row in rows}):
            if not Path(root).is_dir():
                continue
            for directory, _, _ in os.walk(root, topdown=False, followlinks=False):
                with contextlib.suppress(OSError):
                    if Path(directory) != Path(root):
                        os.rmdir(directory)
        result = {"window_id": self.window_id, "rule": journal["rule"],
                  "files_deleted": sum(1 for r in rows if r["kind"] == "file"),
                  "links_deleted": sum(1 for r in rows if r["kind"] == "link"),
                  "skipped": journal["skipped"], "resumed": resumed, "released_epoch_s": self.now()}
        write_atomic(path, canonical({**journal, "state": "deleted", "result": result}))
        return result


class _GuardedReader:
    """File reader for tarfile: deadline checks every 64 MiB, optional hashing."""

    def __init__(self, stream, offload: Offload, row: dict, hashing: bool):
        self.stream, self.offload, self.row = stream, offload, row
        self.digest = hashlib.sha256() if hashing else None
        self.seen = 0

    def read(self, size=-1):
        data = self.stream.read(size)
        before, self.seen = self.seen, self.seen + len(data)
        if self.digest is not None:
            self.digest.update(data)
            if data == b"" or self.seen == self.row["size"]:
                require(self.digest.hexdigest() == self.row["sha256"], f"mbp_hash_mismatch:{self.row['path']}", Mismatch)
        if before // (64 << 20) != self.seen // (64 << 20):
            self.offload.check_deadline(0, "pack")
        return data


# -- MBP probes, transports and receipts ------------------------------------------------------

def default_state_probe(launch_agents=Path.home() / "Library/LaunchAgents", markers=()):
    """LaunchAgent and process census. Fail closed (review S1-03): an unreadable LaunchAgents directory, a ps
    that cannot run, exits nonzero, prints nothing, prints an unparseable line, or does not list this very
    process, all count as NOT quiet."""
    def probe():
        armed = []
        try:
            if launch_agents.is_dir():
                armed = sorted(p.name for p in launch_agents.iterdir()
                               if p.name.startswith(ARMED_PREFIXES) and p.name.endswith(".plist"))
        except OSError as exc:
            armed = [f"launch_agents_unreadable:{type(exc).__name__}"]
        armed += [str(m) for m in markers if os.path.lexists(m)]
        try:
            census = subprocess.run(["/bin/ps", "-axo", "pid=,args="], capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.SubprocessError) as exc:
            return {"armed": armed, "measuring": [f"process_census_failed:{type(exc).__name__}"]}
        lines = [line for line in (census.stdout or "").splitlines() if line.strip()]
        parsed = [re.match(r"\s*(\d+)(?:\s|$)", line) for line in lines]
        mine = os.getpid()
        if census.returncode != 0 or not lines or not all(parsed) or mine not in {int(m.group(1)) for m in parsed}:
            return {"armed": armed, "measuring": [f"process_census_failed:rc={census.returncode},lines={len(lines)}"]}
        measuring = [line.strip()[:120] for line in lines
                     if MEASURING.search(line) and not line.strip().startswith(f"{mine} ")]
        return {"armed": armed, "measuring": measuring}
    return probe


def ssh_argv(host: str, key: Path, known_hosts: Path) -> list[str]:
    """No user ssh config (-F /dev/null), pinned host key, batch mode, explicit identity."""
    require(HOST.match(host or "") is not None, "bad_air_host")
    for path in (key, known_hosts):
        require(plain_path(path).is_file(), f"ssh_file_absent:{path}")
    return ["/usr/bin/ssh", "-F", "/dev/null", "-i", str(key), "-T", "-o", "BatchMode=yes",
            "-o", "IdentitiesOnly=yes", "-o", "StrictHostKeyChecking=yes", "-o", f"UserKnownHostsFile={known_hosts}",
            "-o", "GlobalKnownHostsFile=/dev/null", "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=5",
            "-o", "ServerAliveCountMax=3", "-o", "Compression=no", "-o", "RequestTTY=no", host]


def _stdin_runner(argv_for):
    def run(command, *, stdin_path=None, offset=0, timeout=None):
        argv, env = argv_for(command)
        if stdin_path is None:
            return run_process_group(argv, timeout=timeout, env=env)
        fd = os.open(stdin_path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as stream:
            stream.seek(offset)
            return run_process_group(argv, stdin=stream, timeout=timeout, env=env)
    return run


def ssh_runner(host: str, key: Path, known_hosts: Path):
    """The real transport: one ssh call per gate verb; the Air's forced command decides."""
    base = ssh_argv(host, key, known_hosts)
    return _stdin_runner(lambda command: ([*base, command], None))


def local_gate_runner(binding: Path, *, extract=True, python=sys.executable):
    """Testing transport for a single machine: the gate CLI as a local subprocess, with the same
    stdin/stdout protocol and SSH_ORIGINAL_COMMAND as the forced command. No network."""
    argv = [python, "-B", str(Path(__file__).resolve()), "air-gate", "--binding", str(binding)]
    if not extract:
        argv.append("--no-extract")

    def argv_for(command):
        return argv, {**os.environ, "SSH_ORIGINAL_COMMAND": command}
    return _stdin_runner(argv_for)


def load_rates(state_root: Path, seed: Path | None = RATES_SEED) -> dict:
    rates = dict(DEFAULT_RATES)
    for path in (seed, state_root / "rates.json"):
        if path is None:
            continue
        with contextlib.suppress(OSError, ValueError):
            doc = read_json(path)
            rates.update({k: float(v) for k, v in doc.get("rates", doc).items()
                          if k in DEFAULT_RATES and isinstance(v, (int, float)) and v > 0})
    return rates


def predict_s(raw: int, rates: dict, done: dict, recheck_bytes: int = 0, compressed: int | None = None) -> float:
    compressed = raw / rates["ratio"] if compressed is None else compressed
    pack = 0 if done.get("packed") else raw / (rates["pack_raw_mb_s"] * 1e6)
    push = 0 if done.get("verified") else compressed / (rates["push_mb_s"] * 1e6)
    verify = 0 if done.get("verified") else raw / (rates["verify_raw_mb_s"] * 1e6)
    recheck = (recheck_bytes + compressed) / (rates["recheck_mb_s"] * 1e6)
    return pack + push + verify + recheck + 10.0  # ssh handshakes and fsyncs


ACTIVITY_START, ACTIVITY_SPAN = "activity-start.json", "activity-span.json"


def run_offload(args, *, runner, state_probe, now=None, mono=None, lease: Lease | None = None,
                alarm=True) -> int:
    """The magistrate's one call after finalize. Writes start/end receipts whatever happens."""
    now, mono = now or time.time, mono or time.monotonic
    def action(off, span, state_root, deadline):
        outcome = _run_stages(args, off, state_root, span, runner, now, mono, deadline, state_probe, lease)
        if any("mismatch" in row for row in outcome["older"]):
            return Mismatch.code, {**outcome, "outcome": "older_window_mismatch"}
        return 0, outcome
    return _supervised(args, "offload", action, runner=runner, state_probe=state_probe, now=now, mono=mono,
                       lease=lease, alarm=alarm)


def run_release(args, *, runner, state_probe, now=None, mono=None, lease: Lease | None = None,
                alarm=True) -> int:
    """A standalone release under exactly the same supervision as `run` (review F3): the state lock that triage
    reads, start/end receipts, the probe (plus the lease when wired), a bounded monotonic deadline with the
    120 s margin left to the caller's --deadline-epoch or the lease, the admission prediction and the alarm."""
    now, mono = now or time.time, mono or time.monotonic
    def action(off, span, state_root, deadline):
        off.check_quiet_allowed()
        require((off.dir / MANIFEST_NAME).exists(), "nothing_offloaded_for_this_window")
        write_atomic(off.dir / "timing" / "release-start.json", canonical(span))
        manifest = read_json(off.dir / MANIFEST_NAME)
        rates = load_rates(state_root, getattr(args, "rates_seed", RATES_SEED))
        predicted = predict_release_s(manifest, rates)
        span["predicted_s"] = round(predicted, 1)
        off.check_deadline(predicted * args.safety, "predicted_overrun")
        result = {}
        pressure = args.pressure_compressed_local and _pressure(args, state_root)
        span["stages"].append(_stage("release", now, lambda: result.update(
            off.release(pressure_compressed_local=pressure))))
        return 0, {"outcome": "released", "result": result}
    return _supervised(args, "release", action, runner=runner, state_probe=state_probe, now=now, mono=mono,
                       lease=lease, alarm=alarm)


def _supervised(args, kind, action, *, runner, state_probe, now, mono, lease, alarm) -> int:
    try:
        state_root = plain_path(args.state_root)
        valid_window(args.window_id)
    except Refusal as exc:
        print(json.dumps({"outcome": type(exc).__name__, "reason": str(exc)}))
        return exc.code
    state_root.mkdir(parents=True, exist_ok=True)
    lock_fd = os.open(state_root / ".lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o644)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(lock_fd)
        print(json.dumps({"outcome": "refused", "reason": "offload_already_running"}))
        return Refusal.code
    started_epoch, started_mono = now(), time.monotonic_ns()
    activity = {"kind": kind, "window_id": args.window_id, "started_epoch_s": started_epoch,
                "started_monotonic_ns": started_mono}
    write_atomic(state_root / ACTIVITY_START, canonical(activity))
    deadline = args.deadline_epoch if args.deadline_epoch is not None else now() + args.budget_s
    span = {"schema": SCHEMA_SPAN, "stage_id": f"{kind}-{args.window_id}", "kind": "backup", "activity": kind,
            "window_id": args.window_id, "started_epoch_s": started_epoch, "started_monotonic_ns": started_mono,
            "deadline_epoch_s": deadline, "stages": [],
            "interlock": {"mode": "lease+loop_lock+probe" if lease is not None else "probe_only"}}
    rc, outcome, off = 0, {}, None
    try:
        if lease is not None:
            lease.acquire()
            lease.check()
            deadline = min(deadline, lease.deadline_epoch)
            span.update(deadline_epoch_s=deadline)
            span["interlock"]["generation"] = lease.generation
        off = Offload(state_root, args.window_id, runner=runner, now=now, mono=mono, deadline_epoch=deadline,
                      state_probe=state_probe, lease=lease)
        with alarm_guard(off.remaining_s() if alarm else None):
            rc, outcome = action(off, span, state_root, deadline)
    except Refusal as exc:
        rc, outcome = exc.code, {"outcome": type(exc).__name__, "reason": str(exc)}
    except OSError as exc:  # e.g. ENOSPC; resumable, but never silent
        rc, outcome = 6, {"outcome": "io_error", "reason": f"{type(exc).__name__}:{exc}"}
    finally:
        span.update(ended_epoch_s=now(), ended_monotonic_ns=time.monotonic_ns(), rc=rc, **outcome,
                    ended_before_deadline=now() <= deadline)
        if off is not None and off.dir.is_dir() and not off.dir.is_symlink():
            (off.dir / "timing").mkdir(exist_ok=True)
            write_atomic(off.dir / "timing" / f"{kind}-span.json", canonical(span))
            off.journal({"event": f"{kind}_end", "rc": rc, **outcome})
        write_atomic(state_root / ACTIVITY_SPAN, canonical({**activity, "ended_epoch_s": span["ended_epoch_s"],
                                                             "rc": rc}))
        if lease is not None:
            lease.close()
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)
    print(json.dumps(span, sort_keys=True))
    return rc


def predict_release_s(manifest: dict, rates: dict) -> float:
    """Fresh recheck on the Air, plus proving every byte to delete against its bound digest on the MBP."""
    roots = 1 + len(manifest.get("duplicate_roots", []))
    return (manifest["compressed_bytes"] / (rates["recheck_mb_s"] * 1e6)
            + (manifest["raw_bytes"] * roots + manifest["compressed_bytes"]) / (rates["release_hash_mb_s"] * 1e6) + 10.0)


def _run_stages(args, off, state_root, span, runner, now, mono, deadline, state_probe, lease) -> dict:
    off.check_quiet_allowed()
    off.ensure_dirs()
    write_atomic(off.dir / "timing" / "offload-start.json", canonical(span))
    rates = load_rates(state_root, getattr(args, "rates_seed", RATES_SEED))
    manifest_path = off.dir / MANIFEST_NAME
    harvest_pack = getattr(args, "harvest_pack", None)
    done = {"packed": manifest_path.exists() or harvest_pack is not None,
            "verified": (off.dir / "receipt-air.json").exists()}
    compressed = None
    if manifest_path.exists():
        sealed_manifest = read_json(manifest_path)
        raw_bytes, compressed = sealed_manifest["raw_bytes"], sealed_manifest["compressed_bytes"]
    else:
        raw_bytes = _raw_size(args)
        if harvest_pack is not None:
            with contextlib.suppress(OSError):
                compressed = os.lstat(Path(harvest_pack) / HARVEST_PAYLOAD).st_size
    older_bytes, older_s = _pending_older(state_root, args.window_id, rates) if args.release_older else (0, 0.0)
    predicted = predict_s(raw_bytes, rates, done, 0, compressed) + older_s
    span["predicted_s"] = round(predicted, 1)
    span["rates_used"] = rates
    off.check_deadline(predicted * args.safety, "predicted_overrun")
    older = []
    if args.release_older:
        span["stages"].append(_stage("release_older", now, lambda: older.extend(release_older(
            state_root, args.window_id, runner, now, mono, deadline, state_probe, lease,
            args.pressure_compressed_local and _pressure(args, state_root)))))
    manifest = {}
    if harvest_pack is not None:  # lead ruling 2026-11-08: one pack per window, consumed as is
        span["stages"].append(_stage("adopt_harvest_pack", now, lambda: manifest.update(off.adopt_harvest_pack(
            args.record_root, args.record_manifest, args.record_manifest_sha256, harvest_pack,
            duplicate_roots=args.duplicate_root, terminal=args.terminal))))
    else:
        span["stages"].append(_stage("pack", now, lambda: manifest.update(off.pack(
            args.record_root, args.record_manifest, args.record_manifest_sha256,
            codec=choose_codec(args.codec, args.level, args.threads), part_bytes=args.part_mib << 20,
            duplicate_roots=args.duplicate_root, hash_on_mbp=args.hash_on_mbp, terminal=args.terminal))))
    if not done["verified"]:
        span["stages"].append(_stage("push", now, lambda: off.push(manifest)))
        span["stages"].append(_stage("verify", now, lambda: off.verify(manifest)))
    held = None
    try:  # the second copy usually lands later; the next run's release_older picks it up
        span["stages"].append(_stage("release", now, lambda: off.release(
            pressure_compressed_local=args.pressure_compressed_local and _pressure(args, state_root))))
    except Refusal as exc:
        if type(exc) is not Refusal:
            raise
        held = str(exc)
    outcome = {"outcome": "verified_on_air", "raw_bytes": manifest["raw_bytes"],
               "compressed_bytes": manifest["compressed_bytes"], "record_format": manifest["record_format"],
               "pack_format": manifest.get("pack_format", "offload_window.v2"),
               "terminal": manifest["terminal"], "release_held": held, "older": older,
               "disk_pressure": _pressure(args, state_root)}
    _update_rates(state_root, rates, manifest, span, older_bytes)
    return outcome


def _stage(name, now, action):
    start = now()
    action()
    return {"name": name, "started_epoch_s": start, "ended_epoch_s": now()}


def _raw_size(args) -> int:
    raw = read_record_manifest(args.record_manifest, args.record_manifest_sha256)
    root = plain_path(args.record_root)
    env = parse_record_manifest(raw, root, Path(args.record_manifest))
    total = 0
    for rel in env.files:
        try:
            total += lstat_rel(root, rel).st_size
        except FileNotFoundError:
            raise Mismatch(f"listed_file_missing_or_not_regular:{rel}") from None
    return total


def _pending_older(state_root: Path, current: str, rates: dict) -> tuple[int, float]:
    """(compressed bytes the Air rechecks, predicted seconds) for older windows still to release."""
    total, seconds = 0, 0.0
    for directory in state_root.iterdir():
        if directory.name == current or not WINDOW_ID.match(directory.name) or directory.is_symlink():
            continue
        with contextlib.suppress(OSError, ValueError, KeyError):
            if not (directory / "released.json").exists():
                manifest = read_json(directory / MANIFEST_NAME)
                total += manifest["compressed_bytes"]
                seconds += predict_release_s(manifest, rates)
    return total, seconds


def _pressure(args, state_root: Path) -> bool:
    return free_bytes(state_root) < args.min_free_gib * (1 << 30)


def _update_rates(state_root: Path, rates: dict, manifest: dict, span: dict, older_bytes: int):
    by = {s["name"]: s["ended_epoch_s"] - s["started_epoch_s"] for s in span["stages"]}
    new = dict(rates)
    if by.get("pack", 0) > 1:
        new["pack_raw_mb_s"] = manifest["raw_bytes"] / 1e6 / by["pack"]
    if by.get("push", 0) > 1:
        new["push_mb_s"] = manifest["compressed_bytes"] / 1e6 / by["push"]
    if by.get("verify", 0) > 1:
        new["verify_raw_mb_s"] = manifest["raw_bytes"] / 1e6 / by["verify"]
    if by.get("release_older", 0) > 1 and older_bytes:
        new["recheck_mb_s"] = older_bytes / 1e6 / by["release_older"]
    if manifest["compressed_bytes"]:
        new["ratio"] = manifest["raw_bytes"] / manifest["compressed_bytes"]
    write_atomic(state_root / "rates.json", canonical(new))


def release_older(state_root: Path, current: str, runner, now, mono, deadline, state_probe, lease,
                  pressure_local) -> list:
    results = []
    for directory in sorted(p for p in state_root.iterdir() if p.is_dir() and not p.is_symlink()):
        if directory.name == current or not WINDOW_ID.match(directory.name):
            continue
        if not (directory / MANIFEST_NAME).exists() or (directory / "released.json").exists():
            continue
        off = Offload(state_root, directory.name, runner=runner, now=now, mono=mono, deadline_epoch=deadline,
                      state_probe=state_probe, lease=lease)
        try:
            results.append(off.release(pressure_compressed_local=pressure_local))
        except DeadlineStop:
            raise
        except Mismatch as exc:  # keep going for the current window; the run still exits 3
            results.append({"window_id": directory.name, "mismatch": str(exc)})
        except Refusal as exc:
            results.append({"window_id": directory.name, "held": str(exc)})
    return results


def triage(state_root: Path, window_id: str, dwell_start_epoch: float, margin_s: float) -> dict:
    """Evidence for the pre-arm `quiet_start_state` entry; passes only if no offload can be active."""
    reasons = []
    lock = state_root / ".lock"
    if lock.exists():
        fd = os.open(lock, os.O_RDWR | os.O_NOFOLLOW)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(fd, fcntl.LOCK_UN)
        except BlockingIOError:
            reasons.append("offload_running")
        finally:
            os.close(fd)
    span_path = state_root / valid_window(window_id) / "timing" / "offload-span.json"
    start_path = span_path.with_name("offload-start.json")
    span = read_json(span_path) if span_path.exists() else None
    start = read_json(start_path) if start_path.exists() else None
    if start is not None and (span is None or span["started_epoch_s"] < start["started_epoch_s"]):
        reasons.append("offload_started_without_end_receipt")
    if span is not None and span["ended_epoch_s"] > dwell_start_epoch - margin_s:
        reasons.append("offload_ended_inside_dwell_margin")
    # Any offload activity on this MBP (run or a standalone release, for any window) counts (review F3).
    act_start = read_json(state_root / ACTIVITY_START) if (state_root / ACTIVITY_START).exists() else None
    act_span = read_json(state_root / ACTIVITY_SPAN) if (state_root / ACTIVITY_SPAN).exists() else None
    if act_start is not None and (act_span is None or act_span["started_epoch_s"] < act_start["started_epoch_s"]):
        reasons.append("offload_activity_without_end_receipt")
    if act_span is not None and act_span["ended_epoch_s"] > dwell_start_epoch - margin_s:
        reasons.append("offload_activity_inside_dwell_margin")
    return {"schema": SCHEMA_TRIAGE, "activity": act_span, "window_id": window_id, "quiet_start_state_ok": not reasons,
            "reasons": reasons, "span": span, "dwell_start_epoch_s": dwell_start_epoch, "margin_s": margin_s,
            "air_receipt": (state_root / window_id / "receipt-air.json").exists(),
            "second_copy": (state_root / window_id / "receipt-second.json").exists(),
            "free_bytes": free_bytes(state_root)}


# -- Air side: the landing store, bound to one APFS volume ------------------------------------

class VolumeProbe:
    """Real volume identity from diskutil; tests inject a fake."""

    def mounted(self, path: Path) -> bool:
        return os.path.ismount(path)

    def identity(self, path: Path) -> dict:
        try:
            out = subprocess.run(["/usr/sbin/diskutil", "info", "-plist", str(path)], capture_output=True,
                                 timeout=30)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Refusal(f"diskutil_failed:{type(exc).__name__}") from None
        require(out.returncode == 0, "diskutil_failed")
        info = plistlib.loads(out.stdout)
        stores = sorted(s.get("APFSPhysicalStore") for s in info.get("APFSPhysicalStores", []) if isinstance(s, dict))
        return {"volume_uuid": info.get("VolumeUUID"), "volume_name": info.get("VolumeName"),
                "mount_point": info.get("MountPoint"), "internal": bool(info.get("Internal")),
                "filesystem": info.get("FilesystemType"), "owners_enabled": info.get("GlobalPermissionsEnabled"),
                "physical_stores": stores or [info.get("ParentWholeDisk")]}


def find_mount(path: Path, probe) -> Path:
    for candidate in (path, *path.parents):
        if candidate.exists() and probe.mounted(candidate):
            return candidate
    return Path("/")


class Store:
    """The landing store: a directory on one bound APFS volume. Refuses when the volume is not
    mounted, is a different volume (UUID), lost its marker, or (for writes) is below the free floor."""

    def __init__(self, binding_path, probe=None):
        self.binding_path, self.probe = Path(binding_path), probe or VolumeProbe()
        try:
            doc = read_json(self.binding_path)
        except (OSError, ValueError) as exc:
            raise Refusal(f"store_binding_unreadable:{type(exc).__name__}") from None
        require(isinstance(doc, dict) and doc.get("schema") == SCHEMA_BINDING
                and all(isinstance(doc.get(k), str) for k in ("store_root", "mount_point", "volume_uuid", "store_id"))
                and isinstance(doc.get("min_free_gib"), (int, float)), "store_binding_malformed")
        self.doc, self.root, self.mount = doc, Path(doc["store_root"]), Path(doc["mount_point"])

    @property
    def floor_bytes(self) -> int:
        return int(self.doc["min_free_gib"] * (1 << 30))

    def check(self, *, full=True, write=False) -> "Store":
        require(self.probe.mounted(self.mount), f"store_not_mounted:{self.mount}")
        root = plain_path(self.root)
        require(self.mount in root.parents and root.is_dir(), "store_root_missing")
        try:
            marker = read_json(root / MARKER_NAME)
        except (OSError, ValueError):
            raise Refusal("store_marker_missing") from None
        require(marker.get("store_id") == self.doc["store_id"] and marker.get("volume_uuid") == self.doc["volume_uuid"],
                "store_marker_mismatch")
        if full:
            ident = self.probe.identity(self.mount)
            require(ident.get("volume_uuid") == self.doc["volume_uuid"], "store_volume_uuid_mismatch")
            require(not ident.get("internal"), "store_on_internal_disk")
            require(self.doc.get("allow_noowners") or ident.get("owners_enabled") is not False,
                    "store_volume_ignores_ownership")
        if write:
            require(free_bytes(root) >= self.floor_bytes, "store_below_free_floor")
        return self


def init_store(store_root, binding_path, *, role="primary", min_free_gib=100.0, probe=None, mount_point=None,
               allow_noowners=False, rebind=False) -> dict:
    """Bind a store directory to its APFS volume by UUID (run once, explicitly). Idempotent."""
    probe = probe or VolumeProbe()
    require(role in ("primary", "second"), "bad_role")
    store_root = plain_path(store_root)
    mount = Path(mount_point) if mount_point else find_mount(store_root.parent, probe)
    require(mount != Path("/") and mount in store_root.parents, "store_on_boot_volume")
    require(probe.mounted(mount), "store_volume_not_mounted")
    ident = probe.identity(mount)
    require(isinstance(ident.get("volume_uuid"), str) and ident["volume_uuid"], "store_volume_uuid_unknown")
    require(not ident.get("internal"), "store_on_internal_disk")
    require(allow_noowners or ident.get("owners_enabled") is not False,
            "store_volume_ignores_ownership: run `sudo diskutil enableOwnership <volume>` first")
    require(store_root.parent.is_dir(), "store_parent_missing")
    make_dir(store_root, 0o750)
    marker_path = store_root / MARKER_NAME
    if os.path.lexists(marker_path):
        marker = read_json(marker_path)
        require(marker.get("volume_uuid") == ident["volume_uuid"], "store_marker_from_other_volume", Mismatch)
    else:
        marker = {"schema": SCHEMA_MARKER, "store_id": secrets.token_hex(16), "volume_uuid": ident["volume_uuid"],
                  "role": role, "created_epoch_s": time.time()}
        write_atomic(marker_path, canonical(marker))
    binding = {"schema": SCHEMA_BINDING, "store_root": str(store_root), "mount_point": str(mount),
               "volume_uuid": ident["volume_uuid"], "volume_name": ident.get("volume_name"),
               "store_id": marker["store_id"], "role": marker.get("role", role), "min_free_gib": float(min_free_gib),
               "allow_noowners": bool(allow_noowners)}
    binding_path = plain_path(binding_path)
    if os.path.lexists(binding_path):
        old = read_json(binding_path)
        if old != binding:
            require(rebind or all(old.get(k) == binding[k] for k in ("store_root", "volume_uuid", "store_id")),
                    "store_binding_differs: pass --rebind to replace it")
    if not os.path.lexists(binding_path) or read_json(binding_path) != binding:
        write_atomic(binding_path, canonical(binding))
    return binding


# -- Air side: the SSH gate -------------------------------------------------------------------

class Gate:
    """Everything the MBP's restricted key can do, confined to the bound store on the Air SSD."""
    FULL = frozenset({"hello", "stat", "verify", "receipts"})  # re-probe the volume UUID (diskutil)
    WRITE = frozenset({"put", "commit", "verify"})             # need the free floor

    def __init__(self, binding_path, *, extract=True, now=time.time, probe=None):
        self.store = Store(binding_path, probe)
        self.root, self.extract, self.now = self.store.root, extract, now

    def _ready(self, verb):
        self.store.check(full=verb in self.FULL, write=verb in self.WRITE)
        for name in ("inbox", "windows", "queue", "locks"):
            make_dir(self.root / name)

    def _wdir(self, kind: str, window_id: str) -> Path:
        return make_dir(self.root / kind / valid_window(window_id))

    def _name(self, name: str) -> str:
        require(name in (MANIFEST_NAME, RECORD_MANIFEST_NAME) or name in EXTRA_NAMES or PART_NAME.match(name) is not None,
                "bad_name")
        return name

    def dispatch(self, command: str, stdin) -> dict:
        try:
            argv = shlex.split(command)
        except ValueError:
            raise Refusal("unparsable_command") from None
        require(argv, "empty_command")
        verb, rest = argv[0], argv[1:]
        table = {"hello": (0, self.hello), "stat": (1, self.stat), "put": (4, self.put),
                 "commit": (4, self.commit), "verify": (1, self.verify), "receipts": (2, self.receipts)}
        require(verb in table and len(rest) == table[verb][0], "verb_not_allowed")
        if rest:
            valid_window(rest[0])
        self._ready(verb)
        if verb == "put":
            return self.put(*rest, stdin=stdin)
        return table[verb][1](*rest)

    def hello(self):
        return {"gate_version": GATE_VERSION, "free_bytes": free_bytes(self.root), "floor_bytes": self.store.floor_bytes,
                "extract": self.extract, "volume_uuid": self.store.doc["volume_uuid"],
                "store_id": self.store.doc["store_id"], "zstd": bool(zstd_cli() or stdlib_zstd())}

    def stat(self, window_id):
        inbox = self.root / "inbox" / valid_window(window_id)
        files = {}
        if inbox.is_dir() and not inbox.is_symlink():
            for entry in os.scandir(inbox):
                if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                    continue
                base, partial = (entry.name[:-8], True) if entry.name.endswith(".partial") else (entry.name, False)
                if base in (MANIFEST_NAME, RECORD_MANIFEST_NAME) or base in EXTRA_NAMES or PART_NAME.match(base):
                    files.setdefault(base, {})["partial" if partial else "final"] = entry.stat(
                        follow_symlinks=False).st_size
        manifest = inbox / MANIFEST_NAME
        receipt = self.root / "windows" / window_id / AIR_RECEIPT
        return {"files": files,
                "manifest_sha256": hash_file(manifest)[0] if manifest.is_file() and not manifest.is_symlink() else None,
                "receipt_manifest_sha256": read_json(receipt)["offload_manifest_sha256"] if receipt.is_file() else None}

    def put(self, window_id, name, offset, length, *, stdin):
        inbox, name = self._wdir("inbox", window_id), self._name(name)
        try:
            offset, length = int(offset), int(length)
        except ValueError:
            raise Refusal("bad_range") from None
        require(offset >= 0 and length >= 0, "bad_range")
        require(not os.path.lexists(inbox / name), "already_committed")
        require(free_bytes(self.root) - length >= self.store.floor_bytes, "store_below_free_floor")
        partial = inbox / (name + ".partial")
        fd = os.open(partial, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o644)
        with os.fdopen(fd, "r+b") as out:
            require(os.fstat(out.fileno()).st_size == offset, "offset_not_append", Mismatch)
            out.seek(offset)
            left = length
            while left:
                chunk = stdin.read(min(CHUNK, left))
                if not chunk:
                    break
                out.write(chunk)
                left -= len(chunk)
            out.flush()
            os.fsync(out.fileno())
        require(left == 0, "short_stdin", TransportError)
        return {"partial": offset + length}

    def commit(self, window_id, name, size, digest):
        inbox, name = self._wdir("inbox", window_id), self._name(name)
        partial = inbox / (name + ".partial")
        require(os.path.lexists(partial) and not partial.is_symlink(), "no_partial")
        got, got_size = hash_file(partial)
        if got != digest or str(got_size) != size:
            os.unlink(partial)  # restart this file from zero next time
            raise Mismatch(f"commit_digest_mismatch:{name}")
        os.replace(partial, inbox / name)
        fsync_dir(inbox)
        return {"committed": name}

    @contextlib.contextmanager
    def _lock(self, window_id):
        fd = os.open(self.root / "locks" / (valid_window(window_id) + ".lock"),
                     os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o644)
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise Refusal("air_window_busy") from None
            yield
        finally:
            os.close(fd)

    def verify(self, window_id):
        with self._lock(window_id):
            wdir, inbox = self._wdir("windows", window_id), self.root / "inbox" / window_id
            receipt_path = wdir / AIR_RECEIPT
            manifest_raw = (inbox / MANIFEST_NAME).read_bytes()
            msha = sha_bytes(manifest_raw)
            if receipt_path.exists():
                receipt = read_json(receipt_path)
                require(receipt["offload_manifest_sha256"] == msha, "window_id_conflict_on_air", Mismatch)
                return receipt
            manifest = json.loads(manifest_raw)
            require(manifest.get("schema") == SCHEMA_MANIFEST and manifest.get("window_id") == window_id,
                    "manifest_schema_or_window", Mismatch)
            require(hash_file(inbox / RECORD_MANIFEST_NAME)[0] == manifest["record_manifest_sha256"],
                    "record_manifest_digest", Mismatch)
            files = {row["path"]: row for row in manifest["files"]}
            links = {row["path"]: row for row in manifest["links"]}
            dirs = {row["path"]: row for row in manifest["dirs"]}
            externals = {row["member"]: row for row in manifest.get("externals", [])}
            for part in manifest["parts"]:
                got, size = hash_file(inbox / part["name"])
                require(got == part["sha256"] and size == part["bytes"], f"part_digest:{part['name']}", Mismatch)
            for extra in manifest.get("extra_objects", []):
                require(hash_file(inbox / self._name(extra["name"])) == (extra["sha256"], extra["bytes"]),
                        f"extra_digest:{extra['name']}", Mismatch)
            harvest = manifest.get("pack_format") == SCHEMA_HARVEST_PACK
            if harvest:
                self._check_harvest_binding(inbox, manifest, files, links, dirs, externals)
            # A v4 session's raw tree is the harvest restore (at the session's own path); here it is verify-only.
            extract = self.extract and not harvest
            staging = wdir / "raw.staging"
            for stale in (staging, wdir / "raw"):  # an interrupted verify leaves no receipt: redo
                if os.path.lexists(stale):
                    require(not stale.is_symlink(), "symlink_staging", Mismatch)
                    shutil.rmtree(stale)
            staging.mkdir()
            seen = set()
            for part in manifest["parts"]:
                with decompressed(manifest["codec"], inbox / part["name"]) as stream:
                    with tarfile.open(fileobj=stream, mode="r|") as tar:
                        for member in tar:
                            name = member.name
                            require(name not in seen, f"duplicate_member:{name}", Mismatch)
                            seen.add(name)
                            if member.isreg() and name in externals:  # a bound closure input (the ledger)
                                row = externals[name]
                                self._check_member(tar, member, {"path": name, "sha256": row["sha256"],
                                                                 "size": row["size"]}, staging, False)
                            elif member.isreg():
                                row = files.get(name)
                                require(row is not None and row["part"] == part["name"], f"unexpected_member:{name}",
                                        Mismatch)
                                self._check_member(tar, member, row, staging, extract)
                            elif member.issym():
                                row = links.get(name)
                                require(row is not None and row["part"] == part["name"]
                                        and member.linkname == row["target"], f"unexpected_link:{name}", Mismatch)
                                if extract:
                                    fd, leaf = parent_fd(staging, name, make_dirs=True)
                                    try:
                                        os.symlink(row["target"], leaf, dir_fd=fd)
                                    finally:
                                        os.close(fd)
                            elif member.isdir():
                                require(name in dirs and dirs[name]["part"] == part["name"], f"unexpected_dir:{name}",
                                        Mismatch)
                                if extract:
                                    fd, leaf = parent_fd(staging, name, make_dirs=True)
                                    try:
                                        with contextlib.suppress(FileExistsError):
                                            os.mkdir(leaf, 0o755, dir_fd=fd)
                                        require(stat.S_ISDIR(os.stat(leaf, dir_fd=fd, follow_symlinks=False).st_mode),
                                                f"dir_member_not_dir:{name}", Mismatch)
                                    finally:
                                        os.close(fd)
                            else:
                                raise Mismatch(f"unexpected_member_type:{name}")
            require(seen == set(files) | set(links) | set(dirs) | set(externals), "missing_members", Mismatch)
            if extract:
                os.replace(staging, wdir / "raw")
            else:
                shutil.rmtree(staging)
            body = {"schema": SCHEMA_AIR, "window_id": window_id, "offload_manifest_sha256": msha,
                    "record_manifest_sha256": manifest["record_manifest_sha256"],
                    "files_verified": len(files), "links_verified": len(links), "dirs_verified": len(dirs),
                    "externals_verified": len(externals), "extra_objects": manifest.get("extra_objects", []),
                    "pack_format": manifest.get("pack_format", "offload_window.v2"),
                    "raw_bytes": sum(r["size"] for r in files.values()),
                    "parts": [{"name": p["name"], "sha256": p["sha256"], "bytes": p["bytes"]}
                              for p in manifest["parts"]],
                    "store_volume_uuid": self.store.doc["volume_uuid"], "store_id": self.store.doc["store_id"],
                    "extracted": extract, "verified_epoch_s": self.now(), "host": socket.gethostname()}
            receipt = sealed(body)
            write_atomic(receipt_path, canonical(receipt))
            write_atomic(self.root / "queue" / (window_id + ".json"),
                         canonical({"window_id": window_id, "offload_manifest_sha256": msha}))
            return receipt

    def _check_harvest_binding(self, inbox, manifest, files, links, dirs, externals):
        """Independent of the MBP's offload manifest: the pinned finalize manifest and the harvest transport
        manifest must describe exactly the rows this verify checks every member against."""
        env = parse_record_manifest((inbox / RECORD_MANIFEST_NAME).read_bytes(), Path(manifest["record_root"]))
        require(env.fmt == "finalized_manifest.v2"
                and {k: (v["sha256"], v["size"]) for k, v in env.files.items()}
                == {k: (r["sha256"], r["size"]) for k, r in files.items()}
                and env.links == {k: r["target"] for k, r in links.items()} and env.dirs == set(dirs),
                "offload_manifest_differs_from_finalize", Mismatch)
        hdoc = json.loads((inbox / HARVEST_MANIFEST).read_bytes())
        require(isinstance(hdoc, dict) and hdoc.get("schema") == SCHEMA_HARVEST_PACK
                and hdoc.get("finalized_manifest_sha256") == manifest["record_manifest_sha256"]
                and hdoc.get("source_root") == manifest["record_root"]
                and harvest_entries(hdoc.get("entries")) == env.doc["entries"]
                and (hdoc.get("payload") or {}).get("sha256") == manifest["parts"][0]["sha256"]
                and {m: (r.get("path"), r.get("sha256"), r.get("size")) for m, r in (hdoc.get("external") or {}).items()}
                == {m: (r["path"], r["sha256"], r["size"]) for m, r in externals.items()}
                and all(env.closure_inputs.get(r["path"]) == {"sha256": r["sha256"], "size": r["size"]}
                        for r in externals.values()),
                "harvest_manifest_differs_from_finalize", Mismatch)
        require(not restore_gaps(env, list(externals.values())), "harvest_pack_not_restorable", Mismatch)

    def _check_member(self, tar, member, row, staging: Path, extract: bool):
        source = tar.extractfile(member)
        digest, size = hashlib.sha256(), 0
        out = None
        if extract:
            fd = open_nofollow(staging, row["path"], os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644, make_dirs=True)
            out = os.fdopen(fd, "wb")
        try:
            for chunk in iter(lambda: source.read(CHUNK), b""):
                digest.update(chunk)
                size += len(chunk)
                if out is not None:
                    out.write(chunk)
        finally:
            if out is not None:
                out.close()
        require(size == row["size"] and digest.hexdigest() == row["sha256"], f"raw_digest:{row['path']}", Mismatch)

    def receipts(self, window_id, nonce):
        """Sealed receipts plus a FRESH recheck (agreement item 4): re-hash the custody objects (the
        compressed parts and both manifests) and re-read the sealed second-copy receipt, for this nonce.
        The raw tree is a derived convenience and is not re-hashed."""
        require(NONCE.match(nonce or "") is not None, "bad_nonce")
        wdir = self.root / "windows" / valid_window(window_id)

        def load(path):
            return read_json(path) if path.is_file() and not path.is_symlink() else None
        air = load(wdir / AIR_RECEIPT)
        second = load(self.root / "second" / window_id / SECOND_RECEIPT)
        if air is None:
            return {"air": None, "second": second, "fresh": None}
        body = check_sealed(air)
        if second is not None:
            check_sealed(second)
        inbox = self.root / "inbox" / window_id
        rechecked = []
        expected = {p["name"]: (p["sha256"], p["bytes"]) for p in body["parts"]}
        expected.update({x["name"]: (x["sha256"], x["bytes"]) for x in body.get("extra_objects", [])})
        for name in sorted([*expected, MANIFEST_NAME, RECORD_MANIFEST_NAME]):
            got, size = hash_file(inbox / name, nocache=True)
            if name in expected:
                require((got, size) == expected[name], f"air_part_decayed:{name}", Mismatch)
            elif name == MANIFEST_NAME:
                require(got == body["offload_manifest_sha256"], "air_manifest_decayed", Mismatch)
            else:
                require(got == body["record_manifest_sha256"], "air_record_manifest_decayed", Mismatch)
            rechecked.append({"name": name, "sha256": got, "bytes": size})
        fresh = sealed({"schema": SCHEMA_FRESH, "window_id": window_id, "nonce": nonce,
                        "offload_manifest_sha256": body["offload_manifest_sha256"],
                        "air_receipt_sha256": air["receipt_sha256"],
                        "second_receipt_sha256": None if second is None else second["receipt_sha256"],
                        "rechecked": rechecked, "checked_epoch_s": self.now(), "host": socket.gethostname()})
        return {"air": air, "second": second, "fresh": fresh}


def gate_main(binding, extract: bool, command: str, stdin, stdout, *, probe=None) -> int:
    try:
        reply, rc = Gate(binding, extract=extract, probe=probe).dispatch(command, stdin), 0
    except Refusal as exc:
        reply = {"error": str(exc), "kind": "mismatch" if isinstance(exc, Mismatch) else "refusal"}
        rc = exc.code
    except tarfile.TarError as exc:  # a digest-checked part that is not a valid archive
        reply, rc = {"error": f"tar:{exc}", "kind": "mismatch"}, Mismatch.code
    except (OSError, ValueError, KeyError) as exc:
        reply, rc = {"error": f"{type(exc).__name__}:{exc}", "kind": "error"}, 1
    stdout.write(canonical(reply))
    stdout.flush()
    return rc


# -- Air side: second copy (agreement item 9) -------------------------------------------------

def _pending_second(store: Store):
    """Windows the gate queued whose sealed second-copy receipt does not exist yet."""
    second = store.root / "second"
    require(second.is_dir() and not second.is_symlink(), "second_dir_missing")
    for entry in sorted((store.root / "queue").glob("*.json")):
        job = read_json(entry)
        window_id = valid_window(job["window_id"])
        if os.path.lexists(second / window_id / SECOND_RECEIPT):
            continue
        air = check_sealed(read_json(store.root / "windows" / window_id / AIR_RECEIPT))
        require(air["offload_manifest_sha256"] == job["offload_manifest_sha256"], "queue_receipt_mismatch", Mismatch)
        yield window_id, air


def _custody_names(air: dict) -> list[str]:
    return sorted([MANIFEST_NAME, RECORD_MANIFEST_NAME] + [p["name"] for p in air["parts"]]
                  + [x["name"] for x in air.get("extra_objects", [])])


def _write_second_receipt(store: Store, window_id: str, body: dict):
    target = make_dir(store.root / "second" / window_id)
    write_atomic(target / SECOND_RECEIPT, canonical(sealed(body)))


@contextlib.contextmanager
def _worker_lock(store: Store, name: str):
    fd = os.open(store.root / "second" / f".{name}.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o644)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False  # another worker interval is still running
            return
        yield True
    finally:
        os.close(fd)


class CloudOps:
    """Real iCloud Drive operations; tests inject a fake."""

    def evict(self, path: Path):
        subprocess.run(["/usr/bin/brctl", "evict", str(path)], check=True, capture_output=True, timeout=120)

    def download(self, path: Path):
        subprocess.run(["/usr/bin/brctl", "download", str(path)], check=True, capture_output=True, timeout=120)

    def is_dataless(self, path: Path) -> bool:
        return bool(getattr(os.lstat(path), "st_flags", 0) & DATALESS)

    def sleep(self, seconds: float):
        time.sleep(seconds)


def second_copy_icloud(binding, cloud_dir: Path, *, cloud=None, probe=None, now=time.time, wait_s=1800,
                       poll_s=10, internal_min_free_gib=15.0) -> list:
    """Copy each queued window's custody objects to iCloud Drive, then prove the server holds them:
    evict each file to a dataless placeholder, download it again, and match the sha256. The local
    iCloud copy is evicted afterwards: the Air's internal disk keeps no copy."""
    store = Store(binding, probe).check(full=True)
    cloud, done = cloud or CloudOps(), []
    cloud_dir = plain_path(cloud_dir)
    cloud_dir.mkdir(parents=True, exist_ok=True)
    errors = store.root / "second" / "errors.jsonl"
    with _worker_lock(store, "icloud") as locked:
        if not locked:
            return done
        for window_id, air in _pending_second(store):
            inbox, target = store.root / "inbox" / window_id, make_dir(cloud_dir / window_id)
            rows = []
            try:
                names = _custody_names(air)
                need = sum((inbox / n).stat().st_size for n in names if not os.path.lexists(target / n))
                require(free_bytes(cloud_dir) - need >= internal_min_free_gib * (1 << 30), "internal_disk_floor")
                for name in names:
                    expected, size = hash_file(inbox / name)
                    dest = target / name
                    if not os.path.lexists(dest):
                        tmp = target / (name + ".copying")
                        shutil.copyfile(inbox / name, tmp, follow_symlinks=False)
                        os.replace(tmp, dest)
                    for action, want in ((cloud.evict, True), (cloud.download, False)):
                        deadline = now() + wait_s
                        while True:
                            with contextlib.suppress(subprocess.CalledProcessError):
                                action(dest)
                            if cloud.is_dataless(dest) == want:
                                break
                            require(now() < deadline, f"cloud_{'evict' if want else 'download'}_timeout:{name}")
                            cloud.sleep(poll_s)
                    got, got_size = hash_file(dest)
                    require(got == expected and got_size == size, f"cloud_roundtrip_digest:{name}", Mismatch)
                    rows.append({"name": name, "sha256": got, "bytes": got_size})
                    with contextlib.suppress(subprocess.CalledProcessError, OSError):
                        cloud.evict(dest)
            except Refusal as exc:
                append_jsonl(errors, {"t": now(), "window_id": window_id, "error": str(exc)})
                if isinstance(exc, Mismatch):
                    raise
                continue  # stays pending; the next interval retries
            _write_second_receipt(store, window_id, {
                "schema": SCHEMA_SECOND, "window_id": window_id, "offload_manifest_sha256": air["offload_manifest_sha256"],
                "confirmed": True, "method": "icloud_evict_download_roundtrip", "location": str(target),
                "primary_volume_uuid": store.doc["volume_uuid"], "files": rows, "confirmed_epoch_s": now()})
            done.append(window_id)
    return done


def _copy_nocache(src: Path, dest: Path):
    """Copy without leaving the bytes in the page cache, so the re-read below comes from the disk."""
    sfd = os.open(src, os.O_RDONLY | os.O_NOFOLLOW)
    dfd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    try:
        for fd in (sfd, dfd):
            if hasattr(fcntl, "F_NOCACHE"):
                with contextlib.suppress(OSError):
                    fcntl.fcntl(fd, fcntl.F_NOCACHE, 1)
        while True:
            chunk = os.read(sfd, 4 * CHUNK)
            if not chunk:
                break
            view = memoryview(chunk)
            while view:
                view = view[os.write(dfd, view):]
        os.fsync(dfd)
    finally:
        os.close(sfd)
        os.close(dfd)


def second_copy_disk(binding, second_binding, *, probe=None, now=time.time) -> list:
    """Allowed alternative to iCloud: a verified copy on a PHYSICALLY independent, bound disk
    (different volume UUID and no shared APFS physical store, probed live)."""
    probe = probe or VolumeProbe()
    primary = Store(binding, probe).check(full=True)
    second = Store(second_binding, probe).check(full=True, write=True)
    require(second.doc.get("role") == "second", "second_store_role")
    p_id, s_id = probe.identity(primary.mount), probe.identity(second.mount)
    require(p_id["volume_uuid"] != s_id["volume_uuid"]
            and not set(p_id["physical_stores"]) & set(s_id["physical_stores"]), "second_disk_not_physically_independent")
    done = []
    with _worker_lock(primary, "second-disk") as locked:
        if not locked:
            return done
        for window_id, air in _pending_second(primary):
            inbox = primary.root / "inbox" / window_id
            target = make_dir(make_dir(second.root / "windows") / window_id)
            rows = []
            for name in _custody_names(air):
                expected, size = hash_file(inbox / name)
                dest = target / name
                if not os.path.lexists(dest):
                    tmp = target / (name + ".copying")
                    with contextlib.suppress(FileNotFoundError):
                        os.unlink(tmp)
                    _copy_nocache(inbox / name, tmp)
                    os.replace(tmp, dest)
                    fsync_dir(target)
                got, got_size = hash_file(dest, nocache=True)
                require(got == expected and got_size == size, f"second_disk_digest:{name}", Mismatch)
                rows.append({"name": name, "sha256": got, "bytes": got_size})
            _write_second_receipt(primary, window_id, {
                "schema": SCHEMA_SECOND, "window_id": window_id, "offload_manifest_sha256": air["offload_manifest_sha256"],
                "confirmed": True, "method": "second_disk_verified_copy", "location": str(target),
                "primary_volume_uuid": primary.doc["volume_uuid"], "second_volume_uuid": second.doc["volume_uuid"],
                "second_physical_stores": s_id["physical_stores"], "files": rows, "confirmed_epoch_s": now()})
            done.append(window_id)
    return done


# -- CLI ------------------------------------------------------------------------------------------

def _lease_from_args(args, record_sha):
    given = [args.lease, args.watchdog_state, args.loop_lock]
    if not any(given):
        return None
    require(all(given), "lease_needs_lease_watchdog_and_loop_lock")
    require(record_sha is not None, "lease_needs_record_manifest_sha256")
    return Lease(args.lease, args.watchdog_state, args.loop_lock, record_sha, margin_s=args.lease_margin_s)


def _transport(args):
    if args.air_local_binding is not None:
        return local_gate_runner(args.air_local_binding)
    return ssh_runner(args.air_host, args.ssh_key, args.known_hosts)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    def mbp(name):
        p = sub.add_parser(name)
        p.add_argument("--state-root", type=Path, required=True)
        p.add_argument("--window-id", required=True)
        p.add_argument("--air-host", default="jw-offload@Edrs-MacBook-Air.local")
        p.add_argument("--ssh-key", type=Path, default=Path.home() / ".ssh/jw_offload_ed25519")
        p.add_argument("--known-hosts", type=Path, default=Path.home() / ".ssh/jw_offload_known_hosts")
        p.add_argument("--air-local-binding", type=Path, help="testing only: run the gate locally, no ssh")
        p.add_argument("--armed-marker", action="append", default=[], type=Path)
        p.add_argument("--lease", type=Path, help="magistrate cool-down lease (joulewise.air_offload_gate.v1)")
        p.add_argument("--watchdog-state", type=Path, help="magistrate watchdog state (fenced_checkouts)")
        p.add_argument("--loop-lock", type=Path, help="the magistrate's persistent loop lock file")
        p.add_argument("--lease-margin-s", type=float, default=120.0)
        return p

    run = mbp("run")
    run.add_argument("--record-root", type=Path, required=True)
    run.add_argument("--record-manifest", type=Path, required=True)
    run.add_argument("--record-manifest-sha256", required=True)
    term = run.add_mutually_exclusive_group(required=True)
    term.add_argument("--terminal", help="record-relative result.json (e.g. night/result.json), or an absolute "
                                         "path bound as an input of the finalized_manifest.v2 closure")
    term.add_argument("--no-terminal-check", dest="terminal", action="store_const", const=None,
                      help=f"synthetic windows only (ids starting {NO_TERMINAL_PREFIXES})")
    mode = run.add_mutually_exclusive_group(required=True)
    mode.add_argument("--harvest-pack", type=Path,
                      help="finalized_manifest.v2 records: the harvest-off lane's pack directory "
                           "(payload.tar.zst + MANIFEST.json), consumed as is, never repacked")
    mode.add_argument("--pack", action="store_true", help="fallback for R1 and legacy manifests: pack here")
    run.add_argument("--duplicate-root", action="append", default=[], type=Path)
    run.add_argument("--codec", choices=("auto", "zstd-cli", "zstd-stdlib", "gzip"), default="auto")
    run.add_argument("--level", type=int, default=3)
    run.add_argument("--threads", type=int, default=4)
    run.add_argument("--part-mib", type=int, default=2048)
    run.add_argument("--hash-on-mbp", action="store_true", help="also hash raw files on the MBP (more heat)")
    run.add_argument("--deadline-epoch", type=float, help="latest end of all offload activity (dwell start - margin)")
    run.add_argument("--budget-s", type=float, default=600.0, help="used when --deadline-epoch is absent")
    run.add_argument("--safety", type=float, default=1.5, help="predicted time x safety must fit the budget")
    run.add_argument("--rates-seed", type=Path, default=RATES_SEED)
    run.add_argument("--no-release-older", dest="release_older", action="store_false")
    run.add_argument("--min-free-gib", type=float, default=60.0)
    run.add_argument("--pressure-compressed-local", action="store_true",
                     help="below --min-free-gib, drop raw files of Air-verified windows, keeping local parts")
    rel = mbp("release")
    rel.add_argument("--pressure-compressed-local", action="store_true")
    rel.add_argument("--min-free-gib", type=float, default=60.0)
    rel.add_argument("--deadline-epoch", type=float, help="latest end of all release activity (dwell start - margin)")
    rel.add_argument("--budget-s", type=float, default=600.0, help="used when --deadline-epoch is absent")
    rel.add_argument("--safety", type=float, default=1.5)
    rel.add_argument("--rates-seed", type=Path, default=RATES_SEED)
    rel.add_argument("--record-manifest-sha256", help="needed with --lease (the lease names the current record)")
    tri = sub.add_parser("triage")
    tri.add_argument("--state-root", type=Path, required=True)
    tri.add_argument("--window-id", required=True)
    tri.add_argument("--dwell-start-epoch", type=float, required=True)
    tri.add_argument("--margin-s", type=float, default=120.0)
    init = sub.add_parser("init-store", help="Air: bind the store directory to its APFS volume (once)")
    init.add_argument("--store-root", type=Path, default=DEFAULT_STORE_ROOT)
    init.add_argument("--binding", type=Path, default=DEFAULT_BINDING)
    init.add_argument("--role", choices=("primary", "second"), default="primary")
    init.add_argument("--min-free-gib", type=float, default=100.0)
    init.add_argument("--allow-noowners", action="store_true", help="testing only: volume ignores ownership")
    init.add_argument("--rebind", action="store_true")
    gate = sub.add_parser("air-gate", help="SSH forced command on the Air")
    gate.add_argument("--binding", type=Path, default=DEFAULT_BINDING)
    gate.add_argument("--no-extract", dest="extract", action="store_false")
    cloud = sub.add_parser("air-icloud", help="second-copy worker on the Air (LaunchAgent, as the iCloud user)")
    cloud.add_argument("--binding", type=Path, default=DEFAULT_BINDING)
    cloud.add_argument("--cloud-dir", type=Path,
                       default=Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/JouleWise-offload")
    cloud.add_argument("--internal-min-free-gib", type=float, default=15.0)
    disk = sub.add_parser("air-second-disk", help="alternative second copy on a physically independent disk")
    disk.add_argument("--binding", type=Path, default=DEFAULT_BINDING)
    disk.add_argument("--second-binding", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        if args.command == "air-gate":
            return gate_main(args.binding, args.extract, os.environ.get("SSH_ORIGINAL_COMMAND", ""),
                             sys.stdin.buffer, sys.stdout.buffer)
        if args.command == "init-store":
            print(json.dumps(init_store(args.store_root, args.binding, role=args.role, min_free_gib=args.min_free_gib,
                                        allow_noowners=args.allow_noowners, rebind=args.rebind), sort_keys=True))
            return 0
        if args.command == "air-icloud":
            print(json.dumps({"confirmed": second_copy_icloud(args.binding, args.cloud_dir,
                                                              internal_min_free_gib=args.internal_min_free_gib)}))
            return 0
        if args.command == "air-second-disk":
            print(json.dumps({"confirmed": second_copy_disk(args.binding, args.second_binding)}))
            return 0
        if args.command == "triage":
            report = triage(args.state_root, args.window_id, args.dwell_start_epoch, args.margin_s)
            print(json.dumps(report, sort_keys=True))
            return 0 if report["quiet_start_state_ok"] else 2
        runner = _transport(args)
        probe = default_state_probe(markers=args.armed_marker)
        lease = _lease_from_args(args, args.record_manifest_sha256)
        if args.command == "run":
            return run_offload(args, runner=runner, state_probe=probe, lease=lease)
        return run_release(args, runner=runner, state_probe=probe, lease=lease)
    except Refusal as exc:
        print(json.dumps({"outcome": type(exc).__name__, "reason": str(exc)}))
        return exc.code


if __name__ == "__main__":
    raise SystemExit(main())
