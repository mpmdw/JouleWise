"""Verified, temporary plain copies of desk-compressed run bundles.

Storage failures are program refusals, never evidence about a member.
"""
from __future__ import annotations

from contextlib import contextmanager, ExitStack
import fcntl
import hashlib
import math
import os
from pathlib import Path
import re
import shutil
import tempfile

from joulewise import desk_compress

# macOS began evicting ledger-referenced capture files to iCloud near 29 GiB
# free in the 2026-10-12 fault (RUN_STATE.md item 34). Stay above that onset;
# 40 GiB restores the earlier margin (11 GiB above the observed onset).
# restored_run adds the entire uncompressed run size before copying a byte.
MIN_RESERVE_GIB = 40


class StorageStop(BaseException):
    """Like KeyboardInterrupt, a storage or custody condition must stop the program.

    Ordinary handlers must not absorb it.
    """

    def __init__(self, reason):
        self.reason = str(reason).removeprefix("restore_refused: ")
        super().__init__(f"restore_refused: {self.reason}")


class RestoreRefused(StorageStop):
    """A storage/custody refusal that must terminate the consuming program."""


@contextmanager
def _restore_stack():
    stack = ExitStack()
    try:
        yield stack
    finally:
        try:
            stack.close()
        except OSError as exc:
            raise RestoreRefused(exc) from exc


@contextmanager
def restored_run(run_dir, scratch_dir, *, compression_records=None, reserve_gib=MIN_RESERVE_GIB,
                 _require_bundle=True):
    # Catch materialization failures only. Reader exceptions retain their identity.
    with _restore_stack() as stack:
        try:
            plain = stack.enter_context(_restored_run(run_dir, scratch_dir,
                compression_records=compression_records, reserve_gib=reserve_gib,
                _require_bundle=_require_bundle))
        except (OSError, ValueError) as exc:
            raise RestoreRefused(exc) from exc
        yield plain


def _records(path):
    if path is None:
        return {}
    path = Path(path)
    if path.name != "compression.jsonl":
        raise ValueError("compression-records must name compression.jsonl")
    if not path.is_file():
        raise ValueError("compressed run requires compression.jsonl")
    summary = {}
    rows = desk_compress.status(path.parent, summary=summary)
    # A damaged journal is insufficient custody evidence for a verified copy.
    if summary["manifest_lines_skipped"]:
        raise ValueError("invalid compression journal")
    records = {}
    for row in rows:
        if (not Path(row["path"]).is_absolute()
                or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])):
            raise ValueError("invalid compression record")
        records[Path(row["path"]).resolve()] = row
    return records


def _walk_error(error):
    raise error


def _inventory(source, records):
    entries, targets = [], set()
    for directory, dirs, files in os.walk(source, followlinks=False, onerror=_walk_error):
        for name in sorted(dirs + files):
            if (Path(directory) / name).is_symlink():
                raise ValueError("symlinks are not supported")
        dirs.sort()
        for name in sorted(files):
            path = Path(directory) / name
            if not path.is_file():
                raise ValueError("nonregular input")
            compressed = path.suffix == ".zst"
            logical = path.with_suffix("") if compressed else path
            relative = logical.relative_to(source)
            if relative in targets:
                raise ValueError("plain and compressed siblings are ambiguous")
            targets.add(relative)
            record = records.get(logical)
            if compressed and record is None:
                raise ValueError("compressed input has no digest record")
            size = record["size"] if record is not None else path.stat().st_size
            entries.append((path, relative, compressed, record, size))
    return entries


def _copy(stream, target, size, record):
    digest, count = hashlib.sha256(), 0
    with target.open("xb") as output:
        for chunk in iter(lambda: stream.read(desk_compress.CHUNK_BYTES), b""):
            count += len(chunk)
            if count > size:
                raise ValueError("restored size mismatch")
            digest.update(chunk)
            output.write(chunk)
    if count != size or (record is not None and digest.hexdigest() != record["sha256"]):
        raise ValueError("restored size or digest mismatch")


