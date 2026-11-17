"""Span cloud offload (RL-173 A): bytes only, public-key encrypted, synchronous upload, verified marker.

The measurement Mac (MBP) offloads each closed span's output directory (OUT) to a private cloud folder
and writes the copy marker itself, so it never waits for the Air. The Air later pulls the copy, checks it
against the marker's hashes and decrypts it read-only into its desk tree.

Bytes only (RL-173 A.4): no file under OUT is parsed. Each regular file is read once, as bytes, into the
archive; the plaintext manifest is the sha256 of exactly those bytes. Low-level offload retains OUT;
explicit close applies RL-174 D.2 after verified packing and off-host readback. Nothing is written to
the repository (A.6): the tool has no git step.

Key scheme (documented in ``docs/ops/SPAN-OFFLOAD.md``): per span, a fresh 256-bit passphrase encrypts
the archive (``openssl enc -aes-256-cbc -pbkdf2 -md sha256``) and is wrapped to an RSA (>= 3072-bit)
recipient public key with RSA-OAEP. The MBP holds only the public key, pinned by the sha256 of its DER
encoding; the private key lives off the MBP (the Air's custody root and Ed's vault). The passphrase is
held in memory and passed to openssl over a pipe (``-pass fd:N`` / stdin); it never touches disk or argv.

Uploaded per span, under ``<remote>/<plan>/``:
    <plan>.tgz.enc       the encrypted gzip tar of OUT (top directory = OUT's basename)
    <plan>.key.enc       the wrapped passphrase
    <plan>.SHA256SUMS    the plaintext manifest (``<sha256>  ./<relative path>``, byte order)
    <plan>.offload.json  the descriptor: scheme, recipient fingerprint, and the other three files' hashes

Standard library only, plus ``openssl`` (LibreSSL 3.3 on macOS and OpenSSL 3 both work) and, for the
default iCloud backend, macOS ``brctl``. The optional rclone backend uses ``rclone``.
Exit codes are in ``EXIT``.
"""
from __future__ import annotations

import contextlib
import fcntl
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import subprocess
import tarfile
import tempfile
import threading
import time
import unicodedata
import zlib

DESCRIPTOR_SCHEMA = "joulewise.span_offload.v1"
MARKER_SCHEMA = "joulewise.span_offload_marker.v1"
MBP_CONFIG_SCHEMA = "joulewise.span_offload_config.v1"
AIR_CONFIG_SCHEMA = "joulewise.span_offload_pull_config.v1"

EXIT = {
    "ok": 0,
    "internal": 1,
    "usage": 2,
    "marker_exists": 3,  # nothing was done (or another writer won the marker race)
    "refused": 4,  # input refused before any upload: no marker
    "unverified": 5,  # upload or provider read-back failed: no marker (RL-173 A.7 holds the next arm)
    "integrity": 6,  # pull: a hash or archive check failed; nothing lands in the desk tree
    "dest_exists": 7,  # pull: the destination already exists; nothing changed
    "unconfirmed": 8,  # any transport without observed iCloud readback: no <plan>.ok
}

ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")
HEX64 = re.compile(r"[0-9a-f]{64}")
CIPHER = "aes-256-cbc"
KDF_ITER = 10000
MIN_RSA_BITS = 3072
GZIP_LEVEL = 6
CHUNK = 1 << 20
FILE_SUFFIXES = {"ciphertext": ".tgz.enc", "wrapped_key": ".key.enc", "manifest": ".SHA256SUMS",
                 "descriptor": ".offload.json"}
UPLOAD_ORDER = ("ciphertext", "wrapped_key", "manifest", "descriptor")
SIMPLE_HASHES = ("sha256", "sha1", "md5")


class OffloadError(Exception):
    """``code`` is a fixed upper-case word; ``detail`` never carries file contents."""

    def __init__(self, code: str, detail: str = "", exit_kind: str = "refused"):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail
        self.exit_kind = exit_kind


def refused(code, detail=""):
    return OffloadError(code, detail, "refused")


def unverified(code, detail=""):
    return OffloadError(code, detail, "unverified")


def integrity(code, detail=""):
    return OffloadError(code, detail, "integrity")


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


SPAN_STAMP_RE = re.compile(r"[0-9]{8}T[0-9]{6}Z")
MAX_DEADLINE_AHEAD_S = 86400


def span_name_ok(name, plan):
    """OUT is named ``<plan>`` or ``<plan>-<YYYYMMDDTHHMMSSZ>`` (the runner's naming)."""
    return name == plan or (name.startswith(plan + "-") and SPAN_STAMP_RE.fullmatch(name[len(plan) + 1:]) is not None)


def check_id(value, what):
    if not isinstance(value, str) or not ID_RE.fullmatch(value) or ".." in value or value.endswith((".", ".lock")):
        raise refused("BAD_ID", what)
    return value


def names(plan):
    return {kind: plan + suffix for kind, suffix in FILE_SUFFIXES.items()}


def sha256_file(path, algorithm="sha256"):
    with open(path, "rb") as handle:
        return hashlib.file_digest(handle, algorithm).hexdigest()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def canonical(doc):
    return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode() + b"\n"


_CHILDREN = set()


def kill_children():
    """Kill every openssl stream this process started. A signal handler calls it before unwinding, so no
    unwinding step can wait on a stalled child."""
    for proc in list(_CHILDREN):
        with contextlib.suppress(OSError):
            proc.kill()


class Deadline:
    """Remaining time for subprocess timeouts; ``None`` means no deadline."""

    def __init__(self, epoch=None, clock=time.time):
        self.epoch = epoch
        self.clock = clock

    def remaining(self, cap=None):
        if self.epoch is None:
            return cap
        left = self.epoch - self.clock()
        if left <= 0:
            raise unverified("DEADLINE", "the offload deadline passed")
        return left if cap is None else min(left, cap)


# --- the span walk (bytes only) -------------------------------------------------------------------

def _check_name(name, where):
    try:
        name.encode("utf-8")
    except UnicodeEncodeError:
        raise refused("BAD_NAME", f"a name under {where} is not UTF-8") from None
    if any(c in name for c in "\n\r\\") or name in (".", "..") or not name:
        raise refused("BAD_NAME", f"a name under {where} has a newline, carriage return or backslash")


def walk_span(span_dir):
    """Return (directories, files) relative to ``span_dir``, in byte order, without following links.

    Refuses a symlink, a special file or an unencodable name anywhere under the span.
    """
    span_dir = Path(span_dir)
    try:
        top = os.lstat(span_dir)
    except FileNotFoundError:
        raise refused("SPAN_MISSING", "the span directory does not exist") from None
    if not stat.S_ISDIR(top.st_mode):
        raise refused("SPAN_NOT_DIR", "the span path is a symlink or not a directory")
    dirs, files = [], []
    for root, dirnames, filenames in os.walk(span_dir, followlinks=False, onerror=_walk_error):
        rel_root = Path(root).relative_to(span_dir)
        for name in list(dirnames) + filenames:
            _check_name(name, "the span")
            rel = (rel_root / name).as_posix()
            mode = os.lstat(Path(root) / name).st_mode
            if stat.S_ISLNK(mode):
                raise refused("SPAN_SYMLINK", "the span holds a symlink (not followed, not archived)")
            if stat.S_ISDIR(mode):
                dirs.append(rel)
            elif stat.S_ISREG(mode):
                files.append(rel)
            else:
                raise refused("SPAN_SPECIAL_FILE", "the span holds a socket, fifo or device")
        dirnames.sort()
    key = lambda rel: rel.encode("utf-8")  # noqa: E731
    return sorted(dirs, key=key), sorted(files, key=key)


def _walk_error(error):
    raise refused("SPAN_UNREADABLE", type(error).__name__)


def span_snapshot(span_dir, check=None):
    """Census names and identities before reading ANY payload; ignore read-induced atime only.

    ctime catches writes with restored mtime, inode/device catch replacement, directory metadata
    catches membership changes. Comparing a second census after the last read establishes a common
    stable interval for the whole tree. This assumes a closed source on a local filesystem, not an
    adversary able to forge kernel metadata. The controller must stop all writers before close.
    """
    snapshot = {}

    def visit(rel):
        if check:
            check()
        path = Path(span_dir) / rel
        info = os.lstat(path)  # directory identity BEFORE enumerating its children
        snapshot[rel] = (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
                         info.st_mtime_ns, info.st_ctime_ns)
        if stat.S_ISDIR(info.st_mode):
            with os.scandir(path) as entries:
                children = sorted(entry.name for entry in entries)
            for name in children:
                _check_name(name, "the span")
                visit(name if rel == "." else rel + "/" + name)
        elif not stat.S_ISREG(info.st_mode):
            raise refused("SPAN_SYMLINK" if stat.S_ISLNK(info.st_mode) else "SPAN_SPECIAL_FILE",
                          "the source holds a link or special file")

    visit(".")
    return snapshot


def require_snapshot(span_dir, expected, check=None):
    try:
        current = span_snapshot(span_dir, check)
    except (OSError, OffloadError) as error:
        if isinstance(error, OffloadError) and error.exit_kind != "refused":
            raise
        raise refused("SPAN_CHANGED", "the source tree changed during offload") from None
    if current != expected:
        raise refused("SPAN_CHANGED", "the source names, identities or metadata changed during offload")


def manifest_bytes(digests):
    """``digests`` maps relative path -> sha256 hex. Output matches ``shasum -a 256`` on ``./path``."""
    return "".join(f"{digests[rel]}  ./{rel}\n" for rel in sorted(digests, key=lambda r: r.encode("utf-8"))).encode()


def open_regular(path, what="a file", dir_fd=None, single_link=False):
    """Open a regular file without following a link and without blocking on a fifo; refuse anything else.
    With ``dir_fd`` the name is resolved inside that already-open directory (no parent can be swapped).
    ``single_link`` (every control and stage file) also refuses a hard link: a file with one name cannot be
    an alias of a file under OUT."""
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0), dir_fd=dir_fd)
    except OSError as error:
        raise refused("UNREADABLE", f"{what}: {type(error).__name__}") from None
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode):
        os.close(fd)
        raise refused("NOT_A_REGULAR_FILE", f"{what} is not a regular file")
    if single_link and info.st_nlink != 1:
        os.close(fd)
        raise refused("HARD_LINKED", f"{what} has more than one name")
    return os.fdopen(fd, "rb")


DROPBOX_BLOCK = 4 * 1024 * 1024


