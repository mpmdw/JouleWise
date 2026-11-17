"""Durable publication of small byte artifacts in an existing directory.

Writers share the artifact's application lock with recovery. Readers need
no lock. The directory is trusted and reserved temp names belong to this module.
"""

import errno
import hashlib
import os
import stat
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class Busy(Exception):
    """A publication is in progress or changed during this read."""


class Absent(FileNotFoundError):
    """No published artifact was found."""


class Unsafe(ValueError):
    """The artifact or its temporary names violate the publication protocol."""


def checkpoint(name: str) -> None:
    """A no-op production hook for named crash and fault injection."""


@contextmanager
def _directory(path: Path) -> Iterator[int]:
    if path.name in {"", ".."}:
        raise ValueError("an artifact filename is required")
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        yield fd
    finally:
        os.close(fd)


def _prefix(name: str) -> str:
    digest = hashlib.sha256(os.fsencode(name)).hexdigest()
    return f".jw-publish-{digest}-"


def _temps(directory: int, name: str) -> Iterator[str]:
    prefix = _prefix(name)
    for candidate in os.listdir(directory):
        if candidate.startswith(prefix) and candidate.endswith(".tmp"):
            token = candidate[len(prefix):-4]
            if len(token) == 32 and all(ch in "0123456789abcdef" for ch in token):
                yield candidate


def _stat(directory: int, name: str) -> os.stat_result | None:
    try:
        return os.stat(name, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        return None


def _same(left: os.stat_result, right: os.stat_result | None) -> bool:
    return right is not None and os.path.samestat(left, right)


def _publish(path: Path, data: bytes, *, once: bool) -> None:
    with _directory(path) as directory:
        temp = f"{_prefix(path.name)}{uuid.uuid4().hex}.tmp"
        fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=directory)
        with os.fdopen(fd, "wb") as stream:
            checkpoint("durable.temp_created")
            stream.write(data)
            stream.flush()
            checkpoint("durable.temp_written")
            os.fsync(stream.fileno())
            checkpoint("durable.file_synced")
        if once:
            try:
                os.link(temp, path.name, src_dir_fd=directory, dst_dir_fd=directory,
                        follow_symlinks=False)
            except FileExistsError:
                os.unlink(temp, dir_fd=directory)
                raise
            checkpoint("durable.linked")
            os.fsync(directory)
            checkpoint("durable.link_synced")
            os.unlink(temp, dir_fd=directory)
            checkpoint("durable.temp_unlinked")
        else:
            os.replace(temp, path.name, src_dir_fd=directory, dst_dir_fd=directory)
            checkpoint("durable.replaced")
        os.fsync(directory)
        checkpoint("durable.directory_synced")


def publish_once(path: Path, data: bytes) -> None:
    """Publish bytes without replacing an existing entry."""
    _publish(path, data, once=True)


def replace(path: Path, data: bytes) -> None:
    """Atomically replace or create an artifact with fsynced bytes."""
    _publish(path, data, once=False)


def finish_publication(path: Path) -> None:
    """Reconcile one artifact's temps while holding its writer lock.

    A linked temp proves that publication reached its commit point. Sync the
    directory before removing that link. Discard unlinked temps, which may
    contain incomplete bytes. Repeat the directory sync even with no temps,
    since the previous attempt may have failed its final sync.
    """
    with _directory(path) as directory:
        target = _stat(directory, path.name)
        if target is not None and not stat.S_ISREG(target.st_mode):
            raise Unsafe("published artifact is not a regular file")
        candidates = list(_temps(directory, path.name))
        linked = 0
        for name in candidates:
            temp = _stat(directory, name)
            if temp is None or not stat.S_ISREG(temp.st_mode):
                raise Unsafe("publication temp is not a regular file")
            if _same(temp, target):
                linked += 1
            elif temp.st_nlink != 1:
                raise Unsafe("publication temp has unexpected links")
        if target is not None and target.st_nlink != linked + 1:
            raise Unsafe("published artifact has unexpected links")
        if linked:
            os.fsync(directory)
        for name in candidates:
            os.unlink(name, dir_fd=directory)
        os.fsync(directory)


def _check_links(directory: int, name: str, fd: int, record: os.stat_result) -> None:
    if record.st_nlink == 1:
        return
    for temp in _temps(directory, name):
        if _same(record, _stat(directory, temp)):
            raise Busy("publication still has a temporary link")
    current = os.fstat(fd)
    if current.st_nlink != record.st_nlink or not _same(record, _stat(directory, name)):
        raise Busy("publication changed during the read")
    raise Unsafe("published artifact has unexpected links")


def read_published(path: Path, limit: int) -> bytes:
    """Read at most *limit* bytes from a stable regular artifact."""
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    with _directory(path) as directory:
        record = _stat(directory, path.name)
        if record is None:
            raise Absent(errno.ENOENT, os.strerror(errno.ENOENT), path)
        if not stat.S_ISREG(record.st_mode):
            raise Unsafe("published artifact is not a regular file")
        try:
            fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                         dir_fd=directory)
        except FileNotFoundError as error:
            raise Busy("publication changed during the read") from error
        except OSError as error:
            if error.errno == errno.ELOOP:
                raise Unsafe("published artifact became a symbolic link") from error
            raise
        with os.fdopen(fd, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if not _same(record, opened):
                raise Busy("publication changed during the read")
            _check_links(directory, path.name, fd, opened)
            if opened.st_size > limit:
                raise Unsafe("published artifact exceeds the read limit")
            data = stream.read(limit + 1)
            if len(data) > limit:
                raise Unsafe("published artifact exceeds the read limit")
            return data
