"""Durable, race-resistant persistence for cold-gate validator receipts.

The validator emits one canonical receipt on standard output.  A convening
runner, rather than the validator, owns persistence.  This module supplies the
narrow write boundary for that runner without taking on judge handoff.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import secrets
import stat


_O_CLOEXEC = getattr(os, "O_CLOEXEC", 0)
_O_DIRECTORY = getattr(os, "O_DIRECTORY", 0)
_O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)


class ReceiptPublicationError(OSError):
    """A validator receipt was not confirmed as durably published."""


class ReceiptDirectoryChanged(ReceiptPublicationError):
    """The requested receipt directory stopped naming the opened directory."""


class ReceiptPublicationCollision(ReceiptPublicationError):
    """The requested receipt name already exists and was not overwritten."""


class ReceiptDurabilityUncertain(ReceiptPublicationError):
    """The receipt name was published but its directory sync failed."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"receipt publication durability is uncertain: {path}")


@dataclass(frozen=True)
class ReceiptPublication:
    """Confirmed result of one byte-exact validator-receipt publication."""

    path: Path
    sha256: str
    size_bytes: int


def _after_directory_open(directory_fd: int) -> None:
    """Test barrier after directory anchoring and before any write."""

    del directory_fd


def _validate_receipt_name(name: str) -> None:
    if (
        not isinstance(name, str)
        or not name
        or name in {".", ".."}
        or "/" in name
        or "\x00" in name
    ):
        raise ValueError("receipt name must be one nonempty directory entry")


def _same_directory(path: Path, opened: os.stat_result) -> bool:
    try:
        current = os.stat(path, follow_symlinks=False)
    except OSError:
        return False
    return (
        stat.S_ISDIR(current.st_mode)
        and current.st_dev == opened.st_dev
        and current.st_ino == opened.st_ino
    )


def _write_all(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        try:
            written = os.write(descriptor, view)
        except InterruptedError:
            continue
        if written <= 0:
            raise OSError("short validator-receipt write")
        view = view[written:]


def _open_temporary(directory_fd: int) -> tuple[int, str]:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | _O_NOFOLLOW | _O_CLOEXEC
    while True:
        name = f".cgv-receipt-{secrets.token_hex(16)}.tmp"
        try:
            return os.open(name, flags, 0o600, dir_fd=directory_fd), name
        except FileExistsError:
            continue


def persist_validator_receipt(
    directory: Path | str,
    name: str,
    receipt_bytes: bytes,
) -> ReceiptPublication:
    """Publish ``receipt_bytes`` once, atomically and durably.

    The destination directory is opened without following its final path
    component.  Every later namespace operation is relative to that held
    directory descriptor.  A private file is fully written and synced before
    an atomic hard-link operation publishes ``name`` without overwriting an
    existing entry.  The temporary name is then removed and the directory is
    synced.  A directory-sync error is reported as uncertain because the
    complete receipt may already be visible but crash durability is unproved.
    """

    _validate_receipt_name(name)
    if not isinstance(receipt_bytes, bytes):
        raise TypeError("validator receipt must be bytes")
    if not receipt_bytes:
        raise ValueError("validator receipt must not be empty")
    if not _O_DIRECTORY or not _O_NOFOLLOW:
        raise ReceiptPublicationError(
            "platform lacks O_DIRECTORY or O_NOFOLLOW for receipt custody"
        )

    receipt_directory = Path(directory)
    requested_path = receipt_directory / name
    directory_fd = -1
    temporary_fd = -1
    temporary_name: str | None = None
    published = False
    try:
        directory_fd = os.open(
            receipt_directory,
            os.O_RDONLY | _O_DIRECTORY | _O_NOFOLLOW | _O_CLOEXEC,
        )
        opened = os.fstat(directory_fd)
        if not stat.S_ISDIR(opened.st_mode):
            raise ReceiptPublicationError("receipt destination is not a directory")

        _after_directory_open(directory_fd)
        if not _same_directory(receipt_directory, opened):
            raise ReceiptDirectoryChanged(
                "receipt directory changed after it was opened"
            )

        temporary_fd, temporary_name = _open_temporary(directory_fd)
        _write_all(temporary_fd, receipt_bytes)
        os.fsync(temporary_fd)
        os.close(temporary_fd)
        temporary_fd = -1

        try:
            os.link(
                temporary_name,
                name,
                src_dir_fd=directory_fd,
                dst_dir_fd=directory_fd,
                follow_symlinks=False,
            )
        except FileExistsError as exc:
            raise ReceiptPublicationCollision(
                f"receipt already exists: {requested_path}"
            ) from exc
        published = True
        os.unlink(temporary_name, dir_fd=directory_fd)
        temporary_name = None

        try:
            os.fsync(directory_fd)
        except OSError as exc:
            raise ReceiptDurabilityUncertain(requested_path) from exc
        if not _same_directory(receipt_directory, opened):
            raise ReceiptDirectoryChanged(
                "receipt directory changed during publication"
            )

        return ReceiptPublication(
            path=requested_path,
            sha256=hashlib.sha256(receipt_bytes).hexdigest(),
            size_bytes=len(receipt_bytes),
        )
    except ReceiptPublicationError:
        raise
    except OSError as exc:
        if published:
            raise ReceiptPublicationError(
                f"receipt was published but publication did not complete: {requested_path}"
            ) from exc
        raise ReceiptPublicationError(
            f"validator receipt was not published: {requested_path}"
        ) from exc
    finally:
        if temporary_fd >= 0:
            try:
                os.close(temporary_fd)
            except OSError:
                pass
        if temporary_name is not None and directory_fd >= 0:
            try:
                os.unlink(temporary_name, dir_fd=directory_fd)
            except OSError:
                pass
        if directory_fd >= 0:
            try:
                os.close(directory_fd)
            except OSError:
                pass
