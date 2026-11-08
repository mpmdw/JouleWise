"""Verified raw offload of one finalized window for an off-MBP harvest (HARVEST-OFF-opus).

The MBP packs the finalized session root once (``pack``): every regular file is
read once, hashed (SHA-256) and streamed into a zstd-compressed tar; symlinks are
kept literally; any other file type refuses. The manifest records the absolute
source root, every path with its digest, size and mode, and the payload digest.

The Air restores it (``unpack``) only at the SAME absolute path, into a fresh
sibling staging directory that is renamed into place after every byte, link and
path matches the manifest exactly (no extra, missing or changed entry). The
harvest embeds absolute paths (plan, custody, archive, bundle locators), so a
same-path restore is what makes its output byte-identical to an MBP run; a
relocated restore is refused rather than silently producing different bytes.

Nothing here reads outcome-bearing content: it moves bytes and compares digests.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import tarfile
from typing import Any, BinaryIO

SCHEMA = 'joulewise.align_v4.harvest_offload.v1'
PAYLOAD = 'payload.tar.zst'
MANIFEST = 'MANIFEST.json'
CHUNK = 8 * 1024 * 1024
DEFAULT_LEVEL = 3


class OffloadRefused(ValueError):
    """The offload cannot be packed or restored without a byte mismatch."""


def zstd_path() -> str:
    return shutil.which('zstd') or '/opt/homebrew/bin/zstd'


class _HashingReader:
    def __init__(self, stream: BinaryIO):
        self.stream, self.digest, self.size = stream, hashlib.sha256(), 0

    def read(self, size: int = -1) -> bytes:
        data = self.stream.read(size)
        self.digest.update(data)
        self.size += len(data)
        return data


def _walk(root: Path):
    """Sorted, deterministic walk that never follows a symlink."""
    entries = []
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs.sort()
        here = Path(current)
        for name in sorted(dirs + files):
            path = here / name
            entries.append(path)
    return sorted(entries, key=lambda p: p.relative_to(root).as_posix())


EXTERNAL = '.external'


def finalized_manifest(root: Path | str) -> dict[str, dict[str, Any]]:
    """The record-bound tree manifest, written on the MBP at finalize and committed with the record.

    Relative path -> ``{sha256, size}`` (regular file), ``{link}`` (symlink, kept
    literally) or ``{directory: True}``. Sol's finalized-manifest contract, extended
    with literal links because every ALIGN session's measurement view is links.
    """
    root = Path(root)
    rows: dict[str, dict[str, Any]] = {}
    for path in _walk(root):
        relative = path.relative_to(root).as_posix()
        info = os.lstat(path)
        if stat.S_ISLNK(info.st_mode):
            rows[relative] = {'link': os.readlink(path)}
        elif stat.S_ISDIR(info.st_mode):
            rows[relative] = {'directory': True}
        elif stat.S_ISREG(info.st_mode):
            rows[relative] = {'sha256': _file_sha256(path), 'size': info.st_size}
        else:
            raise OffloadRefused(f'unsupported file type: {relative}')
    return rows


def manifest_sha256(manifest: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _as_finalized(rows: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out = {}
    for name, row in rows.items():
        if 'link' in row:
            out[name] = {'link': row['link']}
        elif row.get('dir'):
            out[name] = {'directory': True}
        else:
            out[name] = {'sha256': row['sha256'], 'size': row['size']}
    return out


def _check_finalized(rows, finalized, where):
    actual = _as_finalized(rows)
    if actual != finalized:
        missing = sorted(set(finalized) - set(actual))
        extra = sorted(set(actual) - set(finalized))
        changed = sorted(k for k in set(actual) & set(finalized) if actual[k] != finalized[k])
        raise OffloadRefused(f'{where} differs from the finalized record manifest: missing={missing[:5]} '
                             f'extra={extra[:5]} changed={changed[:5]}')


def pack(source_root: Path | str, out_dir: Path | str, *, level: int = DEFAULT_LEVEL,
         threads: int = 0, external: tuple[Path | str, ...] = (),
         finalized: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    """Pack ``source_root`` into ``out_dir`` (new). Returns the manifest.

    ``external`` names absolute regular files outside the root that the harvest
    reads at their own path (the measurement checkout's calibration ledger, which
    the window appended to). They travel in the same payload and are restored at
    the same absolute path, append-only: absent, identical or a byte prefix.

    ``finalized`` (the record-bound manifest from finalize): every packed byte,
    link and directory must equal it, or the pack refuses and leaves nothing.
    """
    source = Path(source_root)
    if not source.is_absolute() or source.is_symlink() or not source.is_dir():
        raise OffloadRefused('source root must be an absolute real directory')
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=False)
    rows: dict[str, dict[str, Any]] = {}
    outside: dict[str, dict[str, Any]] = {}
    externals = [Path(p) for p in external]
    for path in externals:
        if not path.is_absolute() or path.is_symlink() or not path.is_file() or _under(path, source):
            raise OffloadRefused(f'external entry must be an absolute regular file outside the root: {path}')
    payload = out / PAYLOAD
    with payload.open('wb') as sink:
        process = subprocess.Popen([zstd_path(), '-q', f'-{int(level)}', f'-T{int(threads)}', '-c'],
                                   stdin=subprocess.PIPE, stdout=sink)
        try:
            with tarfile.open(fileobj=process.stdin, mode='w|', format=tarfile.PAX_FORMAT) as tar:
                for path in _walk(source):
                    relative = path.relative_to(source).as_posix()
                    info = os.lstat(path)
                    tarinfo = tarfile.TarInfo(relative)
                    tarinfo.mode, tarinfo.mtime = stat.S_IMODE(info.st_mode), int(info.st_mtime)
                    tarinfo.uid = tarinfo.gid = 0
                    tarinfo.uname = tarinfo.gname = ''
                    if stat.S_ISLNK(info.st_mode):
                        tarinfo.type, tarinfo.linkname = tarfile.SYMTYPE, os.readlink(path)
                        tar.addfile(tarinfo)
                        rows[relative] = {'link': tarinfo.linkname}
                    elif stat.S_ISDIR(info.st_mode):
                        tarinfo.type = tarfile.DIRTYPE
                        tar.addfile(tarinfo)
                        rows[relative] = {'dir': True, 'mode': tarinfo.mode}
                    elif stat.S_ISREG(info.st_mode):
                        tarinfo.size = info.st_size
                        with path.open('rb') as stream:
                            reader = _HashingReader(stream)
                            tar.addfile(tarinfo, reader)
                        if reader.size != info.st_size:
                            raise OffloadRefused(f'file changed while packing: {relative}')
                        rows[relative] = {'sha256': reader.digest.hexdigest(), 'size': reader.size,
                                          'mode': tarinfo.mode}
                    else:
                        raise OffloadRefused(f'unsupported file type: {relative}')
                for index, path in enumerate(externals):
                    info = os.stat(path)
                    tarinfo = tarfile.TarInfo(f'{EXTERNAL}/{index:04d}')
                    tarinfo.mode, tarinfo.mtime, tarinfo.size = stat.S_IMODE(info.st_mode), int(info.st_mtime), info.st_size
                    with path.open('rb') as stream:
                        reader = _HashingReader(stream)
                        tar.addfile(tarinfo, reader)
                    outside[tarinfo.name] = {'path': str(path), 'sha256': reader.digest.hexdigest(),
                                             'size': reader.size, 'mode': tarinfo.mode}
        finally:
            process.stdin.close()
            code = process.wait()
        if code != 0:
            raise OffloadRefused(f'zstd failed with exit {code}')
    if finalized is not None:
        try:
            _check_finalized(rows, finalized, 'packed tree')
        except OffloadRefused:
            shutil.rmtree(out, ignore_errors=True)
            raise
    manifest = {'schema': SCHEMA, 'source_root': str(source), 'entries': rows, 'external': outside,
                'files': sum('sha256' in r for r in rows.values()),
                'bytes': sum(r.get('size', 0) for r in rows.values()),
                'payload': {'name': PAYLOAD, 'sha256': _file_sha256(payload), 'size': payload.stat().st_size},
                'zstd_level': int(level),
                'finalized_manifest_sha256': manifest_sha256(finalized) if finalized is not None else None}
    (out / MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return manifest


def _under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(CHUNK), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative(name: str) -> PurePosixPath:
    relative = PurePosixPath(name)
    if relative.is_absolute() or not relative.parts or any(p in ('', '.', '..') for p in relative.parts):
        raise OffloadRefused(f'unsafe path in payload: {name!r}')
    return relative


def unpack(offload_dir: Path | str, dest_root: Path | str | None = None, *,
           finalized: dict[str, dict[str, Any]] | None = None,
           finalized_sha256: str | None = None) -> dict[str, Any]:
    """Restore at the manifest's absolute source root after full verification.

    ``dest_root`` must equal the recorded source root (it exists only to make the
    caller state it). The destination must not exist. Returns the manifest.
    With ``finalized`` and ``finalized_sha256`` (the digest committed in the window
    record), the chain committed digest -> finalized manifest -> offload manifest ->
    restored bytes is checked end to end; the self-written manifest alone is not trusted.
    """
    offload = Path(offload_dir)
    manifest = json.loads((offload / MANIFEST).read_bytes())
    if manifest.get('schema') != SCHEMA:
        raise OffloadRefused('not a harvest offload manifest')
    if finalized_sha256 is not None or finalized is not None:
        if finalized is None or finalized_sha256 is None or manifest_sha256(finalized) != finalized_sha256:
            raise OffloadRefused('finalized record manifest missing or not the committed digest')
        _check_finalized(manifest['entries'], finalized, 'offload manifest')
    target = Path(manifest['source_root'])
    if dest_root is not None and Path(dest_root) != target:
        raise OffloadRefused('restore path differs from the recorded source root; harvest bytes would differ')
    if os.path.lexists(target):
        raise OffloadRefused('restore destination already exists')
    payload = offload / manifest['payload']['name']
    if _file_sha256(payload) != manifest['payload']['sha256']:
        raise OffloadRefused('payload digest mismatch')
    staging = target.with_name(target.name + '.restoring')
    if os.path.lexists(staging):
        raise OffloadRefused('stale staging directory present')
    staging.mkdir(parents=True)
    seen: dict[str, dict[str, Any]] = {}
    external_seen: dict[str, dict[str, Any]] = {}
    for name, row in manifest.get('external', {}).items():
        current = Path(row['path'])
        if os.path.lexists(current) and (current.is_symlink() or not current.is_file()):
            raise OffloadRefused(f'external destination is not a regular file: {current}')
    directory_modes: list[tuple[Path, int, int]] = []
    try:
        with subprocess.Popen([zstd_path(), '-q', '-d', '-c', str(payload)], stdout=subprocess.PIPE) as process:
            with tarfile.open(fileobj=process.stdout, mode='r|') as tar:
                for member in tar:
                    if member.name.startswith(EXTERNAL + '/') and member.isfile():
                        external_seen[member.name] = _stage_external(tar, member, staging)
                        continue
                    relative = _safe_relative(member.name)
                    path = staging.joinpath(*relative.parts)
                    if member.issym():
                        path.parent.mkdir(parents=True, exist_ok=True)
                        os.symlink(member.linkname, path)
                        seen[relative.as_posix()] = {'link': member.linkname}
                    elif member.isdir():
                        path.mkdir(parents=True, exist_ok=True)
                        directory_modes.append((path, member.mode, member.mtime))
                        seen[relative.as_posix()] = {'dir': True, 'mode': member.mode}
                    elif member.isfile():
                        path.parent.mkdir(parents=True, exist_ok=True)
                        stream = tar.extractfile(member)
                        digest, size = hashlib.sha256(), 0
                        with path.open('xb') as sink:
                            for chunk in iter(lambda: stream.read(CHUNK), b''):
                                digest.update(chunk)
                                size += len(chunk)
                                sink.write(chunk)
                        os.chmod(path, member.mode)
                        os.utime(path, (member.mtime, member.mtime))
                        seen[relative.as_posix()] = {'sha256': digest.hexdigest(), 'size': size,
                                                     'mode': member.mode}
                    else:
                        raise OffloadRefused(f'unsupported payload entry: {member.name}')
            process.stdout.close()
            if process.wait() != 0:
                raise OffloadRefused('zstd decompression failed')
        for path, mode, mtime in reversed(directory_modes):
            os.chmod(path, mode)
            os.utime(path, (mtime, mtime))
        if seen != manifest['entries']:
            missing = sorted(set(manifest['entries']) - set(seen))
            extra = sorted(set(seen) - set(manifest['entries']))
            changed = sorted(k for k in set(seen) & set(manifest['entries']) if seen[k] != manifest['entries'][k])
            raise OffloadRefused(f'restored tree differs from manifest: missing={missing[:5]} '
                                 f'extra={extra[:5]} changed={changed[:5]}')
        expected = {name: {k: row[k] for k in ('sha256', 'size', 'mode')}
                    for name, row in manifest.get('external', {}).items()}
        if external_seen != expected:
            raise OffloadRefused('external files differ from manifest')
        for name, row in sorted(manifest.get('external', {}).items()):
            _place_external(staging / '.external-staged' / name.rsplit('/', 1)[1], Path(row['path']))
        shutil.rmtree(staging / '.external-staged', ignore_errors=True)
        os.rename(staging, target)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return manifest


def _stage_external(tar, member, staging: Path) -> dict[str, Any]:
    directory = staging / '.external-staged'
    directory.mkdir(exist_ok=True)
    stream = tar.extractfile(member)
    digest, size = hashlib.sha256(), 0
    with (directory / member.name.rsplit('/', 1)[1]).open('xb') as sink:
        for chunk in iter(lambda: stream.read(CHUNK), b''):
            digest.update(chunk)
            size += len(chunk)
            sink.write(chunk)
    os.chmod(directory / member.name.rsplit('/', 1)[1], member.mode)
    return {'sha256': digest.hexdigest(), 'size': size, 'mode': member.mode}


def _place_external(staged: Path, destination: Path) -> None:
    """Append-only placement: absent, identical, or the current bytes are a prefix."""
    new = staged.read_bytes()
    if destination.exists():
        old = destination.read_bytes()
        if old == new:
            return
        if not new.startswith(old):
            raise OffloadRefused(f'external file is not an append-only extension: {destination}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + '.restoring')
    shutil.copy2(staged, temporary)
    os.replace(temporary, destination)


def verify_tree(root: Path | str, manifest: dict[str, Any]) -> list[str]:
    """Re-read a restored tree and return every path whose bytes or link differ."""
    root = Path(root)
    problems = []
    actual: dict[str, dict[str, Any]] = {}
    for path in _walk(root):
        relative = path.relative_to(root).as_posix()
        info = os.lstat(path)
        if stat.S_ISLNK(info.st_mode):
            actual[relative] = {'link': os.readlink(path)}
        elif stat.S_ISDIR(info.st_mode):
            actual[relative] = {'dir': True, 'mode': stat.S_IMODE(info.st_mode)}
        else:
            actual[relative] = {'sha256': _file_sha256(path), 'size': info.st_size,
                                'mode': stat.S_IMODE(info.st_mode)}
    for key in sorted(set(actual) | set(manifest['entries'])):
        if actual.get(key) != manifest['entries'].get(key):
            problems.append(key)
    return problems


# Fields that record WHERE and WHEN a harvest ran, not what it found. Two runs of
# the same code on the same bytes at the same paths differ only here (proven by
# tests/align/test_harvest_off.py); with the clock and boot seams pinned they do
# not differ at all. Everything else must match byte for byte.
PROVENANCE_FIELDS = {
    'derived/flags.jsonl': 'every line: emitted (wall_s, monotonic_ns, boot_session_uuid)',
    'derived/window_flags.json': 'window.boot_session_uuid; collector_errors[].elapsed_s',
    'withheld/collector-errors.json': 'errors[].elapsed_s',
    'withheld/desk-verdict-run.json': 'heartbeats; elapsed_s',
    'harvest.json': 'outputs digests of derived/flags.jsonl and derived/window_flags.json',
}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def archive_projection(archive_root: Path | str) -> dict[str, str]:
    """Relative path -> SHA-256 of the archive with only PROVENANCE_FIELDS removed.

    Use it to compare an MBP harvest archive with an Air harvest archive of the
    same window (the native confirmation run): the dicts must be equal.
    """
    root = Path(archive_root)
    out: dict[str, str] = {}
    for path in _walk(root):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            out[relative] = 'link:' + os.readlink(path)
            continue
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if relative == 'derived/flags.jsonl':
            rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
            for row in rows:
                row.pop('emitted', None)
            raw = b'\n'.join(_canonical(row) for row in rows)
        elif relative == 'derived/window_flags.json':
            value = json.loads(raw)
            (value.get('window') or {}).pop('boot_session_uuid', None)
            for row in value.get('collector_errors') or []:
                row.pop('elapsed_s', None)
            raw = _canonical(value)
        elif relative == 'withheld/collector-errors.json':
            value = json.loads(raw)
            for row in value.get('errors') or []:
                row.pop('elapsed_s', None)
            raw = _canonical(value)
        elif relative == 'withheld/desk-verdict-run.json':
            value = json.loads(raw)
            for key in ('heartbeats', 'elapsed_s'):
                value.pop(key, None)
            raw = _canonical(value)
        elif relative == 'harvest.json':
            value = json.loads(raw)
            for key in ('derived/flags.jsonl', 'derived/window_flags.json'):
                (value.get('outputs') or {}).pop(key, None)
            raw = _canonical(value)
        out[relative] = hashlib.sha256(raw).hexdigest()
    return out
