"""Span cloud offload (RL-173 A): bytes only, public-key encrypted, synchronous upload, verified marker.

The measurement Mac (MBP) offloads each closed span's output directory (OUT) to a private cloud folder
and writes the copy marker itself, so it never waits for the Air. The Air later pulls the copy, checks it
against the marker's hashes and decrypts it read-only into its desk tree.

Bytes only (RL-173 A.4): no file under OUT is parsed. Each regular file is read once, as bytes, into the
archive; the plaintext manifest is the sha256 of exactly those bytes. Nothing under OUT is changed or
deleted (A.5). Nothing is written to the repository (A.6): the tool has no git step.

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
rclone backend, ``rclone``. Exit codes are in ``EXIT``.
"""
from __future__ import annotations

import contextlib
import fcntl
import gzip
import hashlib
import io
import json
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


def manifest_bytes(digests):
    """``digests`` maps relative path -> sha256 hex. Output matches ``shasum -a 256`` on ``./path``."""
    return "".join(f"{digests[rel]}  ./{rel}\n" for rel in sorted(digests, key=lambda r: r.encode("utf-8"))).encode()


def hash_tree(span_dir):
    """The manifest of a tree on disk (used by the pull and by tests)."""
    _, files = walk_span(span_dir)
    return manifest_bytes({rel: sha256_file(Path(span_dir) / rel) for rel in files})


class _HashingWriter(io.RawIOBase):
    def __init__(self, sink):
        self.sink = sink
        self.hash = hashlib.sha256()
        self.size = 0

    def writable(self):
        return True

    def write(self, data):
        view = memoryview(data)
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


