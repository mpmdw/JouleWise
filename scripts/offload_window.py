#!/usr/bin/env python3
"""Offload one closed measurement-window record from the MBP to the Air's SSD.

Design: docs/ops/AIR-OFFLOAD-opus.md. Standard library only (Python >= 3.11).

MBP side (runs right after finalize, at the START of cool-down):
  run       pack -> push -> Air verify -> release older windows, inside a deadline
  pack      compress the closed record into tar parts (zstd CLI, stdlib zstd, or gzip)
  push      send parts to the Air through the restricted SSH gate (resumable)
  verify    ask the Air to decompress and check every raw file; store its hashed receipt
  release   delete the MBP copy only after a verified Air receipt AND a confirmed
            second copy (iCloud, server-confirmed by an evict/download round trip)
  triage    evidence for the pre-arm `quiet_start_state` entry (no offload running,
            last offload ended before the dwell)
Air side:
  air-gate  the SSH forced command; the only thing the MBP's key can run
  air-icloud the background second-copy worker (LaunchAgent)

Digests come from the record's own manifest (pinned by --record-manifest-sha256).
The MBP does not re-hash raw files by default: the Air checks every raw file against
those digests, end to end. Exit codes: 0 ok, 2 refused, 3 integrity mismatch
(fail closed), 4 deadline (resumable), 5 transport (resumable).
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import socket
import stat
import subprocess
import sys
import tarfile
import time

SCHEMA_PLAN = "joulewise.ops.offload_plan.v1"
SCHEMA_MANIFEST = "joulewise.ops.offload_manifest.v1"
SCHEMA_AIR = "joulewise.ops.offload_air_receipt.v1"
SCHEMA_SECOND = "joulewise.ops.offload_second_copy.v1"
SCHEMA_SPAN = "joulewise.ops.offload_span.v1"
SCHEMA_TRIAGE = "joulewise.ops.offload_triage.v1"
SCHEMA_R1 = "joulewise.align.r1_harvest_manifest.v1"
GATE_VERSION = 1
WINDOW_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
PART_NAME = re.compile(r"part-\d{4}\.tar\.(?:zst|gz)\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
MANIFEST_NAME = "offload-manifest.json"
RECORD_MANIFEST_NAME = "record-manifest.bin"
CHUNK = 1 << 20
DATALESS = 0x40000000  # SF_DATALESS: iCloud placeholder without local bytes
# LaunchAgents whose presence means a window is armed (the magistrate's watchdog is not).
ARMED_PREFIXES = ("com.joulewise.night", "com.joulewise.align-", "com.joulewise.b6")
MEASURING = re.compile(r"(^|[\s/])(powermetrics|run_night\.py|align_v4_session\.py|align_r1_rehearsal\.py|"
                       r"align_r0_checks\.py|run_campaign\.py|mlx_lm)(\s|$|\.)")
DEFAULT_RATES = {"pack_raw_mb_s": 250.0, "push_mb_s": 40.0, "verify_raw_mb_s": 250.0, "ratio": 8.0}


class Refusal(Exception):
    """A precondition failed; nothing unsafe was done."""
    code = 2


class Mismatch(Refusal):
    """Integrity failure: fail closed, delete nothing."""
    code = 3


class DeadlineStop(Refusal):
    """The dwell deadline would be or was reached; state is resumable."""
    code = 4


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
    return path


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
    fd = open_nofollow(root, rel)
    try:
        info = os.fstat(fd)
    finally:
        os.close(fd)
    require(stat.S_ISREG(info.st_mode), f"not_regular:{rel}", Mismatch)
    return info


def hash_file(path: Path) -> tuple[str, int]:
    digest, size = hashlib.sha256(), 0
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


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
                                         stderr=subprocess.PIPE)
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
            self.proc.kill()
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


# -- the record's own manifest ----------------------------------------------------------

def read_record_manifest(path, expected_sha256: str) -> bytes:
    """The record manifest's bytes, authenticated by the sha256 pinned in the committed record."""
    require(isinstance(expected_sha256, str) and HEX64.match(expected_sha256) is not None,
            "record_manifest_sha256_required")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        raw = stream.read()
    require(sha_bytes(raw) == expected_sha256, "record_manifest_sha256_mismatch", Mismatch)
    return raw


