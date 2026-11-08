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

WORKER_COUNTS = (1, 2, 4, 8)
CHUNK_BYTES = 1024 * 1024


def _stream_sha256(path: Path, *, expected=None) -> str:
    expected = _identity(path.stat()) if expected is None else expected
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        if _identity(os.fstat(handle.fileno())) != expected:
            raise OSError("file changed while hashing")
        while chunk := handle.read(CHUNK_BYTES):
            digest.update(chunk)
        if _identity(os.fstat(handle.fileno())) != expected:
            raise OSError("file changed while hashing")
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


class FileHashes:
    """Operation-local incremental hashes, with ordered, bounded file workers."""

    def __init__(self, workers=1):
        if type(workers) is not int or workers not in WORKER_COUNTS:
            raise ValueError("hash workers must be 1, 2, 4 or 8")
        self.workers = workers
        self._cache = {}

    def sha256(self, path):
        path = Path(path).absolute()
        before = _fingerprint(path)
        cached = self._cache.get(path)
        if cached is not None and cached[0] == before:
            return cached[1]
        digest = _stream_sha256(path, expected=before[1])
        if _fingerprint(path) != before:
            raise OSError("file changed while hashing")
        # Failures/interruption never publish a digest. A changed file is
        # re-read; deletions and read errors propagate to the owning refusal.
        self._cache[path] = (before, digest)
        return digest

    def map(self, function, items):
        """Consume results/errors in input order; at most workers reads queued.

        Shut down and join all readers on exceptions or generator close. No
        background hashing survives publication, interruption or a return.
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
    return _active_hashes.get() or FileHashes()
