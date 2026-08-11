#!/usr/bin/env python3
"""Build the governed D-117 custody-store transport archive.

Archive paths are sorted POSIX paths.  Every archive record is a regular file
with mtime/uid/gid fixed to zero, empty uname/gname, and mode 0644.  Logical
directories are implicit (and are checked in the source tree), so the archive
contains exactly 191 members: 190 ledger-censused artifacts plus manifest.json.
The archive therefore has no directory metadata; extracted directories use the
hydrator's fixed 0755 policy.  GNU tar headers and single-threaded zstd level 10
make the byte stream reproducible for a fixed zstd implementation.

The source walk refuses symlinks, sockets, devices, FIFOs, unexpected paths,
and hard-link aliasing between governed paths.  A governed regular file may
have links outside the source tree: it is still emitted by value as an
independent regular archive member, never as a tar hard-link record.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import tarfile
import tempfile
from typing import BinaryIO


FIXTURE_ID = "d117_v2_production"
CENSUS_SCHEMA = "joulewise.calibration_custody_store_manifest.v1"
TRANSPORT_SCHEMA = "joulewise.d117_fixture_transport.v1"
CONTENT_COUNT = 38
ARTIFACT_PATHS = (
    "events.jsonl",
    "instrument_evidence.json",
    "manifest.json",
    "power_trace.csv",
    "raw/powermetrics.plist",
)
LOGICAL_FILE_COUNT = CONTENT_COUNT * len(ARTIFACT_PATHS) + 1
HEX_SHA256 = frozenset("0123456789abcdef")


class FixtureTransportError(ValueError):
    """A governed fixture transport contract was violated."""


def _reject_constant(value: str) -> object:
    raise FixtureTransportError(f"non-finite JSON constant refused: {value}")


def _object_no_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise FixtureTransportError(f"duplicate JSON key refused: {key}")
        result[key] = value
    return result


def strict_json_bytes(raw: bytes, *, label: str) -> object:
    try:
        return json.loads(
            raw,
            object_pairs_hook=_object_no_duplicates,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FixtureTransportError(f"{label} is not strict UTF-8 JSON: {exc}") from exc


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in HEX_SHA256 for character in value)
    )


def load_census_bytes(raw: bytes) -> tuple[dict[str, object], dict[str, str]]:
    """Validate the committed census and return archive-path digest pins."""

    value = strict_json_bytes(raw, label="custody census")
    if not isinstance(value, dict):
        raise FixtureTransportError("custody census must be an object")
    if set(value) != {"schema_version", "ledger", "contents"}:
        raise FixtureTransportError("custody census has unexpected fields")
    if value["schema_version"] != CENSUS_SCHEMA:
        raise FixtureTransportError("custody census schema mismatch")
    ledger = value["ledger"]
    if not isinstance(ledger, dict) or set(ledger) != {
        "schema_version",
        "head_sequence",
        "head_digest",
    }:
        raise FixtureTransportError("custody census ledger projection is malformed")
    if (
        not isinstance(ledger["schema_version"], str)
        or not isinstance(ledger["head_sequence"], int)
        or isinstance(ledger["head_sequence"], bool)
        or ledger["head_sequence"] < 0
        or not _is_sha256(ledger["head_digest"])
    ):
        raise FixtureTransportError("custody census ledger projection is invalid")
    contents = value["contents"]
    if not isinstance(contents, list) or len(contents) != CONTENT_COUNT:
        raise FixtureTransportError(
            f"custody census must contain exactly {CONTENT_COUNT} content IDs"
        )
    expected: dict[str, str] = {}
    content_ids: list[str] = []
    for entry in contents:
        if not isinstance(entry, dict) or set(entry) != {
            "content_id",
            "artifact_sha256",
        }:
            raise FixtureTransportError("custody census content entry is malformed")
        content_id = entry["content_id"]
        hashes = entry["artifact_sha256"]
        if not _is_sha256(content_id):
            raise FixtureTransportError("custody census content_id is invalid")
        if not isinstance(hashes, dict) or set(hashes) != set(ARTIFACT_PATHS):
            raise FixtureTransportError(
                f"custody census {content_id} does not name the exact artifact vector"
            )
        content_ids.append(content_id)
        for artifact_path in ARTIFACT_PATHS:
            digest = hashes[artifact_path]
            if not _is_sha256(digest):
                raise FixtureTransportError(
                    f"custody census digest is invalid: {content_id}/{artifact_path}"
                )
            expected[f"{content_id}/{artifact_path}"] = digest
    if content_ids != sorted(content_ids) or len(set(content_ids)) != len(content_ids):
        raise FixtureTransportError("custody census content IDs are not unique and sorted")
    expected["manifest.json"] = hashlib.sha256(raw).hexdigest()
    if len(expected) != LOGICAL_FILE_COUNT:
        raise FixtureTransportError("custody census logical file count mismatch")
    return value, expected


def load_census(path: Path) -> tuple[bytes, dict[str, object], dict[str, str]]:
    raw = path.read_bytes()
    value, expected = load_census_bytes(raw)
    return raw, value, expected


def _expected_directories(expected_files: dict[str, str]) -> set[str]:
    result: set[str] = set()
    for name in expected_files:
        parent = PurePosixPath(name).parent
        while parent != PurePosixPath("."):
            result.add(parent.as_posix())
            parent = parent.parent
    return result


def _scan_source_tree(
    store: Path, expected_files: dict[str, str]
) -> dict[str, tuple[int, int, int, int]]:
    try:
        root_stat = store.lstat()
    except FileNotFoundError as exc:
        raise FixtureTransportError(f"custody store is absent: {store}") from exc
    if not stat.S_ISDIR(root_stat.st_mode) or stat.S_ISLNK(root_stat.st_mode):
        raise FixtureTransportError("custody store root must be a real directory")
    expected_dirs = _expected_directories(expected_files)
    found_files: set[str] = set()
    found_dirs: set[str] = set()
    file_stats: dict[str, tuple[int, int, int, int]] = {}
    inodes: dict[tuple[int, int], str] = {}

    def walk(directory: Path) -> None:
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                relative = path.relative_to(store).as_posix()
                entry_stat = entry.stat(follow_symlinks=False)
                mode = entry_stat.st_mode
                if stat.S_ISLNK(mode):
                    raise FixtureTransportError(f"source symlink refused: {relative}")
                if stat.S_ISDIR(mode):
                    if relative not in expected_dirs:
                        raise FixtureTransportError(
                            f"unexpected source directory refused: {relative}"
                        )
                    found_dirs.add(relative)
                    walk(path)
                    continue
                if not stat.S_ISREG(mode):
                    raise FixtureTransportError(
                        f"non-regular source entry refused: {relative}"
                    )
                if relative not in expected_files:
                    raise FixtureTransportError(
                        f"unexpected source file refused: {relative}"
                    )
                inode = (entry_stat.st_dev, entry_stat.st_ino)
                if inode in inodes:
                    raise FixtureTransportError(
                        "source hard-link alias refused: "
                        f"{relative} aliases {inodes[inode]}"
                    )
                inodes[inode] = relative
                found_files.add(relative)
                file_stats[relative] = (
                    entry_stat.st_dev,
                    entry_stat.st_ino,
                    entry_stat.st_size,
                    entry_stat.st_mtime_ns,
                )

    walk(store)
    missing_files = sorted(set(expected_files) - found_files)
    missing_dirs = sorted(expected_dirs - found_dirs)
    if missing_files:
        raise FixtureTransportError(
            f"source is missing governed file: {missing_files[0]}"
        )
    if missing_dirs:
        raise FixtureTransportError(
            f"source is missing governed directory: {missing_dirs[0]}"
        )
    return file_stats


class _HashingReader:
    def __init__(self, handle: BinaryIO) -> None:
        self.handle = handle
        self.digest = hashlib.sha256()
        self.count = 0

    def read(self, size: int = -1) -> bytes:
        chunk = self.handle.read(size)
        self.digest.update(chunk)
        self.count += len(chunk)
        return chunk


def find_zstd(explicit: str | None = None) -> str:
    candidate = explicit or os.environ.get("ZSTD") or shutil.which("zstd")
    if not candidate:
        homebrew = Path("/opt/homebrew/bin/zstd")
        if homebrew.is_file():
            candidate = str(homebrew)
    if not candidate:
        raise FixtureTransportError("zstd executable is unavailable")
    return candidate


def _write_tar_zst(
    store: Path,
    archive_tmp: Path,
    census_raw: bytes,
    expected_files: dict[str, str],
    initial_stats: dict[str, tuple[int, int, int, int]],
    *,
    zstd: str,
) -> int:
    logical_bytes = 0
    with archive_tmp.open("wb") as archive_handle:
        process = subprocess.Popen(
            [zstd, "-q", "-10", "-T1", "-c"],
            stdin=subprocess.PIPE,
            stdout=archive_handle,
            stderr=subprocess.PIPE,
        )
        if process.stdin is None or process.stderr is None:
            process.kill()
            raise FixtureTransportError("could not start zstd compressor")
        try:
            with tarfile.open(
                fileobj=process.stdin, mode="w|", format=tarfile.GNU_FORMAT
            ) as archive:
                for relative in sorted(expected_files):
                    if relative == "manifest.json":
                        source_handle: BinaryIO = io.BytesIO(census_raw)
                        size = len(census_raw)
                        before = None
                    else:
                        path = store / relative
                        flags = os.O_RDONLY
                        if hasattr(os, "O_NOFOLLOW"):
                            flags |= os.O_NOFOLLOW
                        descriptor = os.open(path, flags)
                        source_handle = os.fdopen(descriptor, "rb")
                        opened = os.fstat(source_handle.fileno())
                        before = (
                            opened.st_dev,
                            opened.st_ino,
                            opened.st_size,
                            opened.st_mtime_ns,
                        )
                        if not stat.S_ISREG(opened.st_mode) or before != initial_stats[relative]:
                            source_handle.close()
                            raise FixtureTransportError(
                                f"source changed before packaging: {relative}"
                            )
                        size = opened.st_size
                    info = tarfile.TarInfo(relative)
                    info.size = size
                    info.mtime = 0
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    info.mode = 0o644
                    info.type = tarfile.REGTYPE
                    reader = _HashingReader(source_handle)
                    try:
                        archive.addfile(info, reader)
                        if before is not None:
                            after_stat = os.fstat(source_handle.fileno())
                            after = (
                                after_stat.st_dev,
                                after_stat.st_ino,
                                after_stat.st_size,
                                after_stat.st_mtime_ns,
                            )
                            if after != before:
                                raise FixtureTransportError(
                                    f"source changed while packaging: {relative}"
                                )
                    finally:
                        source_handle.close()
                    if reader.count != size:
                        raise FixtureTransportError(
                            f"short read while packaging: {relative}"
                        )
                    if reader.digest.hexdigest() != expected_files[relative]:
                        raise FixtureTransportError(
                            f"source digest differs from census: {relative}"
                        )
                    logical_bytes += size
            process.stdin.close()
            stderr = process.stderr.read().decode("utf-8", errors="replace")
            process.stderr.close()
            returncode = process.wait()
        except BaseException:
            if process.poll() is None:
                process.kill()
            process.wait()
            if process.stdin and not process.stdin.closed:
                process.stdin.close()
            if process.stderr and not process.stderr.closed:
                process.stderr.close()
            raise
    if returncode != 0:
        raise FixtureTransportError(
            f"zstd compression failed with status {returncode}: {stderr.strip()}"
        )
    return logical_bytes


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def package_fixture(
    store: Path,
    archive_path: Path,
    report_path: Path,
    *,
    zstd: str | None = None,
) -> dict[str, object]:
    """Package a complete governed store and return the transport report."""

    # Make the path absolute without following its final component; the root
    # itself must still be rejected when it is a symlink.
    store = Path(os.path.abspath(os.fspath(store)))
    census_path = store / "manifest.json"
    census_raw, _census, expected_files = load_census(census_path)
    initial_stats = _scan_source_tree(store, expected_files)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{archive_path.name}.", dir=archive_path.parent
    )
    os.close(descriptor)
    archive_tmp = Path(temporary_name)
    try:
        logical_bytes = _write_tar_zst(
            store,
            archive_tmp,
            census_raw,
            expected_files,
            initial_stats,
            zstd=find_zstd(zstd),
        )
        if _scan_source_tree(store, expected_files) != initial_stats:
            raise FixtureTransportError("custody store changed during packaging")
        os.replace(archive_tmp, archive_path)
    finally:
        archive_tmp.unlink(missing_ok=True)
    report = {
        "archive_sha256": file_sha256(archive_path),
        "logical_file_count": len(expected_files),
        "logical_bytes": logical_bytes,
    }
    _atomic_json(report_path, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--zstd")
    args = parser.parse_args(argv)
    try:
        report = package_fixture(
            args.store, args.archive, args.report, zstd=args.zstd
        )
    except (FixtureTransportError, OSError, tarfile.TarError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