def write_archive(span_dir, sink):
    """Stream OUT as a gzip tar into ``sink``; return (manifest bytes, archive sha256, archive size, file count).

    Each file is read exactly once; the manifest hashes those same bytes. A file whose size or mtime moves
    while it is read refuses the offload (``SPAN_CHANGED``).
    """
    span_dir = Path(span_dir)
    top = span_dir.name
    _check_name(top, "the span's parent")
    dirs, files = walk_span(span_dir)
    writer = _HashingWriter(sink)
    digests = {}
    with gzip.GzipFile(filename="", mode="wb", fileobj=writer, compresslevel=GZIP_LEVEL, mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w|", format=tarfile.PAX_FORMAT) as tar:
            info = tarfile.TarInfo(top)
            info.type, info.mode, info.mtime = tarfile.DIRTYPE, 0o755, int(os.lstat(span_dir).st_mtime)
            tar.addfile(info)
            for rel in dirs:
                info = tarfile.TarInfo(f"{top}/{rel}")
                info.type, info.mode = tarfile.DIRTYPE, 0o755
                info.mtime = int(os.lstat(span_dir / rel).st_mtime)
                tar.addfile(info)
            for rel in files:
                digests[rel] = _add_file(tar, span_dir / rel, f"{top}/{rel}")
    return manifest_bytes(digests), writer.hash.hexdigest(), writer.size, len(files)


def _add_file(tar, path, arcname):
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
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
        if handle.read(1) or (after.st_size, after.st_mtime_ns) != (before.st_size, before.st_mtime_ns):
            raise refused("SPAN_CHANGED", "a file changed while it was archived")
        return reader.hash.hexdigest()


# --- openssl ---------------------------------------------------------------------------------------

def _openssl_run(openssl, args, *, input=None, deadline=None, cap=600):
    try:
        proc = subprocess.run([openssl, *args], input=input, capture_output=True,
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
    return fingerprint


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
                                    pass_fds=(read_end,))
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
            result = write_archive(span_dir, proc.stdin)
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
    if rc:
        raise refused("OPENSSL_FAILED", f"openssl enc rc={rc}")
    return result


def wrap_passphrase(openssl, public_key, passphrase, out_path, deadline=None):
    wrapped = _openssl_run(openssl, ["pkeyutl", "-encrypt", "-pubin", "-inkey", str(public_key),
                                     "-pkeyopt", "rsa_padding_mode:oaep"], input=passphrase, deadline=deadline)
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
                                  stderr=subprocess.DEVNULL, pass_fds=(read_end,),
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

    def put(self, local, plan, name, deadline=None):
        dest_dir = self.root / plan
        dest_dir.mkdir(exist_ok=True)
        dest = dest_dir / name
        local_sha = sha256_file(local)
        if dest.exists():
            if sha256_file(dest) != local_sha:
                raise unverified("REMOTE_CONFLICT", f"{name} exists with other bytes")
        else:
            tmp = dest_dir / f".{name}.part-{os.getpid()}"
            shutil.copyfile(local, tmp)
            with open(tmp, "rb") as handle:
                os.fsync(handle.fileno())
            os.replace(tmp, dest)
        size = os.stat(local).st_size
        remote_sha, remote_size = sha256_file(dest), os.stat(dest).st_size
        if (remote_sha, remote_size) != (local_sha, size):
            raise unverified("READBACK_MISMATCH", name)
        return {"name": name, "size": size, "sha256": local_sha, "provider_hash_type": "sha256",
                "provider_hash": remote_sha, "provider_size": remote_size, "kind": "local-readback"}

    def get(self, plan, name, dest, deadline=None):
        src = self.root / plan / name
        if not src.is_file():
            raise integrity("REMOTE_MISSING", name)
        shutil.copyfile(src, dest)


class RcloneBackend:
    """``rclone copyto`` (synchronous; it exits) then ``rclone lsjson --hash`` read back from the provider."""

    kind = "rclone"
    provider_confirmed = True

    def __init__(self, spec):
        self.rclone = spec.get("rclone", "rclone")
        self.config = spec.get("rclone_config")
        self.remote = spec["remote"]
        self.hash_type = spec.get("hash_type", "sha256")
        self.timeout_s = float(spec.get("timeout_s", 5400))
        self.readback_tries = int(spec.get("readback_tries", 3))
        self.readback_wait_s = float(spec.get("readback_wait_s", 10))
        if not isinstance(self.remote, str) or ":" not in self.remote or "\n" in self.remote:
            raise refused("CONFIG", "the rclone remote must look like name:path")
        if self.hash_type not in SIMPLE_HASHES + ("dropbox", "size"):
            raise refused("CONFIG", "hash_type must be sha256, sha1, md5, dropbox or size")

    def describe(self):
        return {"kind": self.kind, "remote": self.remote, "hash_type": self.hash_type}

    def _path(self, plan, name=None):
        base = self.remote if self.remote.endswith((":", "/")) else self.remote + "/"
        return base + plan + ("/" + name if name else "")

    def _run(self, args, deadline, cap=None):
        argv = [self.rclone]
        if self.config:
            argv += ["--config", self.config]
        argv += ["--retries", "3", "--low-level-retries", "10", "--contimeout", "60s", "--timeout", "300s",
                 "--stats", "0", "-q", *args]
        timeout = deadline.remaining(cap or self.timeout_s) if deadline else (cap or self.timeout_s)
        try:
            proc = subprocess.run(argv, capture_output=True, stdin=subprocess.DEVNULL, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise unverified("UPLOAD_TIMEOUT", args[0]) from None
        except OSError:
            raise unverified("RCLONE_UNAVAILABLE", "the rclone binary could not run") from None
        if proc.returncode:
            raise unverified("RCLONE_FAILED", f"rclone {args[0]} rc={proc.returncode}")
        return proc.stdout

    def _local_hash(self, local, deadline):
        if self.hash_type in SIMPLE_HASHES:
            return sha256_file(local, self.hash_type)
        if self.hash_type == "dropbox":
            out = self._run(["hashsum", "dropbox", str(local)], deadline, cap=600).decode("ascii", "replace")
            return out.split()[0] if out.split() else ""
        return None

    def put(self, local, plan, name, deadline=None):
        size = os.stat(local).st_size
        local_sha = sha256_file(local)
        self._run(["copyto", "--immutable", str(local), self._path(plan, name)], deadline)
        expected = self._local_hash(local, deadline)
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
            rows = [row for row in json.loads(listing) if isinstance(row, dict) and row.get("Name") == name]
        except ValueError:
            raise unverified("READBACK_UNPARSEABLE", name) from None
        if len(rows) != 1:
            raise unverified("READBACK_MISSING", name)
        row = rows[0]
        provider_size = row.get("Size")
        if provider_size != size:
            raise unverified("READBACK_SIZE", name)
        provider_hash = (row.get("Hashes") or {}).get(self.hash_type) if expected is not None else None
        if expected is not None and provider_hash != expected:
            raise unverified("READBACK_HASH" if provider_hash else "READBACK_NO_HASH", name)
        return {"name": name, "size": size, "sha256": local_sha, "provider_hash_type": self.hash_type,
                "provider_hash": provider_hash, "provider_size": provider_size, "kind": "rclone-lsjson"}

    def get(self, plan, name, dest, deadline=None):
        try:
            self._run(["copyto", self._path(plan, name), str(dest)], deadline)
        except OffloadError as error:
            raise integrity("DOWNLOAD_FAILED", f"{name}: {error.code}") from None


BACKENDS = {"local": LocalBackend, "rclone": RcloneBackend}


def make_backend(spec, allow_local=False):
    if not isinstance(spec, dict) or spec.get("kind") not in BACKENDS:
        raise refused("CONFIG", "backend.kind must be local or rclone")
    if spec["kind"] == "local" and not allow_local:
        raise refused("LOCAL_BACKEND_NOT_ALLOWED",
                      "the local backend has no provider confirmation; pass --allow-local-backend (tests/interim)")
    return BACKENDS[spec["kind"]](spec)


# --- configs ---------------------------------------------------------------------------------------

MBP_KEYS = {"schema", "recipient_public_key", "recipient_sha256", "stage_root", "marker_dir", "backend", "openssl"}
AIR_KEYS = {"schema", "identity", "recipient_sha256", "work_root", "backend", "openssl"}


def load_config(path, schema, keys, required):
    try:
        doc = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        raise refused("CONFIG", "the config file is missing or not JSON") from None
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
                      ("recipient_public_key", "recipient_sha256", "stage_root", "marker_dir", "backend"))
    return _absolute(doc, ("recipient_public_key", "stage_root", "marker_dir"))


def load_air_config(path):
    doc = load_config(path, AIR_CONFIG_SCHEMA, AIR_KEYS, ("identity", "recipient_sha256", "work_root", "backend"))
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
    """A stage is complete only when its descriptor (written last) exists and every file matches it."""
    descriptor_path = stage / names(plan)["descriptor"]
    if not descriptor_path.is_file():
        return None
    try:
        descriptor = json.loads(descriptor_path.read_bytes())
        for kind in ("ciphertext", "wrapped_key", "manifest"):
            entry = descriptor["files"][kind]
            path = stage / entry["name"]
            if entry["name"] != names(plan)[kind] or sha256_file(path) != entry["sha256"] \
                    or os.stat(path).st_size != entry["size"]:
                return None
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return descriptor


def build_stage(config, plan, span_dir, openssl, recipient_pem, deadline, clock=time.time):
    """Build the four files, or reuse a complete stage of the SAME source whose bytes have not changed.

    A complete stage of another source, of another recipient, or of a source whose bytes moved since is
    refused (``STAGE_CONFLICT``); an incomplete stage (no descriptor: nothing was uploaded from it) is set
    aside as ``<plan>.partial-<epoch>``.
    """
    stage_root = Path(config["stage_root"])
    stage = stage_root / plan
    files = names(plan)
    source = _real(span_dir)
    if stage.exists():
        descriptor = _stage_complete(stage, plan)
        if descriptor is None:
            stage.rename(stage_root / f"{plan}.partial-{int(clock())}")
        else:
            try:
                recorded = json.loads((stage / SOURCE_RECORD).read_bytes())
            except (OSError, ValueError):
                recorded = None
            if not isinstance(recorded, dict) or recorded.get("source") != source \
                    or descriptor.get("span_name") != Path(span_dir).name \
                    or descriptor.get("scheme", {}).get("recipient_sha256") != config["recipient_sha256"]:
                raise refused("STAGE_CONFLICT", "a complete stage of another source or recipient exists for this plan")
            if hash_tree(span_dir) != (stage / files["manifest"]).read_bytes():
                raise refused("STAGE_CONFLICT", "the span's bytes changed since the stage was built")
            return stage, descriptor, True
    stage.mkdir(mode=0o700)
    (stage / SOURCE_RECORD).write_bytes(canonical({"source": source}))
    passphrase = secrets.token_hex(32).encode("ascii")
    manifest, archive_sha, archive_size, count = encrypt_span(openssl, span_dir, passphrase,
                                                              stage / files["ciphertext"], deadline)
    wrap_passphrase(openssl, recipient_pem, passphrase, stage / files["wrapped_key"], deadline)
    del passphrase
    (stage / files["manifest"]).write_bytes(manifest)
    descriptor = {
        "schema": DESCRIPTOR_SCHEMA, "plan": plan, "span_name": Path(span_dir).name,
        "created_epoch_s": round(clock(), 3),
        "scheme": {"archive": "tar+gzip", "cipher": CIPHER, "kdf": "pbkdf2-sha256", "kdf_iter": KDF_ITER,
                   "passphrase": "256-bit random, hex", "wrap": "rsa-oaep", "recipient_sha256": config["recipient_sha256"]},
        "archive": {"sha256": archive_sha, "size": archive_size},
        "manifest": {"files": count},
        "files": {kind: {"name": files[kind], "sha256": sha256_file(stage / files[kind]),
                         "size": os.stat(stage / files[kind]).st_size}
                  for kind in ("ciphertext", "wrapped_key", "manifest")},
    }
    tmp = stage / (files["descriptor"] + ".tmp")
    tmp.write_bytes(canonical(descriptor))
    os.replace(tmp, stage / files["descriptor"])
    return stage, descriptor, False


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


def offload(config, plan, span_dir, *, require_files=(), allow_local=False, deadline_epoch=None,
            clock=time.time):
    """Run the whole MBP side. Returns the marker record. Raises ``OffloadError``."""
    check_id(plan, "plan")
    span_dir = Path(span_dir)
    check_id(span_dir.name, "span directory name")
    marker_dir = Path(config["marker_dir"])
    stage_root = Path(config["stage_root"])
    if not marker_dir.is_dir() or not stage_root.is_dir():
        raise refused("CONFIG", "the marker directory or the stage root does not exist")
    if os.path.lexists(marker_path(marker_dir, plan, True)):
        raise OffloadError("MARKER_EXISTS", "the marker already exists; nothing done", "marker_exists")
    backend = make_backend(config["backend"], allow_local)
    walk_span(span_dir)  # refuse links/special files, and a missing or symlinked span, before anything else
    outputs = {"stage_root": stage_root, "marker_dir": marker_dir,
               "recipient_public_key": config["recipient_public_key"]}
    if isinstance(backend, LocalBackend):
        outputs["backend root"] = backend.root
    check_output_paths(span_dir, outputs)
    openssl = config.get("openssl", "openssl")
    deadline = Deadline(deadline_epoch, clock)
    for name in require_files:
        _check_name(name, "--require-file")
        if "/" in name or not os.path.isfile(span_dir / name) or os.path.islink(span_dir / name):
            raise refused("SPAN_NOT_CLOSED", f"required file {name} is absent")
    with plan_lock(stage_root, plan), tempfile.TemporaryDirectory(prefix=f".{plan}.key-", dir=stage_root) as keydir:
        # One snapshot of the public key: the fingerprint, the size check and the wrap all use these bytes.
        recipient_pem = Path(keydir) / "recipient.pem"
        try:
            recipient_pem.write_bytes(Path(config["recipient_public_key"]).read_bytes())
        except OSError:
            raise refused("RECIPIENT_UNREADABLE", "the recipient public key cannot be read") from None
        recipient = check_recipient(openssl, recipient_pem, config["recipient_sha256"], deadline)
        stage, descriptor, reused = build_stage(config, plan, span_dir, openssl, recipient_pem, deadline, clock)
        files = names(plan)
        expected = {kind: (sha256_file(stage / files[kind]), os.stat(stage / files[kind]).st_size)
                    for kind in UPLOAD_ORDER}
        for kind in ("ciphertext", "wrapped_key", "manifest"):
            if expected[kind] != (descriptor["files"][kind]["sha256"], descriptor["files"][kind]["size"]):
                raise unverified("STAGE_CHANGED", f"{files[kind]} differs from the descriptor")
        deadline.remaining()
        confirmations = [backend.put(stage / files[kind], plan, files[kind], deadline) for kind in UPLOAD_ORDER]
        for kind, row in zip(UPLOAD_ORDER, confirmations):
            if (row["sha256"], row["size"]) != expected[kind] or row["provider_size"] != expected[kind][1]:
                raise unverified("STAGE_CHANGED", f"{files[kind]} changed during the upload")
        record = {
            "schema": MARKER_SCHEMA, "plan": plan, "path": "cloud-offload", "span_name": descriptor["span_name"],
            "written_at": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(clock())),
            "written_epoch_s": round(clock(), 3), "stage_reused": reused,
            "backend": backend.describe(), "provider_confirmed": backend.provider_confirmed,
            "recipient_sha256": recipient,
            "manifest_sha256": expected["manifest"][0], "manifest_files": descriptor["manifest"]["files"],
            "ciphertext": {"sha256": expected["ciphertext"][0], "size": expected["ciphertext"][1]},
            "wrapped_key_sha256": expected["wrapped_key"][0],
            "descriptor_sha256": expected["descriptor"][0],
            "archive_sha256": descriptor["archive"]["sha256"],
            "provider_confirmation": confirmations,
        }
        deadline.remaining()  # the last check before the marker
        write_marker(marker_path(marker_dir, plan, backend.provider_confirmed), record)
    return record


