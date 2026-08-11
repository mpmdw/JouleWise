#!/usr/bin/env python3
"""Safely hydrate the digest-pinned D-117 custody-store transport archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
from typing import BinaryIO


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts.package_d117_fixture import (
    FIXTURE_ID,
    LOGICAL_FILE_COUNT,
    TRANSPORT_SCHEMA,
    FixtureTransportError,
    file_sha256,
    find_zstd,
    load_census,
    strict_json_bytes,
)


DESCRIPTOR_FIELDS = {
    "schema_version",
    "fixture_id",
    "release_tag",
    "asset_name",
    "archive_format",
    "archive_sha256",
    "logical_file_count",
    "logical_bytes",
    "custody_manifest_sha256",
}
HEX_SHA256 = frozenset("0123456789abcdef")


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in HEX_SHA256 for character in value)
    )


def load_descriptor(path: Path) -> dict[str, object]:
    value = strict_json_bytes(path.read_bytes(), label="transport descriptor")
    if not isinstance(value, dict) or set(value) != DESCRIPTOR_FIELDS:
        raise FixtureTransportError("transport descriptor fields mismatch")
    if value["schema_version"] != TRANSPORT_SCHEMA:
        raise FixtureTransportError("transport descriptor schema mismatch")
    if value["fixture_id"] != FIXTURE_ID:
        raise FixtureTransportError("transport descriptor fixture_id mismatch")
    if value["archive_format"] != "tar.zst":
        raise FixtureTransportError("transport descriptor archive format mismatch")
    for field in ("release_tag", "asset_name"):
        if not isinstance(value[field], str) or not value[field]:
            raise FixtureTransportError(f"transport descriptor {field} is invalid")
    if not _is_sha256(value["archive_sha256"]):
        raise FixtureTransportError("transport descriptor archive SHA is invalid")
    if not _is_sha256(value["custody_manifest_sha256"]):
        raise FixtureTransportError("transport descriptor census SHA is invalid")
    if value["logical_file_count"] != LOGICAL_FILE_COUNT:
        raise FixtureTransportError("transport descriptor logical file count mismatch")
    if (
        not isinstance(value["logical_bytes"], int)
        or isinstance(value["logical_bytes"], bool)
        or value["logical_bytes"] <= 0
    ):
        raise FixtureTransportError("transport descriptor logical bytes is invalid")
    return value


def _safe_member_name(name: str) -> str:
    if not name or name.startswith("/") or "\\" in name:
        raise FixtureTransportError(f"absolute or malformed archive path refused: {name!r}")
    path = PurePosixPath(name)
    if any(part in {"", ".", ".."} for part in name.split("/")):
        raise FixtureTransportError(f"noncanonical archive path refused: {name!r}")
    if path.is_absolute() or path.as_posix() != name:
        raise FixtureTransportError(f"absolute or noncanonical archive path refused: {name!r}")
    return name


def _start_decompressor(archive: Path, zstd: str) -> subprocess.Popen[bytes]:
    process = subprocess.Popen(
        [zstd, "-q", "-d", "-c", str(archive)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.stdout is None or process.stderr is None:
        process.kill()
        raise FixtureTransportError("could not start zstd decompressor")
    return process


def _finish_decompressor(process: subprocess.Popen[bytes]) -> None:
    assert process.stdout is not None
    assert process.stderr is not None
    process.stdout.close()
    stderr = process.stderr.read().decode("utf-8", errors="replace")
    process.stderr.close()
    returncode = process.wait()
    if returncode != 0:
        raise FixtureTransportError(
            f"zstd decompression failed with status {returncode}: {stderr.strip()}"
        )


def _abort_decompressor(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is None:
        process.kill()
    process.wait()
    if process.stdout is not None and not process.stdout.closed:
        process.stdout.close()
    if process.stderr is not None and not process.stderr.closed:
        process.stderr.close()


def _validate_archive(
    archive_path: Path,
    expected_files: dict[str, str],
    census_raw: bytes,
    *,
    zstd: str,
) -> None:
    seen: set[str] = set()
    manifest_seen = False
    process = _start_decompressor(archive_path, zstd)
    assert process.stdout is not None
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
            for member in archive:
                name = _safe_member_name(member.name)
                if name in seen:
                    raise FixtureTransportError(
                        f"duplicate archive path refused: {name}"
                    )
                seen.add(name)
                if name not in expected_files:
                    raise FixtureTransportError(
                        f"unexpected archive path refused: {name}"
                    )
                if not member.isreg() or member.linkname:
                    raise FixtureTransportError(
                        f"non-regular archive member refused: {name}"
                    )
                if name == "manifest.json":
                    handle = archive.extractfile(member)
                    if handle is None:
                        raise FixtureTransportError("archive census is unreadable")
                    if handle.read() != census_raw:
                        raise FixtureTransportError(
                            "archive census bytes differ from committed census"
                        )
                    manifest_seen = True
        _finish_decompressor(process)
    except BaseException:
        _abort_decompressor(process)
        raise
    missing = sorted(set(expected_files) - seen)
    if missing:
        raise FixtureTransportError(f"archive member is missing: {missing[0]}")
    if len(seen) != LOGICAL_FILE_COUNT:
        raise FixtureTransportError("archive member count mismatch")
    if not manifest_seen:
        raise FixtureTransportError("archive census member is missing")


class _DigestingWriter:
    def __init__(self, handle: BinaryIO) -> None:
        self.handle = handle
        self.digest = hashlib.sha256()
        self.count = 0

    def write(self, chunk: bytes) -> int:
        count = self.handle.write(chunk)
        self.digest.update(chunk[:count])
        self.count += count
        return count


def _copy_member(source: BinaryIO, destination: _DigestingWriter) -> None:
    while chunk := source.read(1024 * 1024):
        if destination.write(chunk) != len(chunk):
            raise FixtureTransportError("short write while hydrating archive")


def _extract_archive(
    archive_path: Path,
    staging: Path,
    expected_files: dict[str, str],
    *,
    zstd: str,
) -> int:
    seen: set[str] = set()
    logical_bytes = 0
    process = _start_decompressor(archive_path, zstd)
    assert process.stdout is not None
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
            for member in archive:
                name = _safe_member_name(member.name)
                if name in seen:
                    raise FixtureTransportError(
                        f"duplicate archive path refused during extraction: {name}"
                    )
                seen.add(name)
                if name not in expected_files or not member.isreg() or member.linkname:
                    raise FixtureTransportError(
                        f"archive changed after validation: {name}"
                    )
                source = archive.extractfile(member)
                if source is None:
                    raise FixtureTransportError(f"archive member is unreadable: {name}")
                destination = staging.joinpath(*PurePosixPath(name).parts)
                destination.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
                with destination.open("xb") as output_handle:
                    writer = _DigestingWriter(output_handle)
                    _copy_member(source, writer)
                os.chmod(destination, 0o644)
                if writer.count != member.size:
                    raise FixtureTransportError(
                        f"archive member size changed during extraction: {name}"
                    )
                if writer.digest.hexdigest() != expected_files[name]:
                    raise FixtureTransportError(
                        f"archive member digest differs from census: {name}"
                    )
                logical_bytes += writer.count
        _finish_decompressor(process)
    except BaseException:
        _abort_decompressor(process)
        raise
    if seen != set(expected_files):
        raise FixtureTransportError("archive membership changed during extraction")
    return logical_bytes


def _regular_identity(path: Path) -> tuple[int, int, int, int]:
    value = path.lstat()
    if not stat.S_ISREG(value.st_mode) or stat.S_ISLNK(value.st_mode):
        raise FixtureTransportError("archive must be a regular file")
    return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns


def _outside_repository(destination: Path) -> Path:
    resolved = destination.resolve(strict=False)
    repository = REPOSITORY_ROOT.resolve()
    if resolved == repository or repository in resolved.parents:
        raise FixtureTransportError("hydration destination must be outside the repository")
    return resolved


def hydrate_fixture(
    archive_path: Path,
    destination: Path,
    census_path: Path,
    expected_archive_sha256: str,
    *,
    expected_logical_bytes: int | None = None,
    zstd: str | None = None,
) -> dict[str, object]:
    """Validate and atomically hydrate an archive to a caller-owned path."""

    if not _is_sha256(expected_archive_sha256):
        raise FixtureTransportError("expected archive SHA is invalid")
    archive_path = archive_path.resolve()
    archive_identity = _regular_identity(archive_path)
    actual_archive_sha256 = file_sha256(archive_path)
    if actual_archive_sha256 != expected_archive_sha256:
        raise FixtureTransportError(
            "archive SHA mismatch: "
            f"expected {expected_archive_sha256}, observed {actual_archive_sha256}"
        )
    census_raw, _census, expected_files = load_census(census_path)
    destination = _outside_repository(destination)
    if destination.exists() or destination.is_symlink():
        raise FixtureTransportError(f"hydration destination already exists: {destination}")
    zstd_path = find_zstd(zstd)
    _validate_archive(
        archive_path, expected_files, census_raw, zstd=zstd_path
    )
    if _regular_identity(archive_path) != archive_identity:
        raise FixtureTransportError("archive changed after SHA verification")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(
            prefix=f".{destination.name}.hydrate-", dir=destination.parent
        )
    )
    try:
        logical_bytes = _extract_archive(
            archive_path, staging, expected_files, zstd=zstd_path
        )
        if _regular_identity(archive_path) != archive_identity:
            raise FixtureTransportError("archive changed during extraction")
        if expected_logical_bytes is not None and logical_bytes != expected_logical_bytes:
            raise FixtureTransportError(
                "hydrated logical byte count differs from descriptor"
            )
        if (staging / "manifest.json").read_bytes() != census_raw:
            raise FixtureTransportError(
                "hydrated census bytes differ from committed census"
            )
        os.chmod(staging, 0o755)
        if destination.exists() or destination.is_symlink():
            raise FixtureTransportError(
                f"hydration destination appeared during extraction: {destination}"
            )
        os.replace(staging, destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return {
        "archive_sha256": actual_archive_sha256,
        "logical_file_count": len(expected_files),
        "logical_bytes": logical_bytes,
        "destination": str(destination),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument(
        "--census",
        type=Path,
        default=(
            REPOSITORY_ROOT
            / "tests"
            / "fixtures"
            / "d117_v2_production"
            / "custody_store"
            / "manifest.json"
        ),
    )
    digest = parser.add_mutually_exclusive_group(required=True)
    digest.add_argument("--archive-sha256")
    digest.add_argument("--descriptor", type=Path)
    parser.add_argument("--zstd")
    args = parser.parse_args(argv)
    try:
        expected_logical_bytes = None
        if args.descriptor:
            descriptor = load_descriptor(args.descriptor)
            expected_archive_sha256 = str(descriptor["archive_sha256"])
            expected_logical_bytes = int(descriptor["logical_bytes"])
            census_sha256 = file_sha256(args.census)
            if census_sha256 != descriptor["custody_manifest_sha256"]:
                raise FixtureTransportError(
                    "committed census SHA differs from transport descriptor"
                )
            if args.archive.name != descriptor["asset_name"]:
                raise FixtureTransportError(
                    "archive filename differs from transport descriptor"
                )
        else:
            expected_archive_sha256 = args.archive_sha256
        report = hydrate_fixture(
            args.archive,
            args.destination,
            args.census,
            expected_archive_sha256,
            expected_logical_bytes=expected_logical_bytes,
            zstd=args.zstd,
        )
    except (FixtureTransportError, OSError, tarfile.TarError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