def parse_record_manifest(raw: bytes, record_root: Path) -> dict[str, str]:
    """relpath -> sha256 from a supported record manifest; never recomputed here."""
    files: dict[str, str] = {}
    text = raw.decode("utf-8")
    if text.lstrip().startswith("{"):
        doc = json.loads(text)
        if doc.get("schema") == SCHEMA_R1:  # joulewise/align/apple/r1_runtime.py k_harvest
            require(os.path.realpath(doc.get("root", "")) == os.path.realpath(record_root),
                    "record_root_differs_from_manifest_root")
        entries = doc.get("files")
        if isinstance(entries, dict):
            items = list(entries.items())
        elif isinstance(entries, list):
            items = [(row.get("path"), row.get("sha256")) for row in entries if isinstance(row, dict)]
        else:
            raise Refusal("record_manifest_unsupported")
    else:  # sha256sum / SHA256SUMS text: "<hex>  <path>" (binary marker '*' allowed)
        items = []
        for line in text.splitlines():
            if not line.strip():
                continue
            match = re.fullmatch(r"([0-9a-f]{64}) [ *](.+)", line)
            require(match is not None, "record_manifest_line_malformed", Mismatch)
            items.append((match.group(2), match.group(1)))
    for path, digest in items:
        path = safe_relpath(path)
        require(isinstance(digest, str) and HEX64.match(digest) is not None, f"bad_digest:{path}", Mismatch)
        require(path not in files, f"duplicate_manifest_path:{path}", Mismatch)
        files[path] = digest
    require(files, "record_manifest_empty")
    return files


# -- MBP side -----------------------------------------------------------------------------

