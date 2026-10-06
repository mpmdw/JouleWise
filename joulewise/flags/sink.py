"""Append-only flag files: one canonical JSON line per flag, fsync per line.

A :class:`FlagSink` never rewrites or truncates its file. It deduplicates by
``flag_id``: before each append it takes an exclusive ``flock`` on the file,
reads any bytes other writers appended since its last look, and skips the
append when the id is already present. A torn last line (a crash mid-write) is
left in place; the next append first writes a newline so the torn bytes stay a
line of their own, which :func:`read_flags` reports as a problem and skips.
"""

from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
from typing import Any, Iterable, Mapping

from joulewise.flags.schema import render_line, require_flag, validate_flag


def _fsync_directory(path: Path) -> None:
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


class FlagSink:
    """Append flags to ``path``; returns ``True`` from :meth:`append` when written."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._ids: set[str] = set()
        self._offset = 0
        self._partial = b""

    def _open(self) -> int:
        directory = self.path.parent
        created_directory = not directory.exists()
        directory.mkdir(parents=True, exist_ok=True)
        if created_directory:
            _fsync_directory(directory.parent)
        existed = self.path.exists()
        fd = os.open(self.path, os.O_RDWR | os.O_APPEND | os.O_CREAT, 0o644)
        if not existed:
            _fsync_directory(directory)
        return fd

    def _absorb(self, fd: int) -> None:
        """Read bytes appended since the last look and record their flag ids."""

        size = os.fstat(fd).st_size
        if size < self._offset:
            raise OSError(f"flag file {self.path} shrank; append-only file was truncated")
        if size == self._offset:
            return
        chunk = os.pread(fd, size - self._offset, self._offset)
        self._offset = size
        data = self._partial + chunk
        lines = data.split(b"\n")
        self._partial = lines.pop()
        for line in lines:
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if isinstance(value, Mapping) and isinstance(value.get("flag_id"), str):
                self._ids.add(value["flag_id"])

    def append(self, flag: Mapping[str, Any]) -> bool:
        require_flag(flag)
        line = render_line(flag)
        fd = self._open()
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            self._absorb(fd)
            if flag["flag_id"] in self._ids:
                return False
            if self._partial:
                # A torn line from an earlier crash: terminate it first.
                line = b"\n" + line
                self._partial = b""
            written = 0
            while written < len(line):
                written += os.write(fd, line[written:])
            os.fsync(fd)
            self._offset += len(line)
            self._ids.add(flag["flag_id"])
            return True
        finally:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)

    def extend(self, flags: Iterable[Mapping[str, Any]]) -> int:
        return sum(1 for flag in flags if self.append(flag))


def append_json_line(path: Path | str, record: Mapping[str, Any]) -> None:
    """Append one non-flag JSON record (collector run records) with fsync."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    existed = target.exists()
    raw = json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
        "utf-8"
    ) + b"\n"
    fd = os.open(target, os.O_RDWR | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        if os.fstat(fd).st_size:
            last = os.pread(fd, 1, os.fstat(fd).st_size - 1)
            if last != b"\n":
                raw = b"\n" + raw
        written = 0
        while written < len(raw):
            written += os.write(fd, raw[written:])
        os.fsync(fd)
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
    if not existed:
        _fsync_directory(target.parent)


def read_flags(path: Path | str) -> tuple[list[dict[str, Any]], list[str]]:
    """Every conforming flag (first occurrence per id) plus a problem per bad line.

    Reading never raises on content: a malformed record is a problem string,
    because a malformed record must never stop anything downstream.
    """

    target = Path(path)
    flags: list[dict[str, Any]] = []
    problems: list[str] = []
    seen: set[str] = set()
    try:
        raw = target.read_bytes()
    except FileNotFoundError:
        return flags, problems
    except OSError as exc:
        return flags, [f"{target}: unreadable: {exc}"]
    for number, line in enumerate(raw.split(b"\n"), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            problems.append(f"{target}:{number}: not JSON: {exc}")
            continue
        issues = validate_flag(value)
        if issues:
            problems.append(f"{target}:{number}: " + "; ".join(issues))
            continue
        if value["flag_id"] in seen:
            continue
        seen.add(value["flag_id"])
        flags.append(value)
    return flags, problems