def snapshot_digests(path, kinds):
    """One read of ``path`` (as a regular file) giving sha256 and each requested digest of the SAME bytes.
    ``dropbox`` is Dropbox's content hash: sha256 over the sha256 of each 4 MiB block."""
    hashers = {kind: hashlib.new(kind) for kind in {"sha256", *kinds} if kind in SIMPLE_HASHES}
    blocks, block, block_len, size = hashlib.sha256(), hashlib.sha256(), 0, 0
    with open_regular(path, "a staged file", single_link=True) as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b""):
            size += len(chunk)
            for hasher in hashers.values():
                hasher.update(chunk)
            if "dropbox" in kinds:
                view = memoryview(chunk)
                while view:
                    take = min(len(view), DROPBOX_BLOCK - block_len)
                    block.update(view[:take])
                    block_len += take
                    view = view[take:]
                    if block_len == DROPBOX_BLOCK:
                        blocks.update(block.digest())
                        block, block_len = hashlib.sha256(), 0
    out = {kind: hasher.hexdigest() for kind, hasher in hashers.items()}
    if "dropbox" in kinds:
        if block_len:
            blocks.update(block.digest())
        out["dropbox"] = blocks.hexdigest()
    out["size"] = size
    return out


class _NullSink:
    def write(self, data):
        return len(data)


def _sha_size(path):
    snap = snapshot_digests(path, ())
    return {"sha256": snap["sha256"], "size": snap["size"]}


def hash_regular(path, check=None, what="a file"):
    """sha256 of a regular file, read in chunks through ``open_regular``; ``check`` runs between chunks."""
    digest = hashlib.sha256()
    with open_regular(path, what) as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b""):
            digest.update(chunk)
            if check:
                check()
    return digest.hexdigest()


def hash_tree(span_dir, check=None):
    """The manifest of a tree on disk (a re-run's comparison, and the pull's check)."""
    _, files = walk_span(span_dir)
    return manifest_bytes({rel: hash_regular(Path(span_dir) / rel, check, "a span file") for rel in files})


class _HashingWriter(io.RawIOBase):
    """Hashes what it passes on. Once ``aborted``, writes are discarded so a failed archive never blocks or
    raises again while its gzip/tar layers are closed."""

    def __init__(self, sink):
        self.sink = sink
        self.hash = hashlib.sha256()
        self.size = 0
        self.aborted = False

    def writable(self):
        return True

    def write(self, data):
        view = memoryview(data)
        if self.aborted:
            return len(view)
        self.sink.write(view)
        self.hash.update(view)
        self.size += len(view)
        return len(view)


class _HashingReader:
    def __init__(self, handle):
        self.handle = handle
        self.hash = hashlib.sha256()

    def read(self, size=-1):
        data = self.handle.read(size)
        self.hash.update(data)
        return data


def write_archive(span_dir, sink, check=None):
    """Stream OUT as a gzip tar into ``sink``; return (manifest bytes, archive sha256, archive size, file count).

    Each file is read exactly once; the manifest hashes those same bytes. A file whose size or mtime moves
    while it is read refuses the offload (``SPAN_CHANGED``).
    """
    span_dir = Path(span_dir)
    top = span_dir.name
    _check_name(top, "the span's parent")
    snapshot = span_snapshot(span_dir, check)
    dirs = sorted((rel for rel, info in snapshot.items() if rel != "." and stat.S_ISDIR(info[2])),
                  key=lambda r: r.encode("utf-8"))
    files = sorted((rel for rel, info in snapshot.items() if stat.S_ISREG(info[2])), key=lambda r: r.encode("utf-8"))
    writer = _HashingWriter(sink)
    digests = {}
    gz = gzip.GzipFile(filename="", mode="wb", fileobj=writer, compresslevel=GZIP_LEVEL, mtime=0)
    tar = tarfile.open(fileobj=gz, mode="w|", format=tarfile.PAX_FORMAT)
    try:
        info = tarfile.TarInfo(top)
        info.type, info.mode, info.mtime = tarfile.DIRTYPE, 0o755, int(os.lstat(span_dir).st_mtime)
        tar.addfile(info)
        for rel in dirs:
            info = tarfile.TarInfo(f"{top}/{rel}")
            info.type, info.mode = tarfile.DIRTYPE, 0o755
            info.mtime = int(os.lstat(span_dir / rel).st_mtime)
            tar.addfile(info)
        for rel in files:
            if check:
                check()
            digests[rel] = _add_file(tar, span_dir / rel, f"{top}/{rel}")
        require_snapshot(span_dir, snapshot, check)
        tar.close()
        gz.close()
    except BaseException:
        writer.aborted = True  # closing the layers below writes nothing into a stalled or dead pipe
        with contextlib.suppress(Exception):
            tar.close()
        with contextlib.suppress(Exception):
            gz.close()
        raise
    return manifest_bytes(digests), writer.hash.hexdigest(), writer.size, len(files)