class Offload:
    """State for one window on the MBP: <state_root>/<window_id>/."""

    def __init__(self, state_root: Path, window_id: str, *, runner=None, now=time.time,
                 deadline_epoch: float | None = None, state_probe=None, log=None):
        self.window_id = valid_window(window_id)
        self.state_root = Path(state_root)
        self.dir = self.state_root / window_id
        self.parts_dir = self.dir / "parts"
        self.runner, self.now, self.deadline = runner, now, deadline_epoch
        self.state_probe = state_probe
        self.log = log or (lambda message: None)

    # -- guards
    def ensure_dirs(self):
        for path in (self.state_root, self.dir, self.parts_dir, self.dir / "timing"):
            require(not os.path.islink(path), f"symlink_state_dir:{path}", Mismatch)
            path.mkdir(mode=0o755, exist_ok=True)

    def check_quiet_allowed(self):
        """Refuse when a window is armed or measuring (re-checked before every stage)."""
        if self.state_probe is None:
            return
        state = self.state_probe()
        require(not state.get("armed"), f"window_armed:{state.get('armed')}")
        require(not state.get("measuring"), f"window_measuring:{state.get('measuring')}")

    def check_deadline(self, need_s: float = 0.0, what: str = ""):
        if self.deadline is not None and self.now() + need_s > self.deadline:
            raise DeadlineStop(f"deadline:{what}")

    def remaining_s(self) -> float | None:
        return None if self.deadline is None else max(0.0, self.deadline - self.now())

    def journal(self, row: dict):
        append_jsonl(self.dir / "offload-journal.jsonl", {"t": self.now(), "window_id": self.window_id, **row})

    # -- pack
    def build_plan(self, record_root: Path, record_manifest: Path, record_manifest_sha256: str,
                   codec: dict, part_bytes: int, duplicate_roots=()) -> dict:
        record_root = Path(os.path.abspath(record_root))
        require(record_root.is_dir() and not record_root.is_symlink(), "record_root_missing_or_symlink")
        raw = read_record_manifest(record_manifest, record_manifest_sha256)
        digests = parse_record_manifest(raw, record_root)
        files, parts, current, current_bytes = [], [], [], 0
        suffix = "zst" if codec["name"] == "zstd" else "gz"
        for rel in sorted(digests):
            info = lstat_rel(record_root, rel)
            if current and current_bytes + info.st_size > part_bytes:
                parts.append(current)
                current, current_bytes = [], 0
            current.append(rel)
            current_bytes += info.st_size
            files.append({"path": rel, "size": info.st_size, "mtime_ns": info.st_mtime_ns,
                          "mode": stat.S_IMODE(info.st_mode), "sha256": digests[rel],
                          "part": f"part-{len(parts):04d}.tar.{suffix}"})
        if current:
            parts.append(current)
        listed = set(digests)
        manifest_rel = None
        with contextlib.suppress(ValueError):
            manifest_rel = Path(os.path.abspath(record_manifest)).relative_to(record_root).as_posix()
        unlisted = []
        for directory, dirs, names in os.walk(record_root, followlinks=False):
            dirs.sort()
            for name in sorted(names):
                rel = (Path(directory) / name).relative_to(record_root).as_posix()
                if rel not in listed and rel != manifest_rel:
                    unlisted.append(rel)
        return {"schema": SCHEMA_PLAN, "window_id": self.window_id, "record_root": str(record_root),
                "record_manifest_sha256": record_manifest_sha256, "codec": codec, "part_bytes": part_bytes,
                "files": files, "raw_bytes": sum(f["size"] for f in files),
                "parts": [{"name": f"part-{i:04d}.tar.{suffix}", "files": len(group),
                           "raw_bytes": sum(f["size"] for f in files if f["part"] == f"part-{i:04d}.tar.{suffix}")}
                          for i, group in enumerate(parts)],
                "unlisted_not_offloaded": unlisted,
                "duplicate_roots": [str(Path(os.path.abspath(p))) for p in duplicate_roots]}

    def pack(self, record_root, record_manifest, record_manifest_sha256, *, codec, part_bytes=2 << 30,
             duplicate_roots=(), hash_on_mbp=False) -> dict:
        self.ensure_dirs()
        manifest_path = self.dir / MANIFEST_NAME
        if os.path.lexists(manifest_path):  # sealed earlier (the raw files may be released by now)
            manifest = read_json(manifest_path)
            require(manifest["record_manifest_sha256"] == record_manifest_sha256
                    and manifest["record_root"] == os.path.abspath(record_root), "duplicate_run_conflict", Mismatch)
            return manifest
        plan = self.build_plan(Path(record_root), Path(record_manifest), record_manifest_sha256, codec,
                               part_bytes, duplicate_roots)
        plan_path = self.dir / "plan.json"
        identity = ("window_id", "record_root", "record_manifest_sha256", "part_bytes", "files", "parts",
                    "duplicate_roots")
        if os.path.lexists(plan_path):
            old = read_json(plan_path)
            # The codec implementation may differ on resume; the content identity may not.
            require(all(old[k] == plan[k] for k in identity) and old["codec"]["name"] == codec["name"],
                    "duplicate_run_conflict", Mismatch)
            plan = old
        else:
            write_once(plan_path, canonical(plan), "duplicate_run_conflict")
        write_once(self.dir / RECORD_MANIFEST_NAME, read_record_manifest(record_manifest, record_manifest_sha256),
                   "record_manifest_changed")
        by_part: dict[str, list[dict]] = {}
        for row in plan["files"]:
            by_part.setdefault(row["part"], []).append(row)
        sealed_parts = []
        for part in plan["parts"]:
            self.check_quiet_allowed()
            sealed_parts.append(self._pack_part(Path(plan["record_root"]), part, by_part[part["name"]],
                                                plan["codec"], hash_on_mbp))
        manifest = {**{k: v for k, v in plan.items() if k != "schema"}, "schema": SCHEMA_MANIFEST,
                    "parts": sealed_parts,
                    "compressed_bytes": sum(p["bytes"] for p in sealed_parts)}
        write_once(manifest_path, canonical(manifest), "duplicate_run_conflict")
        return manifest

    def _pack_part(self, record_root: Path, part: dict, rows: list[dict], codec: dict, hash_on_mbp: bool) -> dict:
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
                for row in rows:
                    fd = open_nofollow(record_root, row["path"])
                    with os.fdopen(fd, "rb") as stream:
                        info = os.fstat(stream.fileno())
                        require(stat.S_ISREG(info.st_mode) and info.st_size == row["size"]
                                and info.st_mtime_ns == row["mtime_ns"], f"record_changed:{row['path']}", Mismatch)
                        member = tarfile.TarInfo(row["path"])
                        member.size, member.mode, member.mtime = row["size"], row["mode"], row["mtime_ns"] / 1e9
                        member.uid = member.gid = 0
                        member.uname = member.gname = ""
                        tar.addfile(member, _GuardedReader(stream, self, row, hash_on_mbp))
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
        need = manifest["compressed_bytes"] + manifest["raw_bytes"] + (2 << 30)
        require(hello.get("free_bytes", 0) >= need, "air_ssd_space")
        uploads = [(RECORD_MANIFEST_NAME, self.dir / RECORD_MANIFEST_NAME)]
        uploads += [(p["name"], self.parts_dir / p["name"]) for p in manifest["parts"]]
        uploads.append((MANIFEST_NAME, self.dir / MANIFEST_NAME))  # last: its arrival marks completeness
        for name, path in uploads:
            self.check_quiet_allowed()
            digest, size = hash_file(path)
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

    def check_air_receipt(self, receipt, manifest: dict):
        body = check_sealed(receipt)
        msha = sha_bytes((self.dir / MANIFEST_NAME).read_bytes())
        require(body.get("schema") == SCHEMA_AIR and body.get("window_id") == self.window_id
                and body.get("offload_manifest_sha256") == msha
                and body.get("record_manifest_sha256") == manifest["record_manifest_sha256"]
                and body.get("files_verified") == len(manifest["files"])
                and body.get("raw_bytes") == manifest["raw_bytes"]
                and body.get("parts") == [{"name": p["name"], "sha256": p["sha256"], "bytes": p["bytes"]}
                                          for p in manifest["parts"]],
                "air_receipt_does_not_match", Mismatch)

    def check_second_receipt(self, receipt, manifest: dict):
        body = check_sealed(receipt)
        msha = sha_bytes((self.dir / MANIFEST_NAME).read_bytes())
        expected = sorted([{"name": p["name"], "sha256": p["sha256"], "bytes": p["bytes"]} for p in manifest["parts"]]
                          + [{"name": MANIFEST_NAME, "sha256": msha,
                              "bytes": (self.dir / MANIFEST_NAME).stat().st_size}],
                          key=lambda r: r["name"])
        require(body.get("schema") == SCHEMA_SECOND and body.get("window_id") == self.window_id
                and body.get("offload_manifest_sha256") == msha and body.get("confirmed") is True
                and body.get("method") == "icloud_evict_download_roundtrip"
                and sorted(body.get("files", []), key=lambda r: r["name"]) == expected,
                "second_copy_receipt_does_not_match", Mismatch)

    # -- release
    def release(self, *, pressure_compressed_local=False) -> dict:
        """Delete the MBP copy only after BOTH verified receipts. Never rmtree."""
        manifest = read_json(self.dir / MANIFEST_NAME)
        if os.path.lexists(self.dir / "released.json"):
            return read_json(self.dir / "released.json")
        self.check_quiet_allowed()
        receipts = self.call(f"receipts {self.window_id}")
        air, second = receipts.get("air"), receipts.get("second")
        require(air is not None, "no_air_receipt")
        self.check_air_receipt(air, manifest)
        write_once(self.dir / "receipt-air.json", canonical(air), "air_receipt_changed")
        if second is None:
            if not pressure_compressed_local:
                raise Refusal("second_copy_not_confirmed")
            if os.path.lexists(self.dir / "raw-released.json"):
                return read_json(self.dir / "raw-released.json")
            # Pressure rule: raw goes, the Air-verified compressed parts stay on the MBP,
            # so two verified copies still exist (MBP parts + Air SSD).
            for part in manifest["parts"]:
                digest, size = hash_file(self.parts_dir / part["name"])
                require(digest == part["sha256"] and size == part["bytes"], f"local_part_corrupt:{part['name']}", Mismatch)
            result = self._delete_raw(manifest, "pressure_compressed_local")
            write_atomic(self.dir / "raw-released.json", canonical(result))
            return result
        self.check_second_receipt(second, manifest)
        write_once(self.dir / "receipt-second.json", canonical(second), "second_receipt_changed")
        result = self._delete_raw(manifest, "two_verified_copies") if not os.path.lexists(
            self.dir / "raw-released.json") else read_json(self.dir / "raw-released.json")
        for part in manifest["parts"]:
            with contextlib.suppress(FileNotFoundError):
                os.unlink(self.parts_dir / part["name"])
        result = {**result, "parts_deleted": True, "rule": "two_verified_copies"}
        write_atomic(self.dir / "released.json", canonical(result))
        self.journal({"event": "released", **{k: result[k] for k in ("files_deleted", "rule")}})
        return result

    def _delete_raw(self, manifest: dict, rule: str) -> dict:
        roots = [Path(manifest["record_root"])] + [Path(p) for p in manifest.get("duplicate_roots", [])]
        deleted, skipped, doomed = 0, [], []
        # Pass 1 checks everything, so a changed record file stops the release before any unlink.
        for index, root in enumerate(roots):
            if not root.is_dir() or root.is_symlink():
                skipped.append({"root": str(root), "reason": "absent_or_symlink"})
                continue
            for row in manifest["files"]:
                try:
                    info = lstat_rel(root, row["path"])
                except FileNotFoundError:
                    continue  # resumed release
                same = info.st_size == row["size"] and (index > 0 or info.st_mtime_ns == row["mtime_ns"])
                if index == 0:
                    require(same, f"record_changed_since_offload:{row['path']}", Mismatch)
                elif not same:
                    skipped.append({"root": str(root), "path": row["path"], "reason": "duplicate_differs"})
                    continue
                doomed.append((root, row["path"]))
        for root, rel in doomed:
            fd, leaf = parent_fd(root, rel)
            try:
                os.unlink(leaf, dir_fd=fd)
            finally:
                os.close(fd)
            deleted += 1
        for root in {root for root, _ in doomed}:
            # Remove only directories that are now empty, deepest first; never rmtree.
            for directory, _, _ in os.walk(root, topdown=False, followlinks=False):
                with contextlib.suppress(OSError):
                    if Path(directory) != root:
                        os.rmdir(directory)
        return {"window_id": self.window_id, "rule": rule, "files_deleted": deleted, "skipped": skipped,
                "released_epoch_s": self.now()}


