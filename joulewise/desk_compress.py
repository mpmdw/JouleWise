"""Session-desk compression, verified before removing any original bytes."""
from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import time

statvfs = os.statvfs  # Injectable for the restore-space check.
CHUNK_BYTES = 1024 * 1024
ZSTD_FALLBACK = "/opt/homebrew/bin/zstd"


def zstd_path() -> str:
    return shutil.which("zstd") or ZSTD_FALLBACK


def _zstd_version() -> str:
    return subprocess.run([zstd_path(), "--version"], check=True,
                          capture_output=True, text=True).stdout.strip()


def _hash_stream(stream) -> str:
    digest = hashlib.sha256()
    for chunk in iter(lambda: stream.read(CHUNK_BYTES), b""):
        digest.update(chunk)
    return digest.hexdigest()


def _hash_file(path: Path) -> str:
    with path.open("rb") as stream:
        return _hash_stream(stream)


def _decompressed_hash(path: Path) -> str:
    with subprocess.Popen([zstd_path(), "-d", "-q", "-c", str(path)],
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
        digest = _hash_stream(process.stdout)
        if process.wait() != 0:
            raise ValueError("decompression_failed")
        return digest


def read_bytes(path: Path) -> bytes:
    """Read a plain file, or its compressed sibling when the plain file is absent."""
    path = Path(path)
    if path.exists():
        return path.read_bytes()
    compressed = Path(str(path) + ".zst")
    if not compressed.exists():
        raise FileNotFoundError(errno.ENOENT, "file not found", str(compressed))
    try:
        return subprocess.run([zstd_path(), "-d", "-q", "-c", str(compressed)],
                              check=True, stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL).stdout
    except OSError as exc:
        raise OSError(exc.errno, "zstd_unavailable", str(compressed)) from None
    except subprocess.CalledProcessError:
        raise OSError(errno.EIO, "decompression_failed", str(compressed)) from None


def _free(path: Path) -> int:
    while not path.exists():
        path = path.parent
    value = statvfs(path)
    return value.f_bavail * value.f_frsize


def _append(record_dir: Path, row: dict) -> None:
    record_dir.mkdir(parents=True, exist_ok=True)
    with (record_dir / "compression.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def _summary(record_dir: Path, row: dict) -> None:
    record_dir.mkdir(parents=True, exist_ok=True)
    target = record_dir / "compression-summary.json"
    temporary = target.with_suffix(".json.partial")
    temporary.write_text(json.dumps(row, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, target)


def _under(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _protected(path: Path, protected_roots: list[Path]) -> bool:
    real = Path(os.path.realpath(path))
    parts = real.parts
    if any(_under(real, root) for root in protected_roots):
        return True
    if any(part in parts for part in ("instrument_validation", "derived", "withheld")):
        return True
    if real.name in ("calibration_observation_ledger.jsonl", "calibration_ledger_head.json", "harvest.json"):
        return True
    for index, part in enumerate(parts[:-1]):
        if part == "sources" and parts[index + 1] in ("ledger", "inputs", "repo", "SHA256SUMS"):
            return True
    return False


def _ledger_roots(ledgers: list[Path]) -> list[Path]:
    roots = []
    for ledger in ledgers:
        with ledger.open(encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError("ledger_unreadable")
                locator, runs = row.get("custody_locator"), row.get("runs_root")
                # Session-open/abort rows are valid ledger rows without a capture.
                if locator is None:
                    continue
                if not isinstance(locator, str) or not locator:
                    raise ValueError("ledger_unreadable")
                capture = Path(locator)
                if not capture.is_absolute():
                    if not isinstance(runs, str) or not runs:
                        raise ValueError("ledger_unreadable")
                    capture = Path(runs) / capture
                roots.append(Path(os.path.realpath(capture)))
    return roots


def _files(roots):
    seen = set()
    for kind, root in roots:
        for directory, dirs, names in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not (Path(directory) / d).is_symlink())
            for name in sorted(names):
                path = Path(directory) / name
                real = os.path.realpath(path)
                if real not in seen:
                    seen.add(real)
                    yield kind, path


def compress(*, archive: Path, custody: Path, runs_roots=(), ledgers=(),
             after=(), record_dir: Path | None = None, min_bytes: int = 1048576):
    archive, custody = Path(archive).absolute(), Path(custody).absolute()
    record_dir = Path(record_dir) if record_dir is not None else Path(str(archive) + ".desk")
    try:
        ready = ((custody / "night/chain.exited").is_file()
                 and json.loads((archive / "harvest.json").read_text()).get("verdict") != "HARVEST_FAULT"
                 and all(Path(path).exists() for path in after))
    except (OSError, ValueError, AttributeError):
        ready = False
    if not ready:
        return 4, {"reason": "NOT_READY"}
    try:
        version = _zstd_version()
    except (OSError, subprocess.CalledProcessError):
        return 4, {"reason": "zstd_unavailable"}
    copies = list(map(Path, ledgers))
    archive_ledger = archive / "sources/ledger/calibration_observation_ledger.jsonl"
    if archive_ledger.exists():
        copies.append(archive_ledger)
    try:
        protected = _ledger_roots(copies)
    except (OSError, ValueError, TypeError):
        row = {"event": "ledger_unreadable", "t": time.time()}
        _append(record_dir, row)
        _summary(record_dir, {"reason": "ledger_unreadable"})
        return 5, {"reason": "ledger_unreadable"}
    roots = [("runs", Path(path).absolute()) for path in runs_roots]
    roots += [("custody", custody), ("archive", archive / "sources")]
    started, free_before = time.monotonic(), _free(archive)
    summary = {"files": 0, "bytes_before": 0, "bytes_after": 0,
               "skipped_protected": 0, "mismatches": 0}
    # Decide restore leftovers before creating any new compressed siblings.
    for _, path in _files(roots):
        if path.is_symlink() or not path.is_file() or _protected(path, protected):
            continue
        if (path.name.endswith(".zst.partial")
                or (path.name.endswith(".partial")
                    and Path(str(path)[:-len(".partial")] + ".zst").exists())):
            path.unlink()
    for kind, path in _files(roots):
        if path.is_symlink() or not path.is_file():
            continue
        if _protected(path, protected):
            summary["skipped_protected"] += 1
            continue
        if path.name.endswith(".zst") or path.stat().st_size < min_bytes:
            continue
        info, digest = path.stat(), _hash_file(path)
        partial, compressed = Path(str(path) + ".zst.partial"), Path(str(path) + ".zst")
        partial.unlink(missing_ok=True)
        try:
            subprocess.run([zstd_path(), "-3", "-q", "-T0", str(path), "-o", str(partial)],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if _decompressed_hash(partial) != digest:
                raise ValueError("verify_mismatch")
            with partial.open("rb") as stream:
                os.fsync(stream.fileno())
            os.replace(partial, compressed)
            os.chmod(compressed, stat.S_IMODE(info.st_mode))
            os.utime(compressed, ns=(info.st_atime_ns, info.st_mtime_ns))
            row = {"event": "compress", "path": str(path), "root": kind, "sha256": digest,
                   "size": info.st_size, "zst_size": compressed.stat().st_size,
                   "zstd_version": version, "t": time.time(),
                   "mode": stat.S_IMODE(info.st_mode), "mtime_ns": info.st_mtime_ns}
            _append(record_dir, row)
            path.unlink()
        except (subprocess.CalledProcessError, ValueError):
            partial.unlink(missing_ok=True)
            summary["mismatches"] += 1
            _append(record_dir, {"event": "verify_mismatch", "path": str(path), "root": kind, "t": time.time()})
            continue
        summary["files"] += 1
        summary["bytes_before"] += row["size"]
        summary["bytes_after"] += row["zst_size"]
    summary.update(free_bytes_before=free_before, free_bytes_after=_free(archive),
                   seconds=time.monotonic() - started)
    summary["freed_statvfs"] = summary["free_bytes_after"] - free_before
    _summary(record_dir, summary)
    return (2 if summary["mismatches"] else 0), summary


def status(record_dir: Path, root="all") -> list[dict]:
    latest = {}
    manifest = Path(record_dir) / "compression.jsonl"
    if manifest.exists():
        for line in manifest.read_text().splitlines():
            row = json.loads(line)
            if row.get("event") in ("compress", "restore"):
                latest[row["path"]] = row
    return [row for row in latest.values() if row["event"] == "compress"
            and root in ("all", row["root"])]


def restore(*, record_dir: Path, root="all", reserve_gib=20):
    record_dir = Path(record_dir)
    try:
        _zstd_version()
    except (OSError, subprocess.CalledProcessError):
        return 4, {"reason": "zstd_unavailable"}
    rows = status(record_dir, root)
    # Check every filesystem before writing even a partial restore.
    required, locations = {}, {}
    for row in rows:
        path = Path(row["path"]).parent
        device = path.stat().st_dev
        required[device] = required.get(device, 0) + row["size"]
        locations[device] = path
    shortfall = max((int(size + reserve_gib * 1024**3) - _free(locations[device])
                     for device, size in required.items()), default=0)
    if shortfall > 0:
        return 3, {"reason": "restore_space", "shortfall_bytes": shortfall}
    summary = {"files": 0, "mismatches": 0}
    for row in rows:
        path = Path(row["path"])
        compressed, partial = Path(str(path) + ".zst"), Path(str(path) + ".partial")
        partial.unlink(missing_ok=True)
        try:
            subprocess.run([zstd_path(), "-d", "-q", str(compressed), "-o", str(partial)],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if _hash_file(partial) != row["sha256"]:
                raise ValueError("verify_mismatch")
            info = compressed.stat()
            os.chmod(partial, row.get("mode", stat.S_IMODE(info.st_mode)))
            os.utime(partial, ns=(info.st_atime_ns, row.get("mtime_ns", info.st_mtime_ns)))
            with partial.open("rb") as stream:
                os.fsync(stream.fileno())
            os.replace(partial, path)
            _append(record_dir, {**row, "event": "restore", "t": time.time()})
            compressed.unlink()
            summary["files"] += 1
        except (subprocess.CalledProcessError, ValueError):
            partial.unlink(missing_ok=True)
            summary["mismatches"] += 1
            _append(record_dir, {"event": "verify_mismatch", "path": str(path), "root": row["root"], "t": time.time()})
    return (2 if summary["mismatches"] else 0), summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    comp = commands.add_parser("compress")
    comp.add_argument("--archive", required=True, type=Path)
    comp.add_argument("--custody", required=True, type=Path)
    comp.add_argument("--runs-root", action="append", default=[], type=Path)
    comp.add_argument("--ledger", action="append", default=[], type=Path)
    comp.add_argument("--after", action="append", default=[], type=Path)
    comp.add_argument("--record-dir", type=Path)
    comp.add_argument("--min-bytes", type=int, default=1048576)
    for name in ("restore", "status"):
        command = commands.add_parser(name)
        command.add_argument("--record-dir", required=True, type=Path)
        command.add_argument("--root", choices=("runs", "custody", "archive", "all"), default="all")
        if name == "restore":
            command.add_argument("--reserve-gib", type=float, default=20)
    args = parser.parse_args(argv)
    if args.command == "compress":
        if args.min_bytes < 0:
            parser.error("min-bytes must be nonnegative")
        rc, result = compress(archive=args.archive, custody=args.custody, runs_roots=args.runs_root,
                              ledgers=args.ledger, after=args.after, record_dir=args.record_dir,
                              min_bytes=args.min_bytes)
    elif args.command == "restore":
        if args.reserve_gib < 0:
            parser.error("reserve-gib must be nonnegative")
        rc, result = restore(record_dir=args.record_dir, root=args.root, reserve_gib=args.reserve_gib)
    else:
        rc, result = 0, {"files": len(status(args.record_dir, args.root))}
    if "reason" in result:
        print(f"{args.command} reason={result['reason']} shortfall_bytes={result.get('shortfall_bytes', 0)}")
    else:
        print(f"{args.command} files={result['files']} before={result.get('bytes_before', 0)} "
              f"after={result.get('bytes_after', 0)} freed_statvfs={result.get('freed_statvfs', 0)} "
              f"mismatches={result.get('mismatches', 0)}")
    return rc