def _add_file(tar, path, arcname):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))
    except OSError as error:
        raise refused("SPAN_UNREADABLE", type(error).__name__) from None
    with os.fdopen(fd, "rb") as handle:
        before = os.fstat(handle.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise refused("SPAN_SPECIAL_FILE", "a file changed type during the offload")
        info = tarfile.TarInfo(arcname)
        info.type, info.size = tarfile.REGTYPE, before.st_size
        info.mode, info.mtime = stat.S_IMODE(before.st_mode) & 0o755 | 0o400, int(before.st_mtime)
        reader = _HashingReader(handle)
        try:
            tar.addfile(info, reader)
        except OSError as error:
            if "unexpected end of data" in str(error):
                raise refused("SPAN_CHANGED", "a file shrank while it was archived") from None
            raise
        after = os.fstat(handle.fileno())
        if handle.read(1) or (after.st_size, after.st_mtime_ns, after.st_ctime_ns) != (
                before.st_size, before.st_mtime_ns, before.st_ctime_ns):
            raise refused("SPAN_CHANGED", "a file changed while it was archived")
        return reader.hash.hexdigest()


# --- openssl ---------------------------------------------------------------------------------------

def openssl_env():
    """The environment for every openssl child: no OPENSSL_*/SSL_*/RANDFILE variable is inherited, and the
    configuration file is /dev/null, so openssl reads no configuration from anywhere (A.4)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("OPENSSL_", "SSL_", "RANDFILE", "LIBRESSL_"))}
    env["OPENSSL_CONF"] = os.devnull
    return env


def _openssl_run(openssl, args, *, input=None, deadline=None, cap=600):
    try:
        proc = subprocess.run([openssl, *args], input=input, capture_output=True, env=openssl_env(),
                              timeout=deadline.remaining(cap) if deadline else cap)
    except subprocess.TimeoutExpired:
        raise unverified("OPENSSL_TIMEOUT", args[0]) from None
    except OSError:
        raise refused("OPENSSL_UNAVAILABLE", "the openssl binary could not run") from None
    if proc.returncode:
        raise OffloadError("OPENSSL_FAILED", f"openssl {args[0]} rc={proc.returncode}",
                           "integrity" if "-decrypt" in args or "-d" in args else "refused")
    return proc.stdout


def public_key_fingerprint(openssl, public_key, deadline=None):
    """sha256 of the DER SubjectPublicKeyInfo, and the key size in bits."""
    der = _openssl_run(openssl, ["pkey", "-pubin", "-in", str(public_key), "-outform", "DER"], deadline=deadline)
    text = _openssl_run(openssl, ["pkey", "-pubin", "-in", str(public_key), "-noout", "-text"],
                        deadline=deadline).decode("ascii", "replace")
    match = re.search(r"\((\d+) bit\)", text)
    if "RSA" not in text.upper() and not match:
        raise refused("RECIPIENT_NOT_RSA", "the recipient key is not an RSA public key")
    return sha256_bytes(der), int(match.group(1)) if match else 0


def check_recipient(openssl, public_key, pinned_sha256, deadline=None):
    if not HEX64.fullmatch(pinned_sha256 or ""):
        raise refused("CONFIG", "recipient_sha256 must be 64 lower-case hex digits")
    fingerprint, bits = public_key_fingerprint(openssl, public_key, deadline)
    if fingerprint != pinned_sha256:
        raise refused("RECIPIENT_MISMATCH", "the recipient public key is not the pinned one")
    if bits < MIN_RSA_BITS:
        raise refused("RECIPIENT_WEAK", f"RSA key under {MIN_RSA_BITS} bits")
    return fingerprint, bits


def _enc_args(decrypt, fd):
    return ["enc", "-d" if decrypt else "-e", f"-{CIPHER}", "-pbkdf2", "-iter", str(KDF_ITER), "-md", "sha256",
            "-salt", "-pass", f"fd:{fd}"]


ENCRYPT_CAP_S = 4 * 3600


def encrypt_span(openssl, span_dir, passphrase, out_path, deadline=None):
    """Archive and encrypt in one pass. Returns (manifest, archive sha256, archive size, file count).

    One watchdog bounds the whole stream: at the deadline (or ``ENCRYPT_CAP_S``) it kills openssl, which
    unblocks a write into a pipe nobody drains; the offload then fails with ``DEADLINE`` and no marker.
    """
    budget = deadline.remaining(ENCRYPT_CAP_S) if deadline else ENCRYPT_CAP_S
    read_end, write_end = os.pipe()
    try:
        os.write(write_end, passphrase + b"\n")
    finally:
        os.close(write_end)
    try:
        with open(out_path, "xb") as out:
            proc = subprocess.Popen([openssl, *_enc_args(False, read_end)],
                                    stdin=subprocess.PIPE, stdout=out, stderr=subprocess.DEVNULL,
                                    pass_fds=(read_end,), env=openssl_env())
            _CHILDREN.add(proc)
    except OSError:
        os.close(read_end)
        raise refused("OPENSSL_UNAVAILABLE", "the openssl binary could not run") from None
    os.close(read_end)
    expired = threading.Event()

    def expire():
        expired.set()
        with contextlib.suppress(OSError):
            proc.kill()

    timer = threading.Timer(budget, expire)
    timer.daemon = True
    timer.start()
    try:
        try:
            result = write_archive(span_dir, proc.stdin, check=deadline.remaining if deadline else None)
            proc.stdin.close()
        except (BrokenPipeError, ValueError):  # a write into a killed or closed pipe
            if expired.is_set():
                raise unverified("DEADLINE", "the archive and encryption did not finish in time") from None
            raise refused("OPENSSL_FAILED", "openssl enc exited while the archive was written") from None
        try:
            rc = proc.wait(timeout=max(1.0, budget))
        except subprocess.TimeoutExpired:
            raise unverified("DEADLINE", "openssl enc did not finish in time") from None
        if expired.is_set():
            raise unverified("DEADLINE", "the archive and encryption did not finish in time")
    except BaseException:
        proc.kill()
        proc.wait()
        with contextlib.suppress(OSError):
            proc.stdin.close()
        raise
    finally:
        timer.cancel()
        _CHILDREN.discard(proc)
    if rc:
        raise refused("OPENSSL_FAILED", f"openssl enc rc={rc}")
    return result


def verify_ciphertext(openssl, passphrase, in_path, archive_sha256, deadline=None, *, manifest=None, top=None):
    """Decrypt the staged ciphertext with the passphrase still in memory and require the archive's sha256.

    The MBP cannot test the RSA wrap (it has no private key), but it can prove the ciphertext it uploads
    decrypts to the archive it hashed. Plaintext is streamed and hashed, never written.
    """
    budget = deadline.remaining(ENCRYPT_CAP_S) if deadline else ENCRYPT_CAP_S
    read_end, write_end = os.pipe()
    try:
        os.write(write_end, passphrase + b"\n")
    finally:
        os.close(write_end)
    try:
        proc = subprocess.Popen([openssl, *_enc_args(True, read_end), "-in", str(in_path)], stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, pass_fds=(read_end,), env=openssl_env())
        _CHILDREN.add(proc)
    except OSError:
        raise refused("OPENSSL_UNAVAILABLE", "the openssl binary could not run") from None
    finally:
        os.close(read_end)
    timer = threading.Timer(budget, proc.kill)
    timer.daemon = True
    timer.start()
    reader = _HashingReader(proc.stdout)
    try:
        if manifest is not None:
            digests, seen = {}, set()
            try:
                # Parse only our freshly generated transport container, never a source payload.
                with tarfile.open(fileobj=reader, mode="r|gz") as tar:
                    for member in tar:
                        if member.name in seen or not (member.isdir() or member.isreg()) or (
                                member.name != top and not member.name.startswith(top + "/")):
                            raise refused("PACK_MANIFEST_MISMATCH", "invalid packed member")
                        seen.add(member.name)
                        if member.isreg():
                            digest = hashlib.sha256()
                            with tar.extractfile(member) as handle:
                                for chunk in iter(lambda: handle.read(CHUNK), b""):
                                    if deadline:
                                        deadline.remaining()
                                    digest.update(chunk)
                            digests[member.name[len(top) + 1:]] = digest.hexdigest()
                if manifest_bytes(digests) != manifest:
                    raise refused("PACK_MANIFEST_MISMATCH", "packed files differ from the per-file manifest")
            except (tarfile.TarError, EOFError, zlib.error):
                raise refused("CIPHERTEXT_UNVERIFIED", "the packed stream cannot be read") from None
        for _chunk in iter(lambda: reader.read(CHUNK), b""):
            pass  # include trailing compressed bytes in the archive digest; drain openssl before wait
        rc = proc.wait()
    finally:
        timer.cancel()
        if proc.poll() is None:
            proc.kill()
            proc.wait()
        proc.stdout.close()
        _CHILDREN.discard(proc)
    if deadline:
        deadline.remaining()
    if rc or reader.hash.hexdigest() != archive_sha256:
        raise refused("CIPHERTEXT_UNVERIFIED", "the staged ciphertext does not decrypt to the archive")


def wrap_passphrase(openssl, public_key, passphrase, out_path, deadline=None, bits=None):
    wrapped = _openssl_run(openssl, ["pkeyutl", "-encrypt", "-pubin", "-inkey", str(public_key),
                                     "-pkeyopt", "rsa_padding_mode:oaep"], input=passphrase, deadline=deadline)
    if bits is not None and len(wrapped) != (bits + 7) // 8:
        raise refused("WRAP_INVALID", "the wrapped key is not one RSA block")
    with open(out_path, "xb") as out:
        out.write(wrapped)


def unwrap_passphrase(openssl, identity, wrapped_path):
    return _openssl_run(openssl, ["pkeyutl", "-decrypt", "-inkey", str(identity), "-pkeyopt",
                                  "rsa_padding_mode:oaep", "-in", str(wrapped_path)])


def decrypt_file(openssl, passphrase, in_path, out_path, deadline=None):
    read_end, write_end = os.pipe()
    try:
        os.write(write_end, passphrase + b"\n")
    finally:
        os.close(write_end)
    try:
        with open(out_path, "xb") as out:
            proc = subprocess.run([openssl, *_enc_args(True, read_end), "-in", str(in_path)], stdout=out,
                                  stderr=subprocess.DEVNULL, pass_fds=(read_end,), env=openssl_env(),
                                  timeout=deadline.remaining(3600) if deadline else 3600)
    except subprocess.TimeoutExpired:
        raise integrity("OPENSSL_TIMEOUT", "decrypt") from None
    finally:
        os.close(read_end)
    if proc.returncode:
        raise integrity("DECRYPT_FAILED", f"openssl enc -d rc={proc.returncode}")


# --- backends ---------------------------------------------------------------------------------------

class LocalBackend:
    """A directory (tests, or a sync folder). It cannot see the provider, so ``provider_confirmed`` is false."""

    kind = "local"
    provider_confirmed = False

    def __init__(self, spec):
        self.root = Path(spec["root"])
        if not self.root.is_dir():
            raise refused("BACKEND_ROOT", "the local backend root is not a directory")

    def describe(self):
        return {"kind": self.kind, "root": str(self.root)}

    def _plan_dir(self, plan):
        dest_dir = self.root / plan
        if os.path.islink(dest_dir) or (os.path.lexists(dest_dir) and not dest_dir.is_dir()):
            raise unverified("BACKEND_PATH", "the backend's plan directory is a symlink or not a directory")
        return dest_dir

    def put(self, local, plan, name, deadline=None):
        dest_dir = self._plan_dir(plan)
        dest_dir.mkdir(exist_ok=True)
        if inside_git(dest_dir):
            raise unverified("BACKEND_PATH", "the backend's plan directory is inside a git repository")
        if os.path.islink(dest_dir / name):
            raise unverified("BACKEND_PATH", "the backend's file is a symlink")
        dest = dest_dir / name
        snap = snapshot_digests(local, ())
        local_sha, size = snap["sha256"], snap["size"]
        if os.path.lexists(dest):
            if hash_regular(dest, what="the backend copy") != local_sha:
                raise unverified("REMOTE_CONFLICT", f"{name} exists with other bytes")
        else:
            # A fresh, unpredictable, exclusively created temporary file: nothing foreign is followed.
            fd, tmp = tempfile.mkstemp(prefix=f".{name}.part-", dir=dest_dir)
            try:
                with os.fdopen(fd, "wb") as out, open_regular(local, "a staged file") as source:
                    shutil.copyfileobj(source, out, CHUNK)
                    out.flush()
                    os.fsync(out.fileno())
                os.replace(tmp, dest)
            except BaseException:
                with contextlib.suppress(OSError):
                    os.unlink(tmp)
                raise
        remote_sha, remote_size = hash_regular(dest, what="the backend copy"), os.lstat(dest).st_size
        if (remote_sha, remote_size) != (local_sha, size):
            raise unverified("READBACK_MISMATCH", name)
        return {"name": name, "size": size, "sha256": local_sha, "provider_hash_type": "sha256",
                "provider_hash": remote_sha, "provider_size": remote_size, "kind": "local-readback"}

    def get(self, plan, name, dest, deadline=None):
        src = self._plan_dir(plan) / name
        if os.path.islink(src) or not src.is_file():
            raise integrity("REMOTE_MISSING", name)
        shutil.copyfile(src, dest)


class RcloneBackend:
    """``rclone copyto`` (synchronous; it exits) then ``rclone lsjson --hash`` read back from the provider."""

    kind = "rclone"
    provider_confirmed = True

    def __init__(self, spec):
        self.rclone = spec.get("rclone", "rclone")
        self.config = spec.get("rclone_config")
        if not isinstance(self.config, str) or not os.path.isabs(self.config):
            raise refused("CONFIG", "the rclone backend needs rclone_config, an absolute path (rclone's own "
                                    "discovery of a config is never used)")
        self.remote = spec["remote"]
        self.hash_type = spec.get("hash_type", "sha256")
        self.timeout_s = float(spec.get("timeout_s", 5400))
        self.readback_tries = int(spec.get("readback_tries", 3))
        self.readback_wait_s = float(spec.get("readback_wait_s", 10))
        if not isinstance(self.remote, str) or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_. -]*:[^\n]*", self.remote):
            raise refused("CONFIG", "the rclone remote must be a named remote, name:path (not a path, :backend: or a flag)")
        if self.hash_type not in SIMPLE_HASHES + ("dropbox", "size"):
            raise refused("CONFIG", "hash_type must be sha256, sha1, md5, dropbox or size")

    def describe(self):
        return {"kind": self.kind, "remote": self.remote, "hash_type": self.hash_type}

    def _path(self, plan, name=None):
        base = self.remote if self.remote.endswith((":", "/")) else self.remote + "/"
        return base + plan + ("/" + name if name else "")

    def _run(self, args, deadline, cap=None):
        argv = [self.rclone]
        argv += ["--config", self.config]
        argv += ["--retries", "3", "--low-level-retries", "10", "--contimeout", "60s", "--timeout", "300s",
                 "--stats", "0", "-q", *args]
        timeout = deadline.remaining(cap or self.timeout_s) if deadline else (cap or self.timeout_s)
        try:
            env = {k: v for k, v in os.environ.items() if not k.startswith("RCLONE_")}  # no option from the environment
            proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                                    env=env)
        except OSError:
            raise unverified("RCLONE_UNAVAILABLE", "the rclone binary could not run") from None
        _CHILDREN.add(proc)  # a signal handler kills it too (kill_children)
        try:
            out, _ = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            raise unverified("UPLOAD_TIMEOUT", args[0]) from None
        except BaseException:
            proc.kill()
            proc.wait()
            raise
        finally:
            _CHILDREN.discard(proc)
        if proc.returncode:
            raise unverified("RCLONE_FAILED", f"rclone {args[0]} rc={proc.returncode}")
        return out

    def put(self, local, plan, name, deadline=None):
        # sha256 and the provider's digest come from ONE read of the staged bytes, before the upload; after
        # it the file must still be those bytes, and the provider must report that same digest.
        snap = snapshot_digests(local, () if self.hash_type == "size" else (self.hash_type,))
        local_sha, size = snap["sha256"], snap["size"]
        expected = None if self.hash_type == "size" else snap[self.hash_type]
        self._run(["copyto", "--immutable", str(local), self._path(plan, name)], deadline)
        after = snapshot_digests(local, ())
        if (after["sha256"], after["size"]) != (local_sha, size):
            raise unverified("STAGE_CHANGED", f"{name} changed during its upload")
        for attempt in range(1, self.readback_tries + 1):
            try:
                return self._readback(plan, name, size, local_sha, expected, deadline)
            except OffloadError as error:
                # A listing that lags the upload, or a hash the provider has not computed yet, is retried;
                # a size or hash that differs is final.
                if error.code not in ("READBACK_MISSING", "READBACK_NO_HASH") or attempt == self.readback_tries:
                    raise
                time.sleep(deadline.remaining(self.readback_wait_s) if deadline else self.readback_wait_s)
        raise unverified("READBACK_MISSING", name)

    def _readback(self, plan, name, size, local_sha, expected, deadline):
        hash_args = [] if self.hash_type == "size" else ["--hash", "--hash-type", self.hash_type]
        listing = self._run(["lsjson", "--files-only", *hash_args, self._path(plan)], deadline, cap=600)
        try:
            parsed = json.loads(listing)
            if not isinstance(parsed, list):
                raise ValueError("not a list")
            rows = [row for row in parsed if isinstance(row, dict) and row.get("Name") == name]
        except (ValueError, RecursionError):
            raise unverified("READBACK_UNPARSEABLE", name) from None
        if len(rows) != 1:
            raise unverified("READBACK_MISSING", name)
        row = rows[0]
        provider_size = row.get("Size")
        if provider_size != size:
            raise unverified("READBACK_SIZE", name)
        hashes = row.get("Hashes") or {}
        if not isinstance(hashes, dict):
            raise unverified("READBACK_UNPARSEABLE", name)
        provider_hash = hashes.get(self.hash_type) if expected is not None else None
        if provider_hash is not None and not isinstance(provider_hash, str):
            raise unverified("READBACK_UNPARSEABLE", name)
        if expected is not None and (provider_hash != expected or not re.fullmatch(r"[0-9a-f]{32,128}", expected)):
            raise unverified("READBACK_HASH" if provider_hash else "READBACK_NO_HASH", name)
        return {"name": name, "size": size, "sha256": local_sha, "provider_hash_type": self.hash_type,
                "provider_hash": provider_hash, "provider_size": provider_size, "kind": "rclone-lsjson"}

    def get(self, plan, name, dest, deadline=None):
        try:
            self._run(["copyto", self._path(plan, name), str(dest)], deadline)
        except OffloadError as error:
            raise integrity("DOWNLOAD_FAILED", f"{name}: {error.code}") from None


ICLOUD_ROOT = "~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-offload"
ICLOUD_CONFIRMATION = "icloud evict+redownload sha256 match"


def _is_dataless(info):
    """Apple TN3150 / sys/stat.h: SF_DATALESS is metadata, not a local-byte hash.

    None means this platform cannot observe eviction; command success alone is never confirmation.
    """
    flags = getattr(info, "st_flags", None)
    return None if flags is None else bool(flags & getattr(stat, "SF_DATALESS", 0x40000000))


@contextlib.contextmanager
def _directory_no_links(path):
    """Walk an absolute directory using openat and O_NOFOLLOW for EVERY component."""
    path = Path(path)
    fd = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd
    except OSError:
        raise unverified("BACKEND_PATH", "an iCloud directory is missing, linked or inaccessible") from None
    finally:
        os.close(fd)


class ICloudBackend:
    """Wait for CloudDocs, then require observed eviction and hash the downloaded bytes.

    brctl's undocumented status format is treated conservatively. Only its status text is parsed;
    neither journals nor CloudDocs databases are opened. Unsupported eviction/download writes only
    an unconfirmed marker. Upload/status failures and wrong bytes write no marker.
    """

    kind = "icloud"

    def __init__(self, spec):
        self.root = Path(spec.get("root", ICLOUD_ROOT)).expanduser()
        if not self.root.is_absolute() or ".." in self.root.parts:
            raise refused("CONFIG", "the iCloud root must be an absolute directory")
        self.brctl = spec.get("brctl", "brctl")
        self.timeout_s = spec.get("timeout_s", 5400)
        self.poll_interval_s = spec.get("poll_interval_s", 2)
        self.evict_timeout_s = spec.get("evict_timeout_s", 30)
        self.download_timeout_s = spec.get("download_timeout_s", 600)
        for value in (self.timeout_s, self.poll_interval_s, self.evict_timeout_s, self.download_timeout_s):
            if not number(value) or value <= 0:
                raise refused("CONFIG", "iCloud timeouts and poll_interval_s must be finite positive seconds")
        self.provider_confirmed = True  # downgraded permanently for this run if ANY readback is unavailable

    def describe(self):
        return {"kind": self.kind, "root": str(self.root), "readback": ICLOUD_CONFIRMATION}

    def _bounded(self, deadline, seconds):
        clock = deadline.clock if deadline else time.time
        end = clock() + seconds
        return Deadline(min(end, deadline.epoch) if deadline and deadline.epoch is not None else end, clock)

    def _run(self, args, deadline):
        timeout = deadline.remaining()
        try:
            proc = subprocess.Popen([self.brctl, *args], stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError:
            raise unverified("BRCTL_UNAVAILABLE", "brctl could not run") from None
        _CHILDREN.add(proc)
        try:
            out, _ = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            raise unverified("BRCTL_TIMEOUT", args[0]) from None
        except BaseException:
            proc.kill()
            proc.wait()
            raise
        finally:
            _CHILDREN.discard(proc)
        if proc.returncode:
            raise unverified("BRCTL_FAILED", f"brctl {args[0]} rc={proc.returncode}")
        deadline.remaining()
        return out

    @staticmethod
    def _uploaded(status):
        # Item 350's observable: com.apple.CloudDocs, client:idle, caught-up. Empty output,
        # an unknown format or ANY pending/error state is not positive upload evidence.
        text = status.decode("utf-8", "replace")
        return (re.search(r"\bcom\.apple\.CloudDocs\b", text) is not None
                and re.search(r"\bclient\s*:\s*idle\b", text) is not None
                and re.search(r"(?<![\w-])caught-up(?![\w-])", text) is not None
                and re.search(r"needs-|uploading|downloading|\bpending\b|\berror\b|\boffline\b|not[- ](?:caught|idle)",
                              text, re.I) is None)

    def _wait_uploaded(self, deadline):
        while True:
            if self._uploaded(self._run(["status", "com.apple.CloudDocs"], deadline)):
                return deadline.clock()
            time.sleep(deadline.remaining(self.poll_interval_s))

    @contextlib.contextmanager
    def _plan(self, plan, create=False):
        check_id(plan, "plan")
        if inside_git(self.root / plan):
            raise unverified("BACKEND_PATH", "the iCloud destination is inside a repository")
        with _directory_no_links(self.root) as root_fd:
            if create:
                try:
                    os.mkdir(plan, mode=0o700, dir_fd=root_fd)
                except FileExistsError:
                    pass
            try:
                fd = os.open(plan, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd)
            except OSError:
                raise unverified("BACKEND_PATH", "the iCloud plan directory is linked or unavailable") from None
            try:
                yield fd, self.root / plan
            finally:
                os.close(fd)

    @staticmethod
    def _info(fd, name):
        try:
            info = os.stat(name, dir_fd=fd, follow_symlinks=False)
        except OSError:
            raise unverified("BACKEND_PATH", "an iCloud file is unavailable") from None
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise unverified("BACKEND_PATH", "an iCloud file is not a single-name regular file")
        return info

    def _digest(self, fd, name, deadline, dest=None):
        self._info(fd, name)
        digest, size = hashlib.sha256(), 0
        with open_regular(name, "an iCloud file", dir_fd=fd, single_link=True) as source:
            for chunk in iter(lambda: source.read(CHUNK), b""):
                deadline.remaining()
                digest.update(chunk)
                size += len(chunk)
                if dest is not None:
                    dest.write(chunk)
        deadline.remaining()
        return digest.hexdigest(), size

    def _wait_flag(self, fd, name, wanted, deadline):
        while True:
            observed = _is_dataless(self._info(fd, name))
            if observed is None:
                raise unverified("DATALESS_UNAVAILABLE", "this platform cannot observe SF_DATALESS")
            if observed == wanted:
                return deadline.clock()
            time.sleep(deadline.remaining(self.poll_interval_s))

    def _download(self, fd, path, deadline):
        self._info(fd, path.name)
        self._run(["download", str(path)], deadline)
        self._wait_flag(fd, path.name, False, deadline)

    def _unconfirmed(self, error, deadline, row):
        deadline.remaining()  # overall exhaustion is always exit 5
        if error.code not in ("BRCTL_FAILED", "BRCTL_UNAVAILABLE", "BRCTL_TIMEOUT", "DEADLINE",
                              "DATALESS_UNAVAILABLE"):
            raise error
        self.provider_confirmed = False
        return dict(row, kind="icloud-unconfirmed", reason=error.code)

    def put(self, local, plan, name, deadline=None):
        if name not in names(plan).values():
            raise refused("BAD_NAME", "an iCloud object must have its plan's fixed name")
        deadline = self._bounded(deadline, self.timeout_s)
        snap = snapshot_digests(local, ())
        expected = snap["sha256"], snap["size"]
        row = {"name": name, "sha256": expected[0], "size": expected[1], "provider_hash_type": "sha256",
               "provider_hash": None, "provider_size": None, "provider_confirmed": False}
        with self._plan(plan, create=True) as (fd, directory):
            path = directory / name
            try:
                os.stat(name, dir_fd=fd, follow_symlinks=False)
                exists = True
            except FileNotFoundError:
                exists = False
            if exists:
                if _is_dataless(self._info(fd, name)):
                    row["uploaded_epoch_s"] = self._wait_uploaded(deadline)
                    try:
                        self._download(fd, path, self._bounded(deadline, self.download_timeout_s))
                    except OffloadError as error:
                        return self._unconfirmed(error, deadline, row)
                if self._digest(fd, name, deadline) != expected:
                    raise unverified("REMOTE_CONFLICT", f"{name} exists with other bytes")
            else:
                tmp = f".{name}.part-{secrets.token_hex(12)}"
                out_fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
                try:
                    with os.fdopen(out_fd, "wb") as out, open_regular(local, "a staged file", single_link=True) as src:
                        for chunk in iter(lambda: src.read(CHUNK), b""):
                            deadline.remaining()
                            out.write(chunk)
                        out.flush()
                        os.fsync(out.fileno())
                    os.rename(tmp, name, src_dir_fd=fd, dst_dir_fd=fd)
                finally:
                    with contextlib.suppress(FileNotFoundError):
                        os.unlink(tmp, dir_fd=fd)
                if self._digest(fd, name, deadline) != expected:
                    raise unverified("READBACK_HASH", name)
            row["uploaded_epoch_s"] = self._wait_uploaded(deadline)
            try:
                self._info(fd, name)
                eviction = self._bounded(deadline, self.evict_timeout_s)
                self._run(["evict", str(path)], eviction)
                row["evicted_epoch_s"] = self._wait_flag(fd, name, True, eviction)
                self._download(fd, path, self._bounded(deadline, self.download_timeout_s))
            except OffloadError as error:
                return self._unconfirmed(error, deadline, row)
            got = self._digest(fd, name, deadline)
            if got != expected:
                raise unverified("READBACK_HASH", name)
            after = snapshot_digests(local, ())
            if (after["sha256"], after["size"]) != expected:
                raise unverified("STAGE_CHANGED", name)
            return dict(row, kind=ICLOUD_CONFIRMATION, provider_confirmed=True,
                        provider_hash=got[0], provider_size=got[1], verified_epoch_s=deadline.clock())

    def get(self, plan, name, dest, deadline=None):
        if name not in names(plan).values():
            raise refused("BAD_NAME", "an iCloud object must have its plan's fixed name")
        deadline = self._bounded(deadline, self.download_timeout_s)
        try:
            with self._plan(plan) as (fd, directory):
                self._download(fd, directory / name, deadline)
                with open(dest, "xb") as out:
                    self._digest(fd, name, deadline, out)
        except OffloadError as error:
            raise integrity("DOWNLOAD_FAILED", f"{name}: {error.code}") from None


BACKENDS = {"icloud": ICloudBackend, "local": LocalBackend, "rclone": RcloneBackend}


def make_backend(spec, allow_local=False):
    if not isinstance(spec, dict) or spec.get("kind", "icloud") not in BACKENDS:
        raise refused("CONFIG", "backend.kind must be icloud, local or rclone")
    kind = spec.get("kind", "icloud")
    if kind == "local" and not allow_local:
        raise refused("LOCAL_BACKEND_NOT_ALLOWED",
                      "the local backend has no provider confirmation; pass --allow-local-backend (tests/interim)")
    return BACKENDS[kind](spec)


# --- configs ---------------------------------------------------------------------------------------

MBP_KEYS = {"schema", "recipient_public_key", "recipient_sha256", "stage_root", "marker_dir", "backend", "openssl",
            "forbid_paths", "default_budget_s", "lead_email"}
DEFAULT_BUDGET_S = 5400  # item 347's 90 minutes, when the caller names no deadline
AIR_KEYS = {"schema", "identity", "recipient_sha256", "work_root", "backend", "openssl"}


def load_config(path, schema, keys, required):
    try:
        with open_regular(path, "the config file", single_link=True) as handle:
            doc = json.loads(handle.read(1 << 20))
    except (OffloadError, OSError, ValueError, RecursionError):
        raise refused("CONFIG", "the config file is missing, not a regular file or not JSON") from None
    if not isinstance(doc, dict) or doc.get("schema") != schema:
        raise refused("CONFIG", f"schema must be {schema}")
    unknown = set(doc) - keys
    if unknown:
        raise refused("CONFIG", "unknown config keys: " + ", ".join(sorted(unknown)))
    missing = [key for key in required if key not in doc]
    if missing:
        raise refused("CONFIG", "missing config keys: " + ", ".join(missing))
    return doc


def _absolute(doc, keys):
    for key in keys:
        if not isinstance(doc[key], str) or not os.path.isabs(doc[key]):
            raise refused("CONFIG", f"{key} must be an absolute path")
    return doc


def load_mbp_config(path):
    doc = load_config(path, MBP_CONFIG_SCHEMA, MBP_KEYS,
                      ("recipient_public_key", "recipient_sha256", "stage_root", "marker_dir"))
    return _absolute(doc, ("recipient_public_key", "stage_root", "marker_dir"))


def load_air_config(path):
    doc = load_config(path, AIR_CONFIG_SCHEMA, AIR_KEYS, ("identity", "recipient_sha256", "work_root"))
    return _absolute(doc, ("identity", "work_root"))


# --- paths ----------------------------------------------------------------------------------------

def _real(path):
    return os.path.realpath(path)


def _overlaps(a, b):
    a, b = _real(a), _real(b)
    return a == b or a.startswith(b.rstrip("/") + "/") or b.startswith(a.rstrip("/") + "/")


def inside_git(path):
    """True when ``path`` (resolved) is inside a git working tree, a ``.git`` directory or a bare repository."""
    current = Path(_real(path))
    for candidate in (current, *current.parents):
        if os.path.lexists(candidate / ".git") or candidate.name == ".git":
            return True
        if (candidate / "HEAD").is_file() and (candidate / "objects").is_dir() and (candidate / "refs").is_dir():
            return True
    return False


def check_output_paths(span_dir, outputs):
    """Every place the tool writes or reads its own records stays outside OUT and outside any repository (A.5, A.6)."""
    for what, path in outputs.items():
        if span_dir is not None and _overlaps(path, span_dir):
            raise refused("PATH_OVERLAPS_SPAN", f"{what} overlaps the span directory")
        if inside_git(path):
            raise refused("PATH_IN_REPOSITORY", f"{what} is inside a git repository")


# --- offload (MBP) -----------------------------------------------------------------------------------

SOURCE_RECORD = ".source.json"


def _stage_complete(stage, plan):
    """A stage is complete only when its descriptor (written last) exists and every file matches it.

    The stage must be a real directory of regular files: nothing behind a link is opened or parsed.
    """
    try:
        dfd = os.open(stage, os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0))
    except OSError:
        raise refused("STAGE_CONFLICT", "the stage path is a symlink or not a directory") from None
    try:
        return _stage_records(dfd, plan)
    finally:
        os.close(dfd)


def _read_in(dfd, name, limit=1 << 20):
    """A small control file inside the open stage directory: regular, not followed, not waited on."""
    with open_regular(name, "a stage record", dir_fd=dfd, single_link=True) as handle:
        data = handle.read(limit + 1)
    if len(data) > limit:
        raise refused("STAGE_CONFLICT", "a stage record is too large")
    return data


def _stage_records(dfd, plan):
    with os.scandir(dfd) as entries:
        for entry in entries:
            if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                raise refused("STAGE_CONFLICT", "the stage holds a symlink or a non-regular entry")
    files = names(plan)
    try:
        descriptor_bytes = _read_in(dfd, files["descriptor"])
        descriptor = json.loads(descriptor_bytes)
    except OffloadError as error:
        if error.code == "UNREADABLE":
            return None  # no descriptor: an incomplete or foreign stage
        raise refused("STAGE_CONFLICT", "a stage record is not a regular file") from None
    except (ValueError, RecursionError):
        return None
    try:
        for kind in ("ciphertext", "wrapped_key", "manifest"):
            entry = descriptor["files"][kind]
            if entry["name"] != files[kind]:
                return None
            fd = os.open(entry["name"], os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0), dir_fd=dfd)
            with os.fdopen(fd, "rb") as handle:
                if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode) or os.fstat(handle.fileno()).st_nlink != 1:
                    raise refused("STAGE_CONFLICT", "a stage file is not a single-link regular file")
                digest = hashlib.file_digest(handle, "sha256").hexdigest()
                size = os.fstat(handle.fileno()).st_size
            if digest != entry["sha256"] or size != entry["size"]:
                return None
        recorded = json.loads(_read_in(dfd, SOURCE_RECORD))
        manifest = _read_in(dfd, files["manifest"], 1 << 30)
    except OffloadError:
        raise refused("STAGE_CONFLICT", "a stage record is not a regular file") from None
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        return None
    return {"descriptor": descriptor, "source": recorded, "manifest": manifest,
            "descriptor_sha256": sha256_bytes(descriptor_bytes)}


def build_stage(config, plan, span_dir, openssl, recipient_pem, deadline, clock=time.time, bits=None):
    """Build the four files, or reuse a complete stage of the SAME source whose bytes have not changed.

    A complete stage of another source, of another recipient, or of a source whose bytes moved since is
    refused (``STAGE_CONFLICT``), and so is an incomplete or foreign directory at the stage path: the tool
    never moves a directory it did not build. A new stage is built in a private ``.<plan>.building-*``
    directory, removed on any failure, and renamed to ``<plan>`` only when complete.
    """
    stage_root = Path(config["stage_root"])
    stage = stage_root / plan
    files = names(plan)
    source = _real(span_dir)
    if os.path.lexists(stage):
        found = _stage_complete(stage, plan)
        if found is None:
            raise refused("STAGE_CONFLICT", "an incomplete or foreign directory holds this plan's stage path")
        descriptor, recorded = found["descriptor"], found["source"]
        if not isinstance(recorded, dict) or recorded.get("source") != source \
                or not isinstance(descriptor, dict) or descriptor.get("span_name") != Path(span_dir).name \
                or not isinstance(descriptor.get("scheme"), dict) \
                or descriptor["scheme"].get("recipient_sha256") != config["recipient_sha256"]:
            raise refused("STAGE_CONFLICT", "a complete stage of another source or recipient exists for this plan")
        # Re-derive the archive from OUT (deterministic: fixed gzip header and level, tar metadata from the files)
        # and require the stored manifest, archive digest and size: a corrupted or edited descriptor is refused.
        sink = _NullSink()
        manifest, archive_sha, archive_size, _ = write_archive(span_dir, sink, deadline.remaining if deadline else None)
        if manifest != found["manifest"]:
            raise refused("STAGE_CONFLICT", "the span's bytes changed since the stage was built")
        if not isinstance(descriptor.get("archive"), dict) \
                or (descriptor["archive"].get("sha256"), descriptor["archive"].get("size")) != (archive_sha, archive_size) \
                or descriptor.get("schema") != DESCRIPTOR_SCHEMA or descriptor.get("plan") != plan:
            raise refused("STAGE_CONFLICT", "the stored descriptor does not describe this span's archive")
        return stage, descriptor, True, found["descriptor_sha256"]
    building = Path(tempfile.mkdtemp(prefix=f".{plan}.building-", dir=stage_root))
    try:
        (building / SOURCE_RECORD).write_bytes(canonical({"source": source}))
        passphrase = secrets.token_hex(32).encode("ascii")
        manifest, archive_sha, archive_size, count = encrypt_span(openssl, span_dir, passphrase,
                                                                  building / files["ciphertext"], deadline)
        verify_ciphertext(openssl, passphrase, building / files["ciphertext"], archive_sha, deadline,
                          manifest=manifest, top=Path(span_dir).name)
        wrap_passphrase(openssl, recipient_pem, passphrase, building / files["wrapped_key"], deadline, bits)
        del passphrase
        (building / files["manifest"]).write_bytes(manifest)
        descriptor = {
            "schema": DESCRIPTOR_SCHEMA, "plan": plan, "span_name": Path(span_dir).name,
            "created_epoch_s": round(clock(), 3),
            "scheme": {"archive": "tar+gzip", "cipher": CIPHER, "kdf": "pbkdf2-sha256", "kdf_iter": KDF_ITER,
                       "passphrase": "256-bit random, hex", "wrap": "rsa-oaep",
                       "recipient_sha256": config["recipient_sha256"]},
            "archive": {"sha256": archive_sha, "size": archive_size},
            "pack_verification": "stream per-file manifest match",
            "manifest": {"files": count},
            "files": {kind: {"name": files[kind], **_sha_size(building / files[kind])}
                      for kind in ("ciphertext", "wrapped_key", "manifest")},
        }
        descriptor_bytes = canonical(descriptor)
        (building / files["descriptor"]).write_bytes(descriptor_bytes)
        for entry in building.iterdir():
            os.chmod(entry, 0o400)  # the staged bytes are read-only from here to the upload
        os.chmod(building, 0o700)
        os.rename(building, stage)  # the stage path only ever names a complete stage
    except BaseException:
        shutil.rmtree(building, ignore_errors=True)  # our own private directory: a failed build leaves nothing
        raise
    return stage, descriptor, False, sha256_bytes(descriptor_bytes)


def write_marker(marker_path, record):
    """Create the marker only if it does not exist (``test ! -e``), atomically and complete."""
    marker_path = Path(marker_path)
    tmp = marker_path.parent / f".{marker_path.name}.tmp-{os.getpid()}-{secrets.token_hex(4)}"
    with open(tmp, "xb") as handle:
        handle.write(canonical(record))
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.link(tmp, marker_path)
    except FileExistsError:
        raise OffloadError("MARKER_EXISTS", "another writer created the marker first", "marker_exists") from None
    finally:
        tmp.unlink()


@contextlib.contextmanager
def plan_lock(stage_root, plan):
    """One offload per plan at a time, from the first stage read to the marker."""
    path = Path(stage_root) / f".{plan}.lock"
    fd = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise refused("BUSY", "another offload of this plan is running") from None
        yield
    finally:
        os.close(fd)


def offload(config, plan, span_dir, *, require_files=("runner_receipt.json",), allow_local=False,
            deadline_epoch=None, clock=time.time):
    """Run the whole MBP side. Returns the marker record. Raises ``OffloadError``.

    The span directory's name must be the plan id or start with ``<plan>-`` (the runner's OUT naming), the
    span must hold at least one regular file and every ``require_files`` name, and no ``forbid_paths``
    entry (for example the magistrate's desk fence) may exist. Without ``deadline_epoch`` the whole offload
    gets ``default_budget_s`` (90 min).
    """
    check_id(plan, "plan")
    span_dir = Path(span_dir)
    check_id(span_dir.name, "span directory name")
    if not span_name_ok(span_dir.name, plan):
        raise refused("PLAN_SPAN_MISMATCH", "the span directory is not named <plan> or <plan>-<YYYYMMDDTHHMMSSZ>")
    for forbidden in config.get("forbid_paths", []):
        if not isinstance(forbidden, str) or not os.path.isabs(forbidden):
            raise refused("CONFIG", "forbid_paths entries must be absolute paths")
        if os.path.lexists(forbidden):
            raise refused("FORBIDDEN_PATH_PRESENT", "a forbid_paths entry exists (a fence is up)")
    budget = config.get("default_budget_s", DEFAULT_BUDGET_S)
    if not number(budget) or budget <= 0:
        raise refused("CONFIG", "default_budget_s must be a positive number of seconds")
    if deadline_epoch is None:
        deadline_epoch = clock() + budget
    elif not number(deadline_epoch) or deadline_epoch > clock() + MAX_DEADLINE_AHEAD_S:
        raise refused("BAD_DEADLINE", "the deadline is not a finite epoch within 24 h (milliseconds given?)")
    marker_dir = Path(config["marker_dir"])
    stage_root = Path(config["stage_root"])
    if not marker_dir.is_dir() or not stage_root.is_dir():
        raise refused("CONFIG", "the marker directory or the stage root does not exist")
    backend = make_backend(config.get("backend", {}), allow_local)
    if os.path.lexists(marker_path(marker_dir, plan, True)):
        return recheck_marker(config, plan, span_dir, backend, Deadline(deadline_epoch, clock))
    if not walk_span(span_dir)[1]:  # refuses links/special files and a missing or symlinked span, too
        raise refused("SPAN_EMPTY", "the span holds no regular file")
    outputs = {"stage_root": stage_root, "marker_dir": marker_dir,
               "recipient_public_key": config["recipient_public_key"]}
    if isinstance(backend, (LocalBackend, ICloudBackend)):
        outputs["backend root"] = backend.root
    if isinstance(backend, RcloneBackend):
        outputs["rclone_config"] = backend.config  # rclone rewrites it when a token refreshes
    check_output_paths(span_dir, outputs)
    if isinstance(backend, RcloneBackend):
        with open_regular(backend.config, "the rclone config", single_link=True):
            pass  # a regular file with one name: not an alias of a file under OUT
    openssl = config.get("openssl", "openssl")
    deadline = Deadline(deadline_epoch, clock)
    for name in require_files:
        _check_name(name, "--require-file")
        if "/" in name or not os.path.isfile(span_dir / name) or os.path.islink(span_dir / name):
            raise refused("SPAN_NOT_CLOSED", f"required file {name} is absent")
    deadline.remaining()
    with plan_lock(stage_root, plan), tempfile.TemporaryDirectory(prefix=f".{plan}.key-", dir=stage_root) as keydir:
        source_snapshot = span_snapshot(span_dir, deadline.remaining)
        # One snapshot of the public key: the fingerprint, the size check and the wrap all use these bytes.
        recipient_pem = Path(keydir) / "recipient.pem"
        try:
            with open_regular(config["recipient_public_key"], "the recipient public key", single_link=True) as handle:
                key_bytes = handle.read(65537)
        except OffloadError:
            raise refused("RECIPIENT_UNREADABLE", "the recipient public key is not a readable regular file") from None
        if len(key_bytes) > 65536:
            raise refused("RECIPIENT_UNREADABLE", "the recipient public key file is too large")
        recipient_pem.write_bytes(key_bytes)
        recipient, bits = check_recipient(openssl, recipient_pem, config["recipient_sha256"], deadline)
        stage, descriptor, reused, descriptor_sha = build_stage(config, plan, span_dir, openssl, recipient_pem,
                                                                deadline, clock, bits)
        files = names(plan)
        expected = {}
        for kind in UPLOAD_ORDER:  # single-link regular files, never followed, never waited on
            snap = snapshot_digests(stage / files[kind], ())
            expected[kind] = (snap["sha256"], snap["size"])
        for kind in ("ciphertext", "wrapped_key", "manifest"):
            if expected[kind] != (descriptor["files"][kind]["sha256"], descriptor["files"][kind]["size"]):
                raise unverified("STAGE_CHANGED", f"{files[kind]} differs from the descriptor")
        if expected["descriptor"][0] != descriptor_sha:
            raise unverified("STAGE_CHANGED", "the descriptor differs from the one validated")
        deadline.remaining()
        confirmations = [backend.put(stage / files[kind], plan, files[kind], deadline) for kind in UPLOAD_ORDER]
        for kind, row in zip(UPLOAD_ORDER, confirmations):
            if (row["sha256"], row["size"]) != expected[kind] or (
                    row.get("provider_confirmed", True) and row["provider_size"] != expected[kind][1]):
                raise unverified("STAGE_CHANGED", f"{files[kind]} changed during the upload")
        # RL-174 D.1 is the global .ok rule. Legacy transports may retain their hash evidence,
        # but no provider listing (including size-only) substitutes for observed iCloud readback.
        confirmed = isinstance(backend, ICloudBackend) and backend.provider_confirmed
        record = {
            "schema": MARKER_SCHEMA, "plan": plan, "path": "cloud-offload", "span_name": descriptor["span_name"],
            "written_at": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(clock())),
            "written_epoch_s": round(clock(), 3), "stage_reused": reused,
            "backend": backend.describe(), "provider_confirmed": confirmed,
            "recipient_sha256": recipient,
            "manifest_sha256": expected["manifest"][0], "manifest_files": descriptor["manifest"]["files"],
            "ciphertext": {"sha256": expected["ciphertext"][0], "size": expected["ciphertext"][1]},
            "wrapped_key_sha256": expected["wrapped_key"][0],
            "descriptor_sha256": expected["descriptor"][0],
            "archive_sha256": descriptor["archive"]["sha256"],
            "provider_confirmation": confirmations,
        }
        if confirmed:
            marker_files(record, plan, icloud=True)
        if confirmed:
            backend._wait_uploaded(deadline)
        require_snapshot(span_dir, source_snapshot, deadline.remaining)
        deadline.remaining()  # the last check before the marker
        marker = marker_path(marker_dir, plan, confirmed)
        try:
            write_marker(marker, record)
        except OffloadError as error:
            if (isinstance(backend, ICloudBackend) and not backend.provider_confirmed
                    and error.exit_kind == "marker_exists"):
                with open_regular(marker, "the existing unconfirmed marker", single_link=True):
                    pass  # preserve it; never confuse this with a completed copy-gate marker
                raise OffloadError("ICLOUD_UNCONFIRMED",
                                   "readback is still unconfirmed; existing .ok.unconfirmed preserved",
                                   "unconfirmed") from None
            raise
    return record


def read_record(path):
    with open_regular(path, "an offload record", single_link=True) as handle:
        try:
            record = json.loads(handle.read(1 << 20))
        except (ValueError, RecursionError):
            raise refused("RECORD_INVALID", "the offload record is not JSON") from None
    if not isinstance(record, dict):
        raise refused("RECORD_INVALID", "the offload record is not an object")
    return record


def marker_files(record, plan, *, icloud=False):
    """Validate a typed copy marker, including every observed round trip. Legacy lines are no proof."""
    try:
        if record["schema"] != MARKER_SCHEMA or record["plan"] != plan or record["provider_confirmed"] is not True:
            raise ValueError
        if not span_name_ok(record["span_name"], plan):
            raise ValueError
        if icloud and record["backend"]["kind"] != "icloud":
            raise ValueError
        expect = expectations(record)
        files = {}
        rows = record["provider_confirmation"]
        if len(rows) != len(UPLOAD_ORDER):
            raise ValueError
        for kind, row in zip(UPLOAD_ORDER, rows):
            if row["name"] != names(plan)[kind] or row["sha256"] != expect[kind] or not HEX64.fullmatch(expect[kind]):
                raise ValueError
            if type(row["size"]) is not int or row["size"] < 1 or row["provider_size"] != row["size"]:
                raise ValueError
            if icloud or record["backend"]["kind"] == "icloud":
                times = [row[k] for k in ("uploaded_epoch_s", "evicted_epoch_s", "verified_epoch_s")]
                if row.get("provider_confirmed") is not True or row["kind"] != ICLOUD_CONFIRMATION \
                        or row["provider_hash"] != expect[kind] or not all(number(t) for t in times) \
                        or times != sorted(times):
                    raise ValueError
            files[kind] = {"sha256": expect[kind], "size": row["size"]}
        if files["ciphertext"] != record["ciphertext"]:
            raise ValueError
        return files
    except (KeyError, TypeError, ValueError):
        raise refused("MARKER_INVALID", "the marker lacks complete, consistent verification evidence") from None


def recheck_marker(config, plan, span_dir, backend, deadline):
    marker = marker_path(config["marker_dir"], plan, True)
    try:
        record = read_record(marker)
    except OffloadError as error:
        if error.code == "RECORD_INVALID":
            raise OffloadError("MARKER_EXISTS", "legacy marker preserved; verify it separately", "marker_exists") from None
        raise
    expected = marker_files(record, plan, icloud=True)
    if record["backend"] != backend.describe() or record.get("recipient_sha256") != config["recipient_sha256"]:
        raise refused("MARKER_INVALID", "the marker belongs to another backend or key")
    controls = {"marker": marker, "stage_root": config["stage_root"], "recipient": config["recipient_public_key"]}
    if isinstance(backend, (ICloudBackend, LocalBackend)):
        controls["backend"] = backend.root
    if isinstance(backend, RcloneBackend):
        controls["rclone_config"] = backend.config
    check_output_paths(span_dir, controls)
    with plan_lock(config["stage_root"], plan), tempfile.TemporaryDirectory(dir=config["stage_root"]) as tmp:
        for kind, name in names(plan).items():
            target = Path(tmp) / name
            backend.get(plan, name, target, deadline)
            if _sha_size(target) != expected[kind]:
                raise unverified("READBACK_HASH", "a previously verified cloud artifact changed")
        source_snapshot = None
        if os.path.lexists(span_dir):
            source_snapshot = span_snapshot(span_dir, deadline.remaining)
            manifest, digest, _size, _count = write_archive(span_dir, _NullSink(), deadline.remaining)
            if sha256_bytes(manifest) != record["manifest_sha256"] or digest != record["archive_sha256"]:
                raise refused("SPAN_CHANGED", "the source differs from the existing copy marker")
        if isinstance(backend, ICloudBackend):
            backend._wait_uploaded(deadline)
        if source_snapshot is not None:
            # The final status subprocess must not reopen a source-mutation gap on a valid retry.
            require_snapshot(span_dir, source_snapshot, deadline.remaining)
        elif os.path.lexists(span_dir):
            raise refused("SPAN_CHANGED", "an original appeared during marker retry")
        deadline.remaining()
    return record  # immutable marker; valid retries exit 0 only after rechecking hashes


def pending_transfers(config, *, clock=time.time):
    """Read-only pre-arm observation. Container-wide idle is stricter than JouleWise folders only.

    Unknown, pending, offline and error states fail closed. This command never downloads or evicts.
    Run in the user's GUI domain; an SSH observation cannot qualify the MBP's iCloud session.
    """
    backend = make_backend(config.get("backend", {}))
    if not isinstance(backend, ICloudBackend):
        raise refused("ICLOUD_REQUIRED", "pending-transfer checks require the iCloud backend")
    deadline = Deadline(clock() + min(backend.timeout_s, 30), clock)
    clear = backend._uploaded(backend._run(["status", "com.apple.CloudDocs"], deadline))
    return {"clear": clear, "observed_epoch_s": clock(), "scope": "com.apple.CloudDocs"}


SSD_SCHEMA = "joulewise.span_offload_ssd.v1"


def require_ssd_receipt(receipt, plan, record, expected):
    """One receipt contract for both SSD-copy retries and MBP cleanup."""
    if receipt.get("schema") != SSD_SCHEMA or receipt.get("plan") != plan \
            or receipt.get("descriptor_sha256") != record["descriptor_sha256"] \
            or receipt.get("files") != expected or not number(receipt.get("verified_epoch_s")):
        raise refused("SSD_RECEIPT_INVALID", "SSD readback does not match this copy marker")


def require_ssd_mount(root):
    if not os.path.ismount(root) or os.stat(root).st_dev == os.stat(root.anchor).st_dev:
        raise refused("SSD_MOUNT", "--ssd-root must be the mounted external SSD, not a directory on the system disk")


def ssd_copy(config, plan, marker, ssd_root, *, clock=time.time):
    """Air: retain encrypted transport bytes on the mounted SSD; read back and publish a receipt.

    No archive is expanded. The receipt is a trusted courier record, like the copy marker; copy it
    to the MBP only after this command succeeds. It certifies a readback, not perpetual SSD health.
    """
    check_id(plan, "plan")
    expected = marker_files(marker, plan, icloud=True)
    root = Path(ssd_root)
    if not root.is_absolute() or ".." in root.parts:
        raise refused("SSD_MOUNT", "the SSD mount must be an absolute path")
    require_ssd_mount(root)
    check_output_paths(None, {"ssd_root": root})
    backend = make_backend(config.get("backend", {}))
    if not isinstance(backend, ICloudBackend) or backend.describe() != marker["backend"]:
        raise refused("ICLOUD_REQUIRED", "the SSD copy must use the marker's iCloud backend")
    deadline = Deadline(clock() + DEFAULT_BUDGET_S, clock)
    with _directory_no_links(root):
        archive_root = root / "span-archives"
        archive_root.mkdir(mode=0o700, exist_ok=True)
    with _directory_no_links(archive_root):
        final = archive_root / plan
        receipt = final / "ssd.ok.json"
        if os.path.lexists(final):
            with _directory_no_links(final):
                for kind, name in names(plan).items():
                    if _sha_size(final / name) != expected[kind]:
                        raise integrity("SSD_MISMATCH", "the existing SSD copy differs from the marker")
                require_ssd_receipt(read_record(receipt), plan, marker, expected)
            return str(receipt)
        with tempfile.TemporaryDirectory(prefix=f".{plan}.ssd-", dir=archive_root) as tmp:
            tmp = Path(tmp)
            for kind, name in names(plan).items():
                target = tmp / name
                backend.get(plan, name, target, deadline)
                with open_regular(target, "an SSD artifact", single_link=True) as handle:
                    os.fsync(handle.fileno())
                if _sha_size(target) != expected[kind]:
                    raise integrity("SSD_MISMATCH", "the SSD readback differs from the marker")
                target.chmod(0o400)
            write_marker(tmp / "ssd.ok.json", {"schema": SSD_SCHEMA, "plan": plan,
                         "descriptor_sha256": marker["descriptor_sha256"], "files": expected,
                         "destination": str(final), "verified_epoch_s": clock()})
            os.rename(tmp, final)
    return str(receipt)


def storage_alarm(config, plan):
    """Mail at <=60 decimal GB (20 GB above the 40 GB line). Never authorise eviction."""
    free = shutil.disk_usage(config["stage_root"])[2]
    if free > 60_000_000_000:
        return False
    recipient = config.get("lead_email", "")
    if not re.fullmatch(r"[A-Za-z0-9_.+%-]+@[A-Za-z0-9.-]+", recipient):
        raise refused("LEAD_EMAIL", "configure lead_email for the RL-174 storage alarm")
    try:
        result = subprocess.run(["/usr/bin/mail", "-s", "JouleWise disk space: " + plan, recipient],
                                input=f"plan={plan} free_bytes={free}; 40 GB line + 20 GB warning. No forced eviction.\n".encode(),
                                capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        raise unverified("STORAGE_MAIL_FAILED", "the lead's disk-space mail could not be sent") from None
    if result.returncode:
        raise unverified("STORAGE_MAIL_FAILED", "the lead's disk-space mail was refused")
    return True


def close_offload(config, plan, span_dir, *, ssd_receipt=None, deadline_epoch=None, clock=time.time):
    """Explicit RL-174 D.2 close, after the desk bundle is pushed and the MBP desk is final.

    A verified pack permits raw deletion. Keep its materialised ciphertext until BOTH iCloud and
    a trusted SSD readback receipt are verified. No receipt means no wait for the Air and no eviction.
    """
    backend = make_backend(config.get("backend", {}))
    if not isinstance(backend, ICloudBackend):
        raise refused("ICLOUD_REQUIRED", "close requires observed iCloud readback")
    span_dir = Path(span_dir)
    check_output_paths(None, {"original": span_dir})  # never delete any repository
    if deadline_epoch is None:
        deadline_epoch = clock() + config.get("default_budget_s", DEFAULT_BUDGET_S)
    mailed = storage_alarm(config, plan)
    record = offload(config, plan, span_dir, deadline_epoch=deadline_epoch, clock=clock)
    if not record["provider_confirmed"]:
        raise OffloadError("ICLOUD_UNCONFIRMED", "the original and archive are retained", "unconfirmed")
    expected = marker_files(record, plan, icloud=True)
    deadline = Deadline(deadline_epoch, clock)
    stage = Path(config["stage_root"]) / plan
    with plan_lock(config["stage_root"], plan):
        # Validate the courier receipt BEFORE deleting or evicting anything.
        if ssd_receipt is not None:
            check_output_paths(span_dir, {"ssd_receipt": ssd_receipt})
            receipt = read_record(ssd_receipt)
            require_ssd_receipt(receipt, plan, record, expected)
        with _directory_no_links(stage):
            archive = stage / names(plan)["ciphertext"]
            if ssd_receipt is None and (not os.path.lexists(archive) or _sha_size(archive) != expected["ciphertext"]):
                raise refused("PACK_UNVERIFIED", "keep a materialised local archive while only iCloud is verified")
        if os.path.lexists(span_dir):
            found = _stage_complete(stage, plan)
            if found is None or found["descriptor_sha256"] != record["descriptor_sha256"] \
                    or found["descriptor"].get("pack_verification") != "stream per-file manifest match" \
                    or found["source"].get("source") != _real(span_dir):
                raise refused("PACK_UNVERIFIED", "a verified, materialised local pack is required before raw deletion")
            snapshot = span_snapshot(span_dir, deadline.remaining)
            manifest, digest, _size, _count = write_archive(span_dir, _NullSink(), deadline.remaining)
            if sha256_bytes(manifest) != record["manifest_sha256"] or digest != record["archive_sha256"]:
                raise refused("SPAN_CHANGED", "the original differs from the verified pack")
            require_snapshot(span_dir, snapshot, deadline.remaining)
            shutil.rmtree(span_dir)  # explicit close only; the low-level offload never deletes OUT
        if ssd_receipt is not None:
            deadline.remaining()
            name = names(plan)["ciphertext"]
            with backend._plan(plan) as (fd, directory):
                backend._run(["evict", str(directory / name)], deadline)
                backend._wait_flag(fd, name, True, deadline)
            archive = stage / name
            if os.path.lexists(archive):
                if _sha_size(archive) != expected["ciphertext"]:
                    raise refused("STAGE_CHANGED", "local archive changed; retained")
                archive.unlink()
        backend._wait_uploaded(deadline)
        if not mailed:
            mailed = storage_alarm(config, plan)
    return dict(record, original_deleted=True, archive_evicted=ssd_receipt is not None, storage_mail_sent=mailed)


def marker_path(marker_dir, plan, provider_confirmed):
    """The copy gate's ``<plan>.ok`` exists only after a provider-confirmed upload (RL-173 A.7).

    A transport without observed iCloud eviction/download (including legacy rclone) writes ``<plan>.ok.unconfirmed``,
    which no copy gate accepts.
    """
    return Path(marker_dir) / (f"{plan}.ok" if provider_confirmed else f"{plan}.ok.unconfirmed")


# --- pull (Air) --------------------------------------------------------------------------------------

def expectations(marker=None, manifest_sha256=None, ciphertext_sha256=None):
    """The hashes the pull must match: from the marker record, or the two RL-173 A.2 hashes given by hand."""
    expect = {}
    if marker is not None:
        if not isinstance(marker, dict) or marker.get("schema") != MARKER_SCHEMA:
            raise refused("MARKER_SCHEMA", "the marker is not a span_offload marker record")
        expect = {"manifest": marker.get("manifest_sha256"), "ciphertext": (marker.get("ciphertext") or {}).get("sha256"),
                  "wrapped_key": marker.get("wrapped_key_sha256"), "descriptor": marker.get("descriptor_sha256"),
                  "plan": marker.get("plan")}
    if manifest_sha256:
        if expect.get("manifest") not in (None, manifest_sha256):
            raise refused("EXPECT_CONFLICT", "--expect-manifest-sha256 differs from the marker")
        expect["manifest"] = manifest_sha256
    if ciphertext_sha256:
        if expect.get("ciphertext") not in (None, ciphertext_sha256):
            raise refused("EXPECT_CONFLICT", "--expect-ciphertext-sha256 differs from the marker")
        expect["ciphertext"] = ciphertext_sha256
    for kind in ("manifest", "ciphertext"):
        if not HEX64.fullmatch(expect.get(kind) or ""):
            raise refused("EXPECT_MISSING", f"the expected {kind} sha256 is missing or malformed")
    return expect


def _safe_members(tar, top):
    members, seen = [], set()
    for member in tar:
        name = member.name
        parts = name.split("/")
        if name.startswith("/") or ".." in parts or "" in parts[:-1] or parts[0] != top:
            raise integrity("ARCHIVE_PATH", "a member is outside the span's top directory")
        if not (member.isreg() or member.isdir()):
            raise integrity("ARCHIVE_MEMBER_TYPE", "a member is not a regular file or directory")
        if "." in parts:
            raise integrity("ARCHIVE_PATH", "a member name has a '.' component")
        try:
            for part in parts:
                if part:
                    _check_name(part, "the archive")
        except OffloadError:
            raise integrity("ARCHIVE_PATH", "a member name has a newline, backslash or bad encoding") from None
        folded = unicodedata.normalize("NFC", name.rstrip("/")).casefold()
        if folded in seen:
            raise integrity("ARCHIVE_DUPLICATE", "a member name appears twice (case and normalisation folded)")
        seen.add(folded)
        members.append(member)
    return members


def _read_only_below(tree):
    """Files 0444 and every directory 0555 except ``tree`` itself (which must stay writable to be moved)."""
    for root, dirnames, filenames in os.walk(tree, topdown=False):
        for name in filenames:
            os.chmod(Path(root) / name, 0o444)
        if Path(root) != Path(tree):
            os.chmod(root, 0o555)


PULL_SCHEMA = "joulewise.span_offload_pull.v1"


def landing_complete(done_path, plan, span_name):
    """A landing is complete only with a valid completion record naming this plan and span."""
    try:
        with open_regular(done_path, "the completion record", single_link=True) as handle:
            doc = json.loads(handle.read(65536))
    except (OffloadError, ValueError, OSError, RecursionError):
        return False
    return isinstance(doc, dict) and doc.get("schema") == PULL_SCHEMA and doc.get("plan") == plan \
        and doc.get("span_name") == span_name and HEX64.fullmatch(str(doc.get("manifest_sha256"))) is not None


def landing_names(span_name):
    return {"mbp": span_name + ".mbp.SHA256SUMS", "air": span_name + ".air.SHA256SUMS",
            "done": span_name + ".pull.ok"}


def pull(config, plan, kit, dest_root, expect, *, allow_local=False, deadline_epoch=None, clock=time.time):
    """Fetch, verify and decrypt one span into ``<dest_root>/<kit>/<span_name>/``, read-only.

    The landing is complete only when ``<span_name>.pull.ok`` exists (written last). A tree without it is
    an interrupted landing: the pull refuses it (``INCOMPLETE_LANDING``) and the lead moves it aside.
    """
    check_id(plan, "plan")
    check_id(kit, "kit")
    if expect.get("plan") not in (None, plan):
        raise refused("EXPECT_CONFLICT", "the marker names another plan")
    backend = make_backend(config.get("backend", {}), allow_local)
    openssl = config.get("openssl", "openssl")
    if deadline_epoch is not None and (not number(deadline_epoch) or deadline_epoch > clock() + MAX_DEADLINE_AHEAD_S):
        raise refused("BAD_DEADLINE", "the deadline is not a finite epoch within 24 h")
    deadline = Deadline(deadline_epoch, clock)
    dest_root = Path(dest_root)
    kit_dir = dest_root / kit
    work_root = Path(config["work_root"])
    if not dest_root.is_dir() or not work_root.is_dir():
        raise refused("DEST_ROOT", "the destination root or work root is not a directory")
    controls = {"dest_root": dest_root, "work_root": work_root, "identity": config["identity"]}
    if isinstance(backend, ICloudBackend):
        controls["backend root"] = backend.root
    if isinstance(backend, RcloneBackend):
        controls["rclone_config"] = backend.config
    check_output_paths(None, controls)
    if isinstance(backend, RcloneBackend):
        with open_regular(backend.config, "the rclone config", single_link=True):
            pass
    if os.stat(dest_root).st_dev != os.stat(work_root).st_dev:
        raise refused("CONFIG", "work_root must be on the same filesystem as the destination root")
    if os.path.islink(kit_dir) or (os.path.lexists(kit_dir) and not kit_dir.is_dir()):
        raise refused("DEST_SYMLINK", "the kit directory is a symlink or not a directory")
    if os.path.lexists(kit_dir) and inside_git(kit_dir):
        raise refused("PATH_IN_REPOSITORY", "the kit directory is inside a git repository")
    files = names(plan)
    with tempfile.TemporaryDirectory(prefix=f".pull-{plan}-", dir=work_root) as tmp:
        tmp = Path(tmp)
        for kind in UPLOAD_ORDER:
            backend.get(plan, files[kind], tmp / files[kind], deadline)
        got = {kind: sha256_file(tmp / files[kind]) for kind in UPLOAD_ORDER}
        for kind in ("ciphertext", "manifest", "wrapped_key", "descriptor"):
            if expect.get(kind) and got[kind] != expect[kind]:
                raise integrity("HASH_MISMATCH", f"{files[kind]} differs from the expected sha256")
        try:
            descriptor = json.loads((tmp / files["descriptor"]).read_bytes())
            span_name = descriptor["span_name"]
            archive_sha = descriptor["archive"]["sha256"]
            for kind in ("ciphertext", "wrapped_key", "manifest"):
                entry = descriptor["files"][kind]
                if entry["name"] != files[kind] or entry["sha256"] != got[kind] \
                        or entry["size"] != os.stat(tmp / files[kind]).st_size:
                    raise integrity("DESCRIPTOR_MISMATCH", f"{files[kind]} differs from the descriptor")
            if descriptor["schema"] != DESCRIPTOR_SCHEMA or descriptor["plan"] != plan:
                raise integrity("DESCRIPTOR_MISMATCH", "schema or plan")
            if descriptor["scheme"]["recipient_sha256"] != config["recipient_sha256"]:
                raise integrity("RECIPIENT_MISMATCH", "the copy was encrypted to another key")
        except (ValueError, KeyError, TypeError, RecursionError):
            raise integrity("DESCRIPTOR_INVALID", "the descriptor is not a span_offload descriptor") from None
        try:
            check_id(span_name, "span_name")
            _check_name(span_name, "the descriptor")
            if not span_name_ok(span_name, plan):
                raise refused("PLAN_SPAN_MISMATCH", "span name")
        except OffloadError:
            raise integrity("DESCRIPTOR_INVALID", "the descriptor's span name is not a plain name") from None
        final = kit_dir / span_name
        side = {k: kit_dir / v for k, v in landing_names(span_name).items()}
        if os.path.lexists(final) and not landing_complete(side["done"], plan, span_name):
            raise OffloadError("INCOMPLETE_LANDING", "an interrupted landing exists; move it aside", "dest_exists")
        if os.path.lexists(final) or any(os.path.lexists(p) for p in side.values()):
            raise OffloadError("DEST_EXISTS", "the destination already exists; nothing changed", "dest_exists")
        passphrase = unwrap_passphrase(openssl, config["identity"], tmp / files["wrapped_key"])
        archive = tmp / "archive.tgz"
        decrypt_file(openssl, passphrase, tmp / files["ciphertext"], archive, deadline)
        del passphrase
        if sha256_file(archive) != archive_sha:
            raise integrity("ARCHIVE_MISMATCH", "the decrypted archive differs from the descriptor")
        extract = tmp / "extract"
        extract.mkdir()
        try:
            with tarfile.open(archive, "r:gz") as tar:
                members = _safe_members(tar, span_name)
                kwargs = {"filter": "data"} if hasattr(tarfile, "data_filter") else {}
                tar.extractall(extract, members=members, **kwargs)
        except (tarfile.TarError, EOFError, OSError, zlib.error):
            raise integrity("ARCHIVE_INVALID", "the archive could not be read") from None
        archive.unlink()
        tree = extract / span_name
        if sorted(os.listdir(extract)) != [span_name] or not tree.is_dir():
            raise integrity("ARCHIVE_PATH", "the archive does not hold exactly the span's top directory")
        manifest = (tmp / files["manifest"]).read_bytes()
        try:
            air_manifest = hash_tree(tree, deadline.remaining if deadline else None)
        except OffloadError as error:
            if error.exit_kind != "refused":
                raise
            raise integrity("ARCHIVE_INVALID", f"the extracted tree: {error.code}") from None
        if air_manifest != manifest:
            raise integrity("MANIFEST_MISMATCH", "the extracted files differ from the plaintext manifest")
        _read_only_below(tree)
        kit_dir.mkdir(exist_ok=True)
        if os.path.islink(kit_dir):
            raise refused("DEST_SYMLINK", "the kit directory became a symlink")
        if os.path.lexists(final):
            raise OffloadError("DEST_EXISTS", "the destination appeared during the pull", "dest_exists")
        os.rename(tree, final)
        os.chmod(final, 0o555)
        for which, data in (("mbp", manifest), ("air", air_manifest)):
            with open(side[which], "xb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(side[which], 0o444)
        # The completion record last, complete and atomic (link of a synced temporary file, as the marker).
        write_marker(side["done"], {"schema": PULL_SCHEMA, "plan": plan, "span_name": span_name,
                                    "manifest_sha256": got["manifest"], "ciphertext_sha256": got["ciphertext"],
                                    "pulled_epoch_s": round(clock(), 3)})
        os.chmod(side["done"], 0o444)
    return {"plan": plan, "kit": kit, "span_name": span_name, "dest": str(final),
            "manifest_sha256": got["manifest"], "ciphertext_sha256": got["ciphertext"],
            "files": manifest.count(b"\n")}


# --- keygen (Air) ------------------------------------------------------------------------------------

def keygen(openssl, out_dir, bits=4096):
    """Write ``span-offload.key.pem`` (0600) and ``span-offload.pub.pem``; return the pinned fingerprint."""
    out_dir = Path(out_dir)
    if inside_git(out_dir):
        raise refused("PATH_IN_REPOSITORY", "the key directory is inside a git repository")
    out_dir.mkdir(mode=0o700, exist_ok=True)
    if out_dir.is_symlink() or not out_dir.is_dir():
        raise refused("KEY_DIRECTORY", "the key directory must be a real private directory")
    private, public = out_dir / "span-offload.key.pem", out_dir / "span-offload.pub.pem"
    if os.path.lexists(private) or os.path.lexists(public):
        raise refused("KEY_EXISTS", "a key file already exists; nothing written")
    old = os.umask(0o077)
    try:
        _openssl_run(openssl, ["genpkey", "-algorithm", "RSA", "-pkeyopt", f"rsa_keygen_bits:{bits}",
                               "-out", str(private)])
    finally:
        os.umask(old)
    os.chmod(private, 0o600)
    _openssl_run(openssl, ["pkey", "-in", str(private), "-pubout", "-out", str(public)])
    os.chmod(public, 0o644)
    return public_key_fingerprint(openssl, public)[0]