def marker_path(marker_dir, plan, provider_confirmed):
    """The copy gate's ``<plan>.ok`` exists only after a provider-confirmed upload (RL-173 A.7).

    A backend without a provider read-back (``local``: tests, a sync folder) writes ``<plan>.ok.unconfirmed``,
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
        if name.rstrip("/") in seen:
            raise integrity("ARCHIVE_DUPLICATE", "a member name appears twice")
        seen.add(name.rstrip("/"))
        members.append(member)
    return members


def _read_only_below(tree):
    """Files 0444 and every directory 0555 except ``tree`` itself (which must stay writable to be moved)."""
    for root, dirnames, filenames in os.walk(tree, topdown=False):
        for name in filenames:
            os.chmod(Path(root) / name, 0o444)
        if Path(root) != Path(tree):
            os.chmod(root, 0o555)


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
    backend = make_backend(config["backend"], allow_local)
    openssl = config.get("openssl", "openssl")
    deadline = Deadline(deadline_epoch, clock)
    dest_root = Path(dest_root)
    kit_dir = dest_root / kit
    work_root = Path(config["work_root"])
    if not dest_root.is_dir() or not work_root.is_dir():
        raise refused("DEST_ROOT", "the destination root or work root is not a directory")
    check_output_paths(None, {"dest_root": dest_root, "work_root": work_root})
    if os.path.islink(kit_dir) or (os.path.lexists(kit_dir) and not kit_dir.is_dir()):
        raise refused("DEST_SYMLINK", "the kit directory is a symlink or not a directory")
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
        except (ValueError, KeyError, TypeError):
            raise integrity("DESCRIPTOR_INVALID", "the descriptor is not a span_offload descriptor") from None
        check_id(span_name, "span_name")
        final = kit_dir / span_name
        side = {k: kit_dir / v for k, v in landing_names(span_name).items()}
        if os.path.lexists(final) and not os.path.lexists(side["done"]):
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
        air_manifest = hash_tree(tree)
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
        for which, data in (("mbp", manifest), ("air", air_manifest),
                            ("done", canonical({"schema": "joulewise.span_offload_pull.v1", "plan": plan,
                                                "span_name": span_name, "manifest_sha256": got["manifest"],
                                                "ciphertext_sha256": got["ciphertext"],
                                                "pulled_epoch_s": round(clock(), 3)}))):
            with open(side[which], "xb") as handle:
                handle.write(data)
            os.chmod(side[which], 0o444)
    return {"plan": plan, "kit": kit, "span_name": span_name, "dest": str(final),
            "manifest_sha256": got["manifest"], "ciphertext_sha256": got["ciphertext"],
            "files": manifest.count(b"\n")}


# --- keygen (Air) ------------------------------------------------------------------------------------

def keygen(openssl, out_dir, bits=4096):
    """Write ``span-offload.key.pem`` (0600) and ``span-offload.pub.pem``; return the pinned fingerprint."""
    out_dir = Path(out_dir)
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