class _GuardedReader:
    """File reader for tarfile: deadline and armed checks every 64 MiB, optional hashing."""

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


# -- MBP probes and receipts ----------------------------------------------------------------

def default_state_probe(launch_agents=Path.home() / "Library/LaunchAgents", markers=()):
    def probe():
        armed = sorted(p.name for p in launch_agents.iterdir()
                       if p.name.startswith(ARMED_PREFIXES) and p.name.endswith(".plist")) \
            if launch_agents.is_dir() else []
        armed += [str(m) for m in markers if os.path.lexists(m)]
        table = subprocess.run(["/bin/ps", "-axo", "pid=,args="], capture_output=True, text=True).stdout
        mine = os.getpid()
        measuring = [line.strip()[:120] for line in table.splitlines()
                     if MEASURING.search(line) and not line.strip().startswith(f"{mine} ")]
        return {"armed": armed, "measuring": measuring}
    return probe


def ssh_runner(host: str, key: Path, extra=()):
    """The real transport: one ssh call per gate verb; the Air's forced command decides."""
    def run(command, *, stdin_path=None, offset=0, timeout=None):
        argv = ["/usr/bin/ssh", "-i", str(key), "-T", "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes",
                "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=15",
                "-o", "Compression=no", *extra, host, command]
        if stdin_path is None:
            result = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, timeout=timeout)
        else:
            fd = os.open(stdin_path, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(fd, "rb") as stream:
                stream.seek(offset)
                result = subprocess.run(argv, stdin=stream, capture_output=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    return run


def load_rates(state_root: Path) -> dict:
    with contextlib.suppress(OSError, ValueError):
        return {**DEFAULT_RATES, **read_json(state_root / "rates.json")}
    return dict(DEFAULT_RATES)


def predict_s(manifest_or_plan_raw: int, rates: dict, done: dict) -> float:
    raw = manifest_or_plan_raw
    pack = 0 if done.get("packed") else raw / (rates["pack_raw_mb_s"] * 1e6)
    push = 0 if done.get("pushed") else raw / rates["ratio"] / (rates["push_mb_s"] * 1e6)
    verify = 0 if done.get("verified") else raw / (rates["verify_raw_mb_s"] * 1e6)
    return pack + push + verify + 10.0  # ssh handshakes and fsyncs


def run_offload(args, *, runner, state_probe, now=time.time) -> int:
    """The magistrate's one call after finalize. Writes start/end receipts whatever happens."""
    state_root = Path(args.state_root)
    require(not state_root.is_symlink(), "symlink_state_root", Mismatch)
    state_root.mkdir(parents=True, exist_ok=True)
    deadline = args.deadline_epoch if args.deadline_epoch is not None else now() + args.budget_s
    off = Offload(state_root, args.window_id, runner=runner, now=now, deadline_epoch=deadline,
                  state_probe=state_probe)
    lock_fd = os.open(state_root / ".lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o644)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(lock_fd)
        print(json.dumps({"outcome": "refused", "reason": "offload_already_running"}))
        return Refusal.code
    started_epoch, started_mono = now(), time.monotonic_ns()
    span = {"schema": SCHEMA_SPAN, "stage_id": f"offload-{args.window_id}", "kind": "backup",
            "window_id": args.window_id, "started_epoch_s": started_epoch, "started_monotonic_ns": started_mono,
            "deadline_epoch_s": deadline, "stages": []}
    rc, outcome = 0, {}
    try:
        off.check_quiet_allowed()
        off.ensure_dirs()
        timing = off.dir / "timing"
        write_atomic(timing / "offload-start.json", canonical(span))
        rates = load_rates(state_root)
        manifest_path = off.dir / MANIFEST_NAME
        done = {"packed": manifest_path.exists(), "verified": (off.dir / "receipt-air.json").exists()}
        raw_bytes = read_json(manifest_path)["raw_bytes"] if done["packed"] else _raw_size(args)
        predicted = predict_s(raw_bytes, rates, done)
        span["predicted_s"] = round(predicted, 1)
        off.check_deadline(predicted * args.safety, "predicted_overrun")
        older = []
        if args.release_older:
            span["stages"].append(_stage("release_older", now, lambda: older.extend(release_older(
                state_root, args.window_id, runner, now, deadline, state_probe,
                args.pressure_compressed_local and _pressure(args, state_root)))))
        manifest = {}
        span["stages"].append(_stage("pack", now, lambda: manifest.update(off.pack(
            args.record_root, args.record_manifest, args.record_manifest_sha256,
            codec=choose_codec(args.codec, args.level, args.threads), part_bytes=args.part_mib << 20,
            duplicate_roots=args.duplicate_root, hash_on_mbp=args.hash_on_mbp))))
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
                   "compressed_bytes": manifest["compressed_bytes"], "release_held": held,
                   "older": older, "disk_pressure": _pressure(args, state_root)}
        _update_rates(state_root, rates, manifest, span)
        if any("mismatch" in row for row in older):
            rc, outcome["outcome"] = Mismatch.code, "older_window_mismatch"
    except Refusal as exc:
        rc, outcome = exc.code, {"outcome": type(exc).__name__, "reason": str(exc)}
    except OSError as exc:  # e.g. ENOSPC; resumable, but never silent
        rc, outcome = 6, {"outcome": "io_error", "reason": f"{type(exc).__name__}:{exc}"}
    finally:
        span.update(ended_epoch_s=now(), ended_monotonic_ns=time.monotonic_ns(), rc=rc, **outcome,
                    ended_before_deadline=now() <= deadline)
        if off.dir.is_dir() and not off.dir.is_symlink():
            write_atomic(off.dir / "timing" / "offload-span.json", canonical(span))
            off.journal({"event": "run_end", "rc": rc, **outcome})
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)
    print(json.dumps(span, sort_keys=True))
    return rc


def _stage(name, now, action):
    start = now()
    action()
    return {"name": name, "started_epoch_s": start, "ended_epoch_s": now()}


def _raw_size(args) -> int:
    total = 0
    raw = Path(args.record_manifest).read_bytes()
    for rel in parse_record_manifest(raw, Path(args.record_root)):
        total += lstat_rel(Path(args.record_root), rel).st_size
    return total


def _pressure(args, state_root: Path) -> bool:
    return free_bytes(state_root) < args.min_free_gib * (1 << 30)


def _update_rates(state_root: Path, rates: dict, manifest: dict, span: dict):
    by = {s["name"]: s["ended_epoch_s"] - s["started_epoch_s"] for s in span["stages"]}
    new = dict(rates)
    if by.get("pack", 0) > 1 and manifest["parts"] and all("wall_s" in p for p in manifest["parts"]):
        new["pack_raw_mb_s"] = manifest["raw_bytes"] / 1e6 / max(by["pack"], 1e-3)
    if by.get("push", 0) > 1:
        new["push_mb_s"] = manifest["compressed_bytes"] / 1e6 / by["push"]
    if by.get("verify", 0) > 1:
        new["verify_raw_mb_s"] = manifest["raw_bytes"] / 1e6 / by["verify"]
    if manifest["compressed_bytes"]:
        new["ratio"] = manifest["raw_bytes"] / manifest["compressed_bytes"]
    write_atomic(state_root / "rates.json", canonical(new))


def release_older(state_root: Path, current: str, runner, now, deadline, state_probe, pressure_local) -> list:
    results = []
    for directory in sorted(p for p in state_root.iterdir() if p.is_dir() and not p.is_symlink()):
        if directory.name == current or not WINDOW_ID.match(directory.name):
            continue
        if not (directory / MANIFEST_NAME).exists() or (directory / "released.json").exists():
            continue
        off = Offload(state_root, directory.name, runner=runner, now=now, deadline_epoch=deadline,
                      state_probe=state_probe)
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
    return {"schema": SCHEMA_TRIAGE, "window_id": window_id, "quiet_start_state_ok": not reasons,
            "reasons": reasons, "span": span, "dwell_start_epoch_s": dwell_start_epoch, "margin_s": margin_s,
            "air_receipt": (state_root / window_id / "receipt-air.json").exists(),
            "second_copy": (state_root / window_id / "receipt-second.json").exists(),
            "free_bytes": free_bytes(state_root)}


# -- Air side: the SSH gate -------------------------------------------------------------------

class Gate:
    """Everything the MBP's restricted key can do, confined to one directory on the Air SSD."""

    def __init__(self, root: Path, *, extract=True, now=time.time):
        self.root, self.extract, self.now = Path(root), extract, now
        require(self.root.is_dir() and not self.root.is_symlink(), "air_root_missing_or_symlink")
        for name in ("inbox", "windows", "queue", "locks"):
            path = self.root / name
            require(not path.is_symlink(), f"symlink_air_dir:{name}", Mismatch)
            path.mkdir(exist_ok=True)

    def _wdir(self, kind: str, window_id: str) -> Path:
        path = self.root / kind / valid_window(window_id)
        require(not path.is_symlink(), "symlink_window_dir", Mismatch)
        path.mkdir(exist_ok=True)
        return path

    def _name(self, name: str) -> str:
        require(name in (MANIFEST_NAME, RECORD_MANIFEST_NAME) or PART_NAME.match(name) is not None, "bad_name")
        return name

    def dispatch(self, command: str, stdin) -> dict:
        argv = shlex.split(command)
        require(argv, "empty_command")
        verb, rest = argv[0], argv[1:]
        table = {"hello": (0, self.hello), "stat": (1, self.stat), "put": (4, self.put),
                 "commit": (4, self.commit), "verify": (1, self.verify), "receipts": (1, self.receipts)}
        require(verb in table and len(rest) == table[verb][0], "verb_not_allowed")
        if verb == "put":
            return self.put(*rest, stdin=stdin)
        return table[verb][1](*rest)

    def hello(self):
        return {"gate_version": GATE_VERSION, "free_bytes": free_bytes(self.root), "extract": self.extract,
                "zstd": bool(zstd_cli() or stdlib_zstd())}

    def stat(self, window_id):
        inbox = self.root / "inbox" / valid_window(window_id)
        files = {}
        if inbox.is_dir() and not inbox.is_symlink():
            for entry in os.scandir(inbox):
                if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                    continue
                base, partial = (entry.name[:-8], True) if entry.name.endswith(".partial") else (entry.name, False)
                if base in (MANIFEST_NAME, RECORD_MANIFEST_NAME) or PART_NAME.match(base):
                    files.setdefault(base, {})["partial" if partial else "final"] = entry.stat(
                        follow_symlinks=False).st_size
        manifest = inbox / MANIFEST_NAME
        receipt = self.root / "windows" / window_id / "air-receipt.json"
        return {"files": files,
                "manifest_sha256": hash_file(manifest)[0] if manifest.is_file() and not manifest.is_symlink() else None,
                "receipt_manifest_sha256": read_json(receipt)["offload_manifest_sha256"] if receipt.is_file() else None}

    def put(self, window_id, name, offset, length, *, stdin):
        inbox, name = self._wdir("inbox", window_id), self._name(name)
        offset, length = int(offset), int(length)
        require(offset >= 0 and length >= 0, "bad_range")
        require(not os.path.lexists(inbox / name), "already_committed")
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
        if got != digest or got_size != int(size):
            os.unlink(partial)  # restart this file from zero next time
            raise Mismatch(f"commit_digest_mismatch:{name}")
        os.replace(partial, inbox / name)
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
            receipt_path = wdir / "air-receipt.json"
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
            expected = {row["path"]: row for row in manifest["files"]}
            for part in manifest["parts"]:
                got, size = hash_file(inbox / part["name"])
                require(got == part["sha256"] and size == part["bytes"], f"part_digest:{part['name']}", Mismatch)
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
                            row = expected.get(member.name)
                            require(member.isreg() and row is not None and row["part"] == part["name"]
                                    and member.name not in seen, f"unexpected_member:{member.name}", Mismatch)
                            seen.add(member.name)
                            self._check_member(tar, member, row, staging)
            require(seen == set(expected), "missing_members", Mismatch)
            if self.extract:
                os.replace(staging, wdir / "raw")
            else:
                shutil.rmtree(staging)
            body = {"schema": SCHEMA_AIR, "window_id": window_id, "offload_manifest_sha256": msha,
                    "record_manifest_sha256": manifest["record_manifest_sha256"],
                    "files_verified": len(seen), "raw_bytes": sum(r["size"] for r in expected.values()),
                    "parts": [{"name": p["name"], "sha256": p["sha256"], "bytes": p["bytes"]}
                              for p in manifest["parts"]],
                    "extracted": self.extract, "verified_epoch_s": self.now(), "host": socket.gethostname()}
            receipt = sealed(body)
            write_atomic(receipt_path, canonical(receipt))
            write_atomic(self.root / "queue" / (window_id + ".json"),
                         canonical({"window_id": window_id, "offload_manifest_sha256": msha}))
            return receipt

    def _check_member(self, tar, member, row, staging: Path):
        source = tar.extractfile(member)
        digest, size = hashlib.sha256(), 0
        out = None
        if self.extract:
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

    def receipts(self, window_id):
        wdir = self.root / "windows" / valid_window(window_id)
        def load(name):
            path = wdir / name
            return read_json(path) if path.is_file() and not path.is_symlink() else None
        return {"air": load("air-receipt.json"), "second": load("second-copy-receipt.json")}


def gate_main(root: Path, extract: bool, command: str, stdin, stdout) -> int:
    try:
        reply, rc = Gate(root, extract=extract).dispatch(command, stdin), 0
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


# -- Air side: second copy (iCloud, server-confirmed) ---------------------------------------

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


def second_copy(root: Path, cloud_dir: Path, *, cloud=None, now=time.time, wait_s=1800, poll_s=10) -> list:
    """Process queued windows: copy to iCloud Drive, then prove the server holds the bytes by
    evicting each file to a dataless placeholder and re-downloading it with matching sha256."""
    cloud, root, done = cloud or CloudOps(), Path(root), []
    require(not cloud_dir.is_symlink(), "symlink_cloud_dir", Mismatch)
    cloud_dir.mkdir(parents=True, exist_ok=True)
    lock = os.open(root / "locks" / "icloud.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o644)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(lock)
        return done  # another worker interval is still running
    try:
        return _second_copy_jobs(root, cloud_dir, cloud, now, wait_s, poll_s, done)
    finally:
        os.close(lock)


def _second_copy_jobs(root, cloud_dir, cloud, now, wait_s, poll_s, done):
    for entry in sorted((root / "queue").glob("*.json")):
        job = read_json(entry)
        window_id = valid_window(job["window_id"])
        inbox, wdir = root / "inbox" / window_id, root / "windows" / window_id
        air = check_sealed(read_json(wdir / "air-receipt.json"))
        require(air["offload_manifest_sha256"] == job["offload_manifest_sha256"], "queue_receipt_mismatch", Mismatch)
        names = [MANIFEST_NAME] + [p["name"] for p in air["parts"]]
        target = cloud_dir / window_id
        require(not target.is_symlink(), "symlink_cloud_target", Mismatch)
        target.mkdir(exist_ok=True)
        rows = []
        try:
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
                # The Air's internal disk is small: leave the cloud copy as a placeholder.
                with contextlib.suppress(subprocess.CalledProcessError, OSError):
                    cloud.evict(dest)
        except Refusal as exc:
            append_jsonl(root / "queue" / "second-copy-errors.jsonl", {"t": now(), "window_id": window_id,
                                                                        "error": str(exc)})
            if isinstance(exc, Mismatch):
                raise
            continue  # stays queued; the next interval retries
        body = {"schema": SCHEMA_SECOND, "window_id": window_id,
                "offload_manifest_sha256": air["offload_manifest_sha256"], "confirmed": True,
                "method": "icloud_evict_download_roundtrip", "location": str(target),
                "files": sorted(rows, key=lambda r: r["name"]), "confirmed_epoch_s": now()}
        write_atomic(wdir / "second-copy-receipt.json", canonical(sealed(body)))
        os.unlink(entry)
        done.append(window_id)
    return done


# -- CLI ------------------------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    def mbp(name):
        p = sub.add_parser(name)
        p.add_argument("--state-root", type=Path, required=True)
        p.add_argument("--window-id", required=True)
        p.add_argument("--air-host", default="jw-air")
        p.add_argument("--ssh-key", type=Path, default=Path.home() / ".ssh/jw_offload_ed25519")
        p.add_argument("--armed-marker", action="append", default=[], type=Path)
        return p

    run = mbp("run")
    run.add_argument("--record-root", type=Path, required=True)
    run.add_argument("--record-manifest", type=Path, required=True)
    run.add_argument("--record-manifest-sha256", required=True)
    run.add_argument("--duplicate-root", action="append", default=[], type=Path)
    run.add_argument("--codec", choices=("auto", "zstd-cli", "zstd-stdlib", "gzip"), default="auto")
    run.add_argument("--level", type=int, default=3)
    run.add_argument("--threads", type=int, default=4)
    run.add_argument("--part-mib", type=int, default=2048)
    run.add_argument("--hash-on-mbp", action="store_true", help="also hash raw files on the MBP (more heat)")
    run.add_argument("--deadline-epoch", type=float, help="latest end of all offload activity (dwell start - margin)")
    run.add_argument("--budget-s", type=float, default=600.0, help="used when --deadline-epoch is absent")
    run.add_argument("--safety", type=float, default=1.5, help="predicted time x safety must fit the budget")
    run.add_argument("--no-release-older", dest="release_older", action="store_false")
    run.add_argument("--min-free-gib", type=float, default=60.0)
    run.add_argument("--pressure-compressed-local", action="store_true",
                     help="below --min-free-gib, drop raw files of Air-verified windows, keeping local parts")
    rel = mbp("release")
    rel.add_argument("--pressure-compressed-local", action="store_true")
    tri = sub.add_parser("triage")
    tri.add_argument("--state-root", type=Path, required=True)
    tri.add_argument("--window-id", required=True)
    tri.add_argument("--dwell-start-epoch", type=float, required=True)
    tri.add_argument("--margin-s", type=float, default=120.0)
    gate = sub.add_parser("air-gate", help="SSH forced command on the Air")
    gate.add_argument("--root", type=Path, required=True)
    gate.add_argument("--no-extract", dest="extract", action="store_false")
    cloud = sub.add_parser("air-icloud", help="second-copy worker on the Air (LaunchAgent)")
    cloud.add_argument("--root", type=Path, required=True)
    cloud.add_argument("--cloud-dir", type=Path,
                       default=Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/JouleWise-offload")
    args = parser.parse_args(argv)

    if args.command == "air-gate":
        return gate_main(args.root, args.extract, os.environ.get("SSH_ORIGINAL_COMMAND", ""),
                         sys.stdin.buffer, sys.stdout.buffer)
    if args.command == "air-icloud":
        print(json.dumps({"confirmed": second_copy(args.root, args.cloud_dir)}))
        return 0
    if args.command == "triage":
        report = triage(args.state_root, args.window_id, args.dwell_start_epoch, args.margin_s)
        print(json.dumps(report, sort_keys=True))
        return 0 if report["quiet_start_state_ok"] else 2
    runner = ssh_runner(args.air_host, args.ssh_key)
    probe = default_state_probe(markers=args.armed_marker)
    if args.command == "run":
        return run_offload(args, runner=runner, state_probe=probe)
    try:
        result = Offload(args.state_root, args.window_id, runner=runner, state_probe=probe).release(
            pressure_compressed_local=args.pressure_compressed_local)
        print(json.dumps(result, sort_keys=True))
        return 0
    except Refusal as exc:
        print(json.dumps({"outcome": type(exc).__name__, "reason": str(exc)}))
        return exc.code


if __name__ == "__main__":
    raise SystemExit(main())
