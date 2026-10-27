"""Desk-compressed session bytes, restored once per run (design §4.1, audit item 4).

The desk compressed each session after its harvest: every file of 1 MiB or
more under the runs roots, the custody and the archive's ``sources/`` became
a verified ``.zst`` sibling (``joulewise.desk_compress``).  L9 reads plain
paths at every step, so a session's files must be plain while any unit that
reads them runs.  Design §4.1 restored and re-compressed per unit; the lead's
correction of 2026-10-27 restores **each session once per run**: before the
first unit that reads it and re-compressed after the last (ALPHA r3 serves
GAMMA r2 and r3, and is restored once).

Per row whose latest event is ``compress`` (``desk_compress.status``), the
desk's own ``restore`` procedure with the transparent-compression step added:
decompress ``<x>.zst`` to ``<x>.partial``; check its SHA-256 against the row;
copy it as an APFS transparently compressed file (``ditto --hfsCompression``)
to ``<x>.tc.partial``, or plain where that is unavailable (Linux, CI); check
the copy's SHA-256; restore mode and modification time; fsync; rename to
``<x>``; remove the partial and the ``.zst``; append a ``restore`` row with
``apfs_compressed``.  Before each file, free space must exceed its plain size
plus the desk's 20 GiB reserve.

After the last unit the desk's ``compress`` runs with the arguments the desk
used, and an inventory taken before the restore must equal one taken after
the re-compression (paths, sizes, modification times, and SHA-256 of every
file below ``min_bytes``; a ``.zst`` may differ in size, but its record's
latest event must be ``compress`` with the first ``compress`` row's digest).

Failures are the tooling refusals ``b6_restore_failed`` and
``b6_recompress_differs``.  Nothing here deletes anything to make room.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import stat
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from joulewise import desk_compress

RESERVE_BYTES = 20 * 1024 ** 3      # desk_compress.restore's reserve_gib=20, unchanged
MIN_BYTES = 1048576                 # desk_compress.compress's default min_bytes, unchanged
DITTO = "/usr/bin/ditto"


class RestoreRefusal(RuntimeError):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(code)
        self.code, self.detail = code, detail


@dataclass(frozen=True)
class SessionBytes:
    session_id: str
    archive: Path
    custody: Path
    runs_roots: tuple[Path, ...]
    ledgers: tuple[Path, ...] = ()

    @property
    def record_dir(self) -> Path:
        return Path(str(self.archive) + ".desk")

    @classmethod
    def from_index_row(cls, row: dict, measurement: Path | None = None) -> "SessionBytes":
        ledger = Path(measurement) / "runs/calibration_observation_ledger.jsonl" if measurement else None
        return cls(row["session_id"], Path(row["archive_root"]), Path(row["custody_root"]),
                   tuple(Path(r) for r in row.get("runs_roots") or ()),
                   (ledger,) if ledger is not None and ledger.exists() else ())

    def roots(self) -> tuple[Path, ...]:
        return (*self.runs_roots, self.custody, self.archive)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(desk_compress.CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _transparent_copy(source: Path, target: Path) -> bool:
    """Copy as an APFS transparently compressed file where ``ditto`` exists."""
    if Path(DITTO).exists():
        subprocess.run([DITTO, "--hfsCompression", str(source), str(target)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    shutil.copyfile(source, target)
    return False


def inventory(session: SessionBytes, *, min_bytes: int = MIN_BYTES) -> dict[str, list]:
    """Every file under the session's roots except the record directory."""
    rows: dict[str, list] = {}
    record_dir = session.record_dir
    for root in session.roots():
        if not root.exists():
            continue
        for directory, dirs, names in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not (Path(directory) / d).is_symlink())
            for name in sorted(names):
                path = Path(directory) / name
                if path.is_symlink() or record_dir in path.parents:
                    continue
                info = path.stat()
                if path.name.endswith(".zst"):
                    rows[str(path)] = ["zst", info.st_mtime_ns, None]
                else:
                    rows[str(path)] = [info.st_size, info.st_mtime_ns,
                                       _sha(path) if info.st_size < min_bytes else None]
    return rows


