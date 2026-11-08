"""Bounded streaming hashes for one closed-file reporting/copy operation.

No persisted cache is trusted. Callers must keep destination authentication in
a separate FileHashes instance, and must not use this cache for live admission
or measurement. A fresh operation always reads every byte again.
"""
from __future__ import annotations

from collections import deque
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
import os
from pathlib import Path
import sys
import time

WORKER_COUNTS = (1, 2, 4, 8)
CHUNK_BYTES = 1024 * 1024
HASH_RETRIES = 3
RETRY_BACKOFF_S = 0.01


class _FileChanged(OSError):
    """Only observed identity changes are retryable, not arbitrary I/O errors."""


def _filesystem_type(path):
    """Darwin statfs; unknown platforms/filesystems must never enable reuse."""
    if sys.platform != "darwin":
        return None
    import ctypes

    class StatFS(ctypes.Structure):
        _fields_ = [
            ("bsize", ctypes.c_uint32), ("iosize", ctypes.c_int32),
            ("blocks", ctypes.c_uint64), ("bfree", ctypes.c_uint64),
            ("bavail", ctypes.c_uint64), ("files", ctypes.c_uint64),
            ("ffree", ctypes.c_uint64), ("fsid", ctypes.c_int32 * 2),
            ("owner", ctypes.c_uint32), ("type", ctypes.c_uint32),
            ("flags", ctypes.c_uint32), ("fssubtype", ctypes.c_uint32),
            ("fstypename", ctypes.c_char * 16),
            ("mntonname", ctypes.c_char * 1024),
            ("mntfromname", ctypes.c_char * 1024),
            ("flags_ext", ctypes.c_uint32), ("reserved", ctypes.c_uint32 * 7),
        ]

    try:
        statfs = ctypes.CDLL("/usr/lib/libSystem.B.dylib").statfs
        statfs.argtypes = [ctypes.c_char_p, ctypes.POINTER(StatFS)]
        statfs.restype = ctypes.c_int
        info = StatFS()
        if statfs(os.fsencode(path), ctypes.byref(info)) == 0:
            return info.fstypename.decode("ascii")
    except (OSError, AttributeError, UnicodeError):
        pass
    return None


def _stream_sha256(path: Path, *, expected=None) -> str:
    if expected is None:
        # Admission callers also get bounded stable-snapshot retries, but
        # never consult an operation's terminal cache.
        return _stable_hash(Path(path), _read_sha256)[1]
    return _read_sha256(path, expected=expected)


def _read_sha256(path: Path, *, expected) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        if _identity(os.fstat(handle.fileno())) != expected:
            raise _FileChanged(f"file changed while hashing: {path}")
        while chunk := handle.read(CHUNK_BYTES):
            digest.update(chunk)
        if _identity(os.fstat(handle.fileno())) != expected:
            raise _FileChanged(f"file changed while hashing: {path}")
    return digest.hexdigest()


def _identity(st):
    # ctime detects writes that restore both length and mtime; device/inode
    # detect replacement. atime deliberately excluded (our own reads change it).
    return (st.st_dev, st.st_ino, st.st_mode, st.st_nlink, st.st_size,
            st.st_mtime_ns, st.st_ctime_ns)


def _fingerprint(path):
    # Retain the caller's symlink policy: night records historically hash the
    # target; harvest inventories store literal link text without hashing it.
    return _identity(path.lstat()), _identity(path.stat())


def _stable_hash(path, read, *, before=None):
    # One initial attempt plus at most three retries, each with a new
    # fingerprint and digest. Never retry missing files, permissions or INT.
    for attempt in range(HASH_RETRIES + 1):
        before = _fingerprint(path) if before is None else before
        try:
            digest = read(path, expected=before[1])
            if _fingerprint(path) != before:
                raise _FileChanged(f"file changed while hashing: {path}")
            return before, digest
        except _FileChanged as exc:
            if attempt == HASH_RETRIES:
                raise OSError(str(exc)) from exc
            time.sleep(RETRY_BACKOFF_S * (attempt + 1))
            before = None


class FileHashes:
    """Operation-local incremental hashes, with ordered, bounded file workers."""

    def __init__(self, workers=1):
        if type(workers) is not int or workers not in WORKER_COUNTS:
            raise ValueError("hash workers must be 1, 2, 4 or 8")
        self.workers = workers
        self._cache = {}
        self._filesystems = {}

    def _can_reuse(self, path, fingerprint):
        for location, identity in zip((path.parent, path), fingerprint):
            # Even on APFS, conservatively re-read files whose observed
            # mtime or ctime could have microsecond (or coarser) precision.
            if any(stamp % 1_000 == 0 for stamp in identity[-2:]):
                return False
            device = identity[0]
            if device not in self._filesystems:
                self._filesystems[device] = _filesystem_type(location)
            if self._filesystems[device] != "apfs":
                return False
        return True

    def sha256(self, path):
        path = Path(path).absolute()
        before = _fingerprint(path)
        cached = self._cache.get(path)
        reusable = self._can_reuse(path, before)
        if reusable and cached is not None and cached[0] == before:
            return cached[1]
        self._cache.pop(path, None)
        after, digest = _stable_hash(path, _stream_sha256, before=before)
        # Failures/interruption never publish a digest. A changed file is
        # re-read; deletions and read errors propagate to the owning refusal.
        if self._can_reuse(path, after):
            self._cache[path] = (after, digest)
        return digest

    def map(self, function, items):
        """Consume results/errors in input order; at most workers reads queued.

        Shut down and join all readers on exceptions or generator close. No
        background hashing survives publication, interruption or a return.
        INT/TERM can therefore wait for the largest in-flight file read.
        """
        if self.workers == 1:
            yield from map(function, items)
            return
        items = iter(items)
        with ThreadPoolExecutor(max_workers=self.workers, thread_name_prefix="custody-hash") as pool:
            pending = deque()
            try:
                for _ in range(self.workers):
                    try:
                        item = next(items)
                    except StopIteration:
                        break
                    pending.append(pool.submit(function, item))
                while pending:
                    yield pending.popleft().result()
                    try:
                        item = next(items)
                    except StopIteration:
                        continue
                    pending.append(pool.submit(function, item))
            finally:
                for future in pending:
                    future.cancel()


_active_hashes = ContextVar("closed_file_hashes", default=None)


@contextmanager
def hash_scope(workers=1):
    """Share only within this invocation's terminal result/publish sequence."""
    hashes = FileHashes(workers)
    token = _active_hashes.set(hashes)
    try:
        yield hashes
    finally:
        _active_hashes.reset(token)


def current_hashes():
    """New threads do not inherit the terminal scope; they get a fresh instance."""
    return _active_hashes.get() or FileHashes()
