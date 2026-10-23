"""Run a reader against one restored bundle, removing the scratch copy afterward.

Example: python scripts/restore_run_to_scratch.py --run-dir ARCHIVE/sources/claim-runs/RUN \
    --scratch-dir SCRATCH --compression-records ARCHIVE.desk/compression.jsonl \
    -- python reader.py {run}

The archive and compression journal are read-only. Compressed files require a
matching journal entry; decompressed sizes and SHA-256 digests must match before
the reader starts. No run or outcome values are printed by this tool.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise import desk_compress

# macOS began evicting ledger-referenced capture files to iCloud near 29 GiB
# free in the 2026-10-12 fault (RUN_STATE.md item 34). Stay above that onset;
# 40 GiB restores the earlier margin (11 GiB above the observed onset).
# restored_run adds the entire uncompressed run size before copying a byte.
MIN_RESERVE_GIB = 40


def _records(path):
    if path is None:
        return {}
    path = Path(path)
    if path.name != "compression.jsonl" or not path.is_file():
        raise ValueError("compression-records must name an existing compression.jsonl")
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
def restored_run(run_dir, scratch_dir, *, compression_records=None, reserve_gib=MIN_RESERVE_GIB):
    """Yield one private, plain bundle; clean it up on success or failure."""
    if not math.isfinite(reserve_gib) or reserve_gib < MIN_RESERVE_GIB:
        raise ValueError(f"reserve-gib must be finite and at least {MIN_RESERVE_GIB}")
    source = Path(run_dir)
    if source.is_symlink():
        raise ValueError("symlinks are not supported")
    source = source.resolve(strict=True)
    if not source.is_dir() or not any((source / name).is_file()
                                     for name in ("metadata.json", "metadata.json.zst")):
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
    required = sum(entry[4] for entry in entries)
    if shutil.disk_usage(scratch).free < required + reserve_gib * 1024**3:
        raise ValueError("insufficient scratch space")
    with tempfile.TemporaryDirectory(prefix="restored-run-", dir=scratch) as temporary:
        restored = Path(temporary) / source.name
        restored.mkdir()
        for path, relative, compressed, record, size in entries:
            target = restored / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            logical = path.with_suffix("") if compressed else path
            with desk_compress.open_bytes(logical) as stream:
                _copy(stream, target, size, record)
        yield restored


@contextmanager
def readable_run(run_dir, *, compression_records=None):
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
        raise ValueError("compressed run requires compression.jsonl; use restore_run_to_scratch.py "
                         "with --compression-records for a nonstandard journal location")
    with tempfile.TemporaryDirectory(prefix="joulewise-reader-") as scratch:
        with restored_run(source, scratch, compression_records=compression_records) as restored:
            yield restored


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--scratch-dir", required=True, type=Path)
    parser.add_argument("--compression-records", type=Path)
    parser.add_argument("--reserve-gib", type=float, default=MIN_RESERVE_GIB,
                        help=f"free space remaining after restore (at least {MIN_RESERVE_GIB} GiB)")
    parser.add_argument("command", nargs=argparse.REMAINDER,
                        help="reader command; each {run} is replaced by the restored bundle path")
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command or not any("{run}" in arg for arg in command):
        parser.error("a reader command containing {run} is required")
    try:
        with restored_run(args.run_dir, args.scratch_dir,
                          compression_records=args.compression_records,
                          reserve_gib=args.reserve_gib) as restored:
            return subprocess.run([arg.replace("{run}", str(restored)) for arg in command],
                                  check=False).returncode
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"restore-to-scratch: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