def restore_session(session: SessionBytes, *, free=desk_compress._free, reserve: int = RESERVE_BYTES) -> dict:
    try:
        desk_compress._zstd_version()
    except (OSError, subprocess.CalledProcessError):
        raise RestoreRefusal("b6_restore_failed", "zstd_unavailable") from None
    rows = desk_compress.status(session.record_dir)
    summary = {"files": 0, "logical_bytes": 0, "disk_bytes": 0, "apfs_compressed": None}
    for row in rows:
        path = Path(row["path"])
        if free(path.parent) <= row["size"] + reserve:
            raise RestoreRefusal("b6_restore_failed", "restore_space")
        compressed, partial = Path(str(path) + ".zst"), Path(str(path) + ".partial")
        transparent = Path(str(path) + ".tc.partial")
        partial.unlink(missing_ok=True)
        transparent.unlink(missing_ok=True)
        try:
            subprocess.run([desk_compress.zstd_path(), "-d", "-q", str(compressed), "-o", str(partial)],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if _sha(partial) != row["sha256"]:
                raise ValueError("verify_mismatch")
            apfs = _transparent_copy(partial, transparent)
            if _sha(transparent) != row["sha256"]:
                raise ValueError("verify_mismatch")
            info = compressed.stat()
            os.chmod(transparent, row.get("mode", stat.S_IMODE(info.st_mode)))
            os.utime(transparent, ns=(info.st_atime_ns, row.get("mtime_ns", info.st_mtime_ns)))
            with transparent.open("rb") as stream:
                os.fsync(stream.fileno())
            os.replace(transparent, path)
            partial.unlink()
            compressed.unlink()
            desk_compress._append(session.record_dir, {**row, "event": "restore", "apfs_compressed": apfs,
                                                       "t": time.time()})
        except (OSError, subprocess.CalledProcessError, ValueError):
            partial.unlink(missing_ok=True)
            transparent.unlink(missing_ok=True)
            raise RestoreRefusal("b6_restore_failed", "verify_mismatch") from None
        summary["files"] += 1
        summary["logical_bytes"] += row["size"]
        summary["disk_bytes"] += path.stat().st_blocks * 512
        summary["apfs_compressed"] = apfs
    return summary


def recompress_session(session: SessionBytes) -> dict:
    code, summary = desk_compress.compress(archive=session.archive, custody=session.custody,
                                           runs_roots=list(session.runs_roots), ledgers=list(session.ledgers))
    if code != 0:
        raise RestoreRefusal("b6_restore_failed", f"compress_exit_{code}")
    return {"files": summary.get("files", 0)}


def after_check(session: SessionBytes, before: dict, after: dict) -> None:
    if set(before) != set(after):
        raise RestoreRefusal("b6_recompress_differs", "paths")
    compress_rows: dict[str, list] = {}
    manifest = session.record_dir / "compression.jsonl"
    if manifest.exists():
        import json
        for line in manifest.read_bytes().splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("event") in ("compress", "restore"):
                    compress_rows.setdefault(row["path"], []).append(row)
    for path, old in before.items():
        new = after[path]
        if old[0] == "zst":
            rows = compress_rows.get(path[:-len(".zst")], [])
            firsts = [r for r in rows if r["event"] == "compress"]
            if not rows or rows[-1]["event"] != "compress" or rows[-1]["sha256"] != firsts[0]["sha256"]:
                raise RestoreRefusal("b6_recompress_differs", "record")
            if new[1] != old[1]:
                raise RestoreRefusal("b6_recompress_differs", "mtime")
        elif new != old:
            raise RestoreRefusal("b6_recompress_differs", "file")


@dataclass
class Lifecycle:
    """Restore each session before its first user and re-compress after its last."""
    sessions: dict[str, SessionBytes]
    users: dict[str, int]
    restore=staticmethod(restore_session)
    recompress=staticmethod(recompress_session)
    cycles: dict = field(default_factory=dict)
    _before: dict = field(default_factory=dict)

    def acquire(self, session_ids) -> str | None:
        for session_id in session_ids:
            if session_id in self.cycles:
                if self.cycles[session_id].get("refusal"):
                    return self.cycles[session_id]["refusal"]
                continue
            session = self.sessions[session_id]
            started = time.monotonic()
            if not (session.record_dir / "compression.jsonl").exists():
                # Never desk-compressed (for example analysed before its desk
                # ran): its bytes are plain, and nothing is restored or
                # compressed, so the run leaves it exactly as it found it.
                self.cycles[session_id] = {"files": 0, "refusal": None, "after_check": "not_compressed",
                                           "restore_seconds": 0.0}
                continue
            try:
                self._before[session_id] = inventory(session)
                self.cycles[session_id] = {**self.restore(session), "refusal": None}
            except RestoreRefusal as exc:
                self.cycles[session_id] = {"refusal": exc.code, "detail": exc.detail}
            self.cycles[session_id]["restore_seconds"] = time.monotonic() - started
            if self.cycles[session_id]["refusal"]:
                return self.cycles[session_id]["refusal"]
        return None

    def release(self, session_ids) -> None:
        for session_id in session_ids:
            self.users[session_id] -= 1
            if self.users[session_id] == 0:
                self._close(session_id)

    def close_all(self) -> None:
        for session_id in sorted(self.cycles):
            if "after_check" not in self.cycles[session_id]:
                self._close(session_id)

    def _close(self, session_id: str) -> None:
        cycle = self.cycles.get(session_id)
        if cycle is None or "after_check" in cycle:
            return    # never restored, already closed, or never desk-compressed
        session = self.sessions[session_id]
        try:
            self.recompress(session)
            if session_id in self._before:
                after_check(session, self._before[session_id], inventory(session))
            cycle["after_check"] = "equal"
        except RestoreRefusal as exc:
            cycle["after_check"] = exc.code

    def refusals(self) -> list[list[str]]:
        rows = []
        for session_id, cycle in sorted(self.cycles.items()):
            if cycle.get("refusal"):
                rows.append([session_id, cycle["refusal"]])
            if cycle.get("after_check") not in (None, "equal", "not_compressed"):
                rows.append([session_id, cycle["after_check"]])
        return rows