@contextmanager
def _restored_run(run_dir, scratch_dir, *, compression_records=None, reserve_gib=MIN_RESERVE_GIB,
                  _require_bundle=True):
    """Yield one private, plain bundle; clean it up on success or failure."""
    if not math.isfinite(reserve_gib) or reserve_gib < MIN_RESERVE_GIB:
        raise ValueError(f"reserve-gib must be finite and at least {MIN_RESERVE_GIB}")
    source = Path(run_dir)
    if source.is_symlink():
        raise ValueError("symlinks are not supported")
    source = source.resolve(strict=True)
    if not source.is_dir() or (_require_bundle and not any((source / name).is_file()
                                      for name in ("metadata.json", "metadata.json.zst"))):
        raise ValueError("run-dir must name one bundle containing metadata.json[.zst]")
    scratch = Path(scratch_dir).resolve()
    if source == scratch or source in scratch.parents or scratch in source.parents:
        raise ValueError("scratch and source must be separate trees")
    # The production layout is ARCHIVE/sources/{claim,bound}-runs/RUN.
    # Also recognize harvest.json when the caller uses another archive layout.
    protected = [source.parent, *(parent for parent in source.parents
                                 if (parent / "harvest.json").is_file())]
    protected.extend(parent.parent for parent in source.parents if parent.name == "sources")
    if any(scratch == parent or parent in scratch.parents for parent in protected):
        raise ValueError("scratch must be outside the archive")
    if compression_records is not None:
        record_dir = Path(compression_records).resolve().parent
        if scratch == record_dir or record_dir in scratch.parents:
            raise ValueError("scratch must be outside the compression records")
    entries = _inventory(source, _records(compression_records))
    scratch.mkdir(parents=True, exist_ok=True)
    # Reader and operator restores share the TMPDIR lock, even when the
    # operator chooses another scratch directory on the same filesystem.
    # Once copied, disk_usage includes these bytes; readers may then overlap.
    with ExitStack() as cleanup:
        with _scratch_lock(Path(tempfile.gettempdir())):
            required = sum(entry[4] for entry in entries)
            if shutil.disk_usage(scratch).free < required + reserve_gib * 1024**3:
                raise ValueError("insufficient scratch space")
            temporary = cleanup.enter_context(tempfile.TemporaryDirectory(prefix="restored-run-", dir=scratch))
            restored = Path(temporary) / source.name
            restored.mkdir()
            if not _require_bundle:
                for directory, _dirs, _files in os.walk(source, followlinks=False, onerror=_walk_error):
                    (restored / Path(directory).relative_to(source)).mkdir(parents=True, exist_ok=True)
            for path, relative, compressed, record, size in entries:
                target = restored / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                logical = path.with_suffix("") if compressed else path
                with desk_compress.open_bytes(logical) as stream:
                    _copy(stream, target, size, record)
        yield restored


@contextmanager
def _scratch_lock(root):
    # Lock the directory itself: no stale lock-file inode or cleanup race.
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        os.close(descriptor)


@contextmanager
def readable_run(run_dir, *, compression_records=None, _require_bundle=True):
    """Keep plain runs in place; verify and restore compressed runs for readers.

    The standard desk journal is ARCHIVE.desk/compression.jsonl. Callers
    with a different journal location can name it explicitly. Scratch uses
    the caller's TMPDIR and is removed before returning to archive work.
    """
    source = Path(run_dir)
    if not any(not path.with_suffix("").is_file() for path in source.rglob("*.zst")):
        yield source
        return
    if compression_records is None:
        compression_records = next(
            (journal for parent in source.resolve().parents
             if (journal := Path(str(parent) + ".desk") / "compression.jsonl").is_file()),
            None,
        )
    if compression_records is None:
        raise RestoreRefused("compressed run requires compression.jsonl; use restore_run_to_scratch.py "
                         "with --compression-records for a nonstandard journal location")
    with _restore_stack() as stack:
        try:
            scratch = stack.enter_context(tempfile.TemporaryDirectory(prefix="joulewise-reader-"))
            restored = stack.enter_context(restored_run(source, scratch,
                compression_records=compression_records,
                _require_bundle=_require_bundle))
        except (OSError, ValueError) as exc:
            raise RestoreRefused(exc) from exc
        yield restored


def readable_tree(source, *, compression_records=None):
    """Restore a complete custody subtree with the same journal, reserve and lock.

    Multi-bundle consumers must preserve root manifests and failed/partial
    directories as well as successful members; no root metadata is required.
    """
    return readable_run(source, compression_records=compression_records, _require_bundle=False)
