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

Record binding (R17 review F1/F2 and the Sol seat-2 custody findings): ``finalized_manifest``
is written on the MBP at finalize and its digest is committed in the window record. It binds
the restore namespace, every tree entry and the finite closure of external inputs that the
tree's links point at. ``pack`` and ``unpack`` require it; the self-written transport manifest
is checked against it and is never the authority for a path, a destination or a namespace.
``pack_unbound``/``unpack_unbound`` are the separately named synthetic/legacy seams.

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
FINALIZED_SCHEMA = 'joulewise.align_v4.finalized_manifest.v2'
FINALIZED_KEYS = frozenset({'schema', 'source_root', 'entries', 'closure'})
# R17 review F1: the finite external-input closure. A link whose target leaves the session root is
# a dependency: it is bound either by the bytes it reaches (hashed at finalize, re-verified at pack
# and on the Air) or, for the measurement checkout, by the separately bound mirror identity. These
# bounds make the byte closure finite. Anything past them refuses at finalize: it must become a
# declared mirror or input. Closure bytes are hashed in place, never copied, except the declared
# append-only externals (the calibration ledger). Model weights never fit the per-file bound.
CLOSURE_MAX_FILES = 4096
CLOSURE_MAX_BYTES = 1 << 30
CLOSURE_MAX_FILE_BYTES = 256 << 20


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def manifest_sha256(manifest: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(manifest)).hexdigest()


def _tree_rows(root: Path) -> dict[str, dict[str, Any]]:
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


class _ClosureFiles:
    """Accumulates the closure's regular files, enforcing the finite bounds before any hash."""

    def __init__(self):
        self.files: dict[str, dict[str, Any]] = {}
        self.total = 0

    def add(self, path: Path, why: str) -> None:
        key = str(path)
        if key in self.files:
            return
        info = os.lstat(path)
        if stat.S_ISLNK(info.st_mode):
            raise OffloadRefused(f'external closure reaches a further link ({why}): {path}; declare it as a mirror or input')
        if not stat.S_ISREG(info.st_mode):
            raise OffloadRefused(f'external closure entry is not a regular file ({why}): {path}')
        if info.st_size > CLOSURE_MAX_FILE_BYTES:
            raise OffloadRefused(f'external closure file over {CLOSURE_MAX_FILE_BYTES} bytes ({why}): {path}; '
                                 'large inputs (model weights) are never bound or copied; bind them by a mirror')
        self.total += info.st_size
        if len(self.files) + 1 > CLOSURE_MAX_FILES or self.total > CLOSURE_MAX_BYTES:
            raise OffloadRefused(f'external closure is not finite within {CLOSURE_MAX_FILES} files / '
                                 f'{CLOSURE_MAX_BYTES} bytes ({why}); declare a mirror instead of traversing it')
        self.files[key] = {'sha256': _file_sha256(path), 'size': info.st_size}


def _directory_listing(target: Path) -> list[str]:
    """Regular-file listing below an external directory link; never follows a link."""
    names = []
    for current, dirs, files in os.walk(target, followlinks=False):
        here = Path(current)
        for name in dirs:
            if (here / name).is_symlink():
                raise OffloadRefused(f'external closure reaches a further link: {here / name}; declare it')
        names.extend((here / name).relative_to(target).as_posix() for name in files)
    return sorted(names)


def _classify_link(path: Path, root_real: Path, mirror_real: Path | None) -> tuple[str, Path]:
    target = Path(os.path.realpath(path))
    if _under(target, root_real):
        return 'internal', target
    if mirror_real is not None and _under(target, mirror_real):
        return 'mirror', target
    if not os.path.lexists(target):
        return 'absent', target
    return 'bytes', target


def _closure(root: Path, *, mirror: dict[str, Any] | None, inputs: tuple[Path | str, ...]) -> dict[str, Any]:
    root_real = Path(os.path.realpath(root))
    mirror_real = Path(os.path.realpath(mirror['root'])) if mirror is not None else None
    collected = _ClosureFiles()
    links: dict[str, dict[str, Any]] = {}
    for path in _walk(root):
        if not path.is_symlink():
            continue
        relative = path.relative_to(root).as_posix()
        kind, target = _classify_link(path, root_real, mirror_real)
        if kind == 'internal':
            continue
        row: dict[str, Any] = {'class': kind, 'target': str(target)}
        if kind == 'bytes':
            if target.is_dir():
                listing = _directory_listing(target)
                for name in listing:
                    collected.add(target / name, relative)
                row.update(kind='directory', files=listing)
            else:
                collected.add(target, relative)
                row['kind'] = 'file'
        links[relative] = row
    declared = []
    for value in inputs:
        path = Path(value)
        if not path.is_absolute() or path.is_symlink() or not path.is_file() or _under(path, root):
            raise OffloadRefused(f'declared input must be an absolute regular file outside the root: {path}')
        collected.add(path, 'declared input')
        declared.append(str(path))
    if mirror is not None and (not isinstance(mirror, dict) or set(mirror) != {'root', 'identity'}
                               or not isinstance(mirror['identity'], dict)):
        raise OffloadRefused('mirror must be {root, identity}')
    return {'links': links, 'files': collected.files, 'inputs': sorted(declared), 'mirror': mirror}


def finalized_manifest(root: Path | str, *, mirror: dict[str, Any] | None = None,
                       inputs: tuple[Path | str, ...] = ()) -> dict[str, Any]:
    """The record-bound manifest, written on the MBP at finalize and committed with the record.

    ``entries``: relative path -> ``{sha256, size}`` (regular file), ``{link}`` (symlink, kept
    literally) or ``{directory: True}``. ``source_root``: the restore namespace. ``closure``: the
    finite inventory of the external inputs that links point at (R17 review F1):

    * a link into ``mirror['root']`` (the measurement checkout) is bound by ``mirror['identity']``
      (head, clean incl. untracked, interpreter and packages), which the Air must reproduce;
    * any other external link target is bound by the bytes it reaches (a file, or every regular file
      below a directory), within the finite bounds; an absent target stays bound as absent;
    * ``inputs`` are further absolute files bound by bytes (the calibration ledger the window appended).

    The external bytes are re-verified at pack and on the Air before the tree is published.
    """
    root = Path(root)
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise OffloadRefused('source root must be an absolute real directory')
    return {'schema': FINALIZED_SCHEMA, 'source_root': str(root), 'entries': _tree_rows(root),
            'closure': _closure(root, mirror=mirror, inputs=inputs)}


def _validate_finalized(finalized: Any) -> None:
    closure = finalized.get('closure') if isinstance(finalized, dict) else None
    if (not isinstance(finalized, dict) or set(finalized) != FINALIZED_KEYS
            or finalized.get('schema') != FINALIZED_SCHEMA or not isinstance(finalized.get('source_root'), str)
            or not isinstance(finalized.get('entries'), dict) or not isinstance(closure, dict)
            or set(closure) != {'links', 'files', 'inputs', 'mirror'}):
        raise OffloadRefused('finalized record manifest malformed (schema ' + FINALIZED_SCHEMA + ')')


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


def _check_finalized(rows, finalized_entries, where):
    actual = _as_finalized(rows)
    if actual != finalized_entries:
        missing = sorted(set(finalized_entries) - set(actual))
        extra = sorted(set(actual) - set(finalized_entries))
        changed = sorted(k for k in set(actual) & set(finalized_entries) if actual[k] != finalized_entries[k])
        raise OffloadRefused(f'{where} differs from the finalized record manifest: missing={missing[:5]} '
                             f'extra={extra[:5]} changed={changed[:5]}')


def _verify_closure(closure: dict[str, Any], root: Path, *, mirror_identity: dict[str, Any] | None,
                    transported: frozenset[str] = frozenset(), where: str) -> None:
    """Re-verify the closure against this host's bytes; ``root`` is where the tree is now (or staged)."""
    mirror = closure['mirror']
    if mirror is not None and mirror_identity != mirror['identity']:
        raise OffloadRefused(f'{where}: measurement checkout mirror differs from the finalized record manifest: '
                             + json.dumps({'finalized': mirror['identity'], 'here': mirror_identity}, sort_keys=True))
    root_real = Path(os.path.realpath(root))
    mirror_real = Path(os.path.realpath(mirror['root'])) if mirror is not None else None
    for relative, row in sorted(closure['links'].items()):
        kind, target = _classify_link(root / relative, root_real, mirror_real)
        if kind != row['class'] or (kind != 'mirror' and str(target) != row['target']):
            raise OffloadRefused(f'{where}: external link {relative} resolves differently from the finalized '
                                 f'record manifest ({kind} {target})')
        if kind == 'bytes' and row['kind'] == 'directory' and _directory_listing(target) != row['files']:
            raise OffloadRefused(f'{where}: external closure directory differs from the finalized record '
                                 f'manifest: {target}')
        if kind == 'bytes' and row['kind'] == 'file' and target.is_dir():
            raise OffloadRefused(f'{where}: external closure file became a directory: {target}')
    for name, row in sorted(closure['files'].items()):
        if name in transported:
            continue
        path = Path(name)
        try:
            info = os.lstat(path)
            same = (stat.S_ISREG(info.st_mode) and info.st_size == row['size']
                    and _file_sha256(path) == row['sha256'])
        except OSError:
            same = False
        if not same:
            raise OffloadRefused(f'{where}: external closure input differs from the finalized record manifest: {path}')


def _closure_external(finalized: dict[str, Any], path: str, sha256: str, size: int) -> None:
    row = finalized['closure']['files'].get(path)
    if row is None:
        raise OffloadRefused(f'external file is not bound by the finalized record manifest: {path}')
    if row != {'sha256': sha256, 'size': size}:
        raise OffloadRefused(f'external input differs from the finalized record manifest: {path}')


def pack(source_root: Path | str, out_dir: Path | str, *, finalized: dict[str, Any] | None,
         level: int = DEFAULT_LEVEL, threads: int = 0, external: tuple[Path | str, ...] = (),
         mirror_identity: dict[str, Any] | None = None) -> dict[str, Any]:
    """Pack ``source_root`` into ``out_dir`` (new), bound to the finalized record manifest. Returns the manifest.

    ``finalized`` (the record-bound manifest from finalize) is REQUIRED (R17 review F2): every
    packed byte, link and directory must equal it, its external closure must still hold on this
    host (``mirror_identity`` is this host's checkout identity when it binds a mirror), and every
    ``external`` file must be a closure file with the bound bytes; otherwise the pack refuses and
    leaves nothing.

    ``external`` names absolute regular files outside the root that the harvest reads at their own
    path (the measurement checkout's calibration ledger, which the window appended to). They travel
    in the same payload and are restored at the same absolute path, append-only.
    """
    if finalized is None:
        raise OffloadRefused('pack requires the finalized record manifest (record-bound); '
                             'pack_unbound is the synthetic/legacy seam only')
    _validate_finalized(finalized)
    source = Path(source_root)
    if str(source) != finalized['source_root']:
        raise OffloadRefused('source root differs from the finalized record manifest')
    for path in external:
        if str(Path(path)) not in finalized['closure']['files']:
            raise OffloadRefused(f'external file is not bound by the finalized record manifest: {path}')
    if source.is_dir() and not source.is_symlink():
        _verify_closure(finalized['closure'], source, mirror_identity=mirror_identity, where='pack')

    def check(rows, outside):
        _check_finalized(rows, finalized['entries'], 'packed tree')
        for row in outside.values():
            _closure_external(finalized, row['path'], row['sha256'], row['size'])

    return _pack(source, Path(out_dir), level=level, threads=threads, external=external, check=check,
                 finalized_sha256=manifest_sha256(finalized))


def pack_unbound(source_root: Path | str, out_dir: Path | str, *, level: int = DEFAULT_LEVEL,
                 threads: int = 0, external: tuple[Path | str, ...] = ()) -> dict[str, Any]:
    """SYNTHETIC/LEGACY seam: pack with no record binding. Never the production route (the CLI refuses it)."""
    return _pack(Path(source_root), Path(out_dir), level=level, threads=threads, external=external,
                 check=None, finalized_sha256=None)


def _pack(source: Path, out: Path, *, level, threads, external, check, finalized_sha256) -> dict[str, Any]:
    if not source.is_absolute() or source.is_symlink() or not source.is_dir():
        raise OffloadRefused('source root must be an absolute real directory')
    externals = [Path(p) for p in external]
    for path in externals:
        if not path.is_absolute() or path.is_symlink() or not path.is_file() or _under(path, source):
            raise OffloadRefused(f'external entry must be an absolute regular file outside the root: {path}')
    out.mkdir(parents=True, exist_ok=False)
    try:
        rows: dict[str, dict[str, Any]] = {}
        outside: dict[str, dict[str, Any]] = {}
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
                        tarinfo.mode, tarinfo.mtime, tarinfo.size = (stat.S_IMODE(info.st_mode), int(info.st_mtime),
                                                                     info.st_size)
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
        if check is not None:
            check(rows, outside)
        manifest = {'schema': SCHEMA, 'source_root': str(source), 'entries': rows, 'external': outside,
                    'files': sum('sha256' in r for r in rows.values()),
                    'bytes': sum(r.get('size', 0) for r in rows.values()),
                    'payload': {'name': PAYLOAD, 'sha256': _file_sha256(payload), 'size': payload.stat().st_size},
                    'zstd_level': int(level), 'finalized_manifest_sha256': finalized_sha256}
        (out / MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    except BaseException:
        shutil.rmtree(out, ignore_errors=True)
        raise
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


def _real_parent(staging: Path, relative: PurePosixPath) -> Path:
    """The member's parent inside staging; refuses unless every ancestor is a real directory already restored.

    A payload member can therefore never be written through a restored symlink (for example below the
    measurement view, which links into the checkout) or into a directory the manifest does not hold.
    """
    parent = staging
    for part in relative.parts[:-1]:
        parent = parent / part
        try:
            info = os.lstat(parent)
        except FileNotFoundError:
            raise OffloadRefused(f'unsafe path in payload (parent not restored first): {relative}') from None
        if not stat.S_ISDIR(info.st_mode):
            raise OffloadRefused(f'unsafe path in payload (through a link or file): {relative}')
    return parent


def unpack(offload_dir: Path | str, dest_root: Path | str | None = None, *,
           finalized: dict[str, Any] | None, finalized_sha256: str | None,
           mirror_identity: dict[str, Any] | None = None) -> dict[str, Any]:
    """Restore at the finalized source root after full verification. Returns the transport manifest.

    ``finalized`` and ``finalized_sha256`` (the digest committed in the window record) are REQUIRED
    (R17 review F2): the chain committed digest -> finalized manifest -> offload manifest -> restored
    bytes -> external closure on this host is checked before anything is published; the
    self-written transport manifest alone is never trusted. The restore namespace and every
    external destination come from the finalized manifest. ``mirror_identity`` is this host's
    checkout identity when the finalized manifest binds a mirror.

    ``dest_root`` must equal the recorded source root (it exists only to make the caller state it).
    The destination must not exist.
    """
    if finalized is None or finalized_sha256 is None or manifest_sha256(finalized) != finalized_sha256:
        raise OffloadRefused('finalized record manifest missing or not the committed digest')
    _validate_finalized(finalized)
    return _unpack(Path(offload_dir), dest_root, finalized=finalized, mirror_identity=mirror_identity)


def unpack_unbound(offload_dir: Path | str, dest_root: Path | str | None = None) -> dict[str, Any]:
    """SYNTHETIC/LEGACY seam: restore against the self-written manifest only. Never the production route."""
    return _unpack(Path(offload_dir), dest_root, finalized=None, mirror_identity=None)


def _unpack(offload: Path, dest_root, *, finalized, mirror_identity) -> dict[str, Any]:
    manifest = json.loads((offload / MANIFEST).read_bytes())
    if manifest.get('schema') != SCHEMA:
        raise OffloadRefused('not a harvest offload manifest')
    if finalized is not None:
        if manifest.get('source_root') != finalized['source_root']:
            raise OffloadRefused('offload manifest restore namespace differs from the finalized record manifest')
        if manifest.get('finalized_manifest_sha256') != manifest_sha256(finalized):
            raise OffloadRefused('offload manifest differs from the finalized record manifest (packed against another)')
        _check_finalized(manifest['entries'], finalized['entries'], 'offload manifest')
        for row in manifest.get('external', {}).values():
            _closure_external(finalized, row.get('path'), row.get('sha256'), row.get('size'))
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
    entries = manifest['entries']
    externals = manifest.get('external', {})
    for name, row in externals.items():
        current = Path(row['path'])
        if os.path.lexists(current) and (current.is_symlink() or not current.is_file()):
            raise OffloadRefused(f'external destination is not a regular file: {current}')
    staging.mkdir(parents=True)
    seen: dict[str, dict[str, Any]] = {}
    external_seen: dict[str, dict[str, Any]] = {}
    directory_modes: list[tuple[Path, int, int]] = []
    try:
        with subprocess.Popen([zstd_path(), '-q', '-d', '-c', str(payload)], stdout=subprocess.PIPE) as process:
            with tarfile.open(fileobj=process.stdout, mode='r|') as tar:
                for member in tar:
                    if member.name.startswith(EXTERNAL + '/') and member.isfile():
                        if member.name not in externals or member.name in external_seen:
                            raise OffloadRefused(f'external payload entry not in the manifest: {member.name}')
                        external_seen[member.name] = _stage_external(tar, member, staging)
                        continue
                    relative = _safe_relative(member.name)
                    name = relative.as_posix()
                    expected = entries.get(name)
                    # Every member is checked against the manifest BEFORE anything is written for it.
                    if expected is None or name in seen:
                        raise OffloadRefused(f'restored tree differs from manifest: extra={[name]}')
                    kind = 'link' if member.issym() else 'dir' if member.isdir() else 'file' if member.isfile() else None
                    if kind is None:
                        raise OffloadRefused(f'unsupported payload entry: {member.name}')
                    if kind != ('link' if 'link' in expected else 'dir' if expected.get('dir') else 'file'):
                        raise OffloadRefused(f'restored tree differs from manifest: changed={[name]}')
                    path = _real_parent(staging, relative) / relative.name
                    if kind == 'link':
                        os.symlink(member.linkname, path)
                        seen[name] = {'link': member.linkname}
                    elif kind == 'dir':
                        path.mkdir()
                        directory_modes.append((path, member.mode, member.mtime))
                        seen[name] = {'dir': True, 'mode': member.mode}
                    else:
                        stream = tar.extractfile(member)
                        digest, size = hashlib.sha256(), 0
                        with path.open('xb') as sink:
                            for chunk in iter(lambda: stream.read(CHUNK), b''):
                                digest.update(chunk)
                                size += len(chunk)
                                sink.write(chunk)
                        os.chmod(path, member.mode)
                        os.utime(path, (member.mtime, member.mtime))
                        seen[name] = {'sha256': digest.hexdigest(), 'size': size, 'mode': member.mode}
            process.stdout.close()
            if process.wait() != 0:
                raise OffloadRefused('zstd decompression failed')
        for path, mode, mtime in reversed(directory_modes):
            os.chmod(path, mode)
            os.utime(path, (mtime, mtime))
        if seen != entries:
            missing = sorted(set(entries) - set(seen))
            extra = sorted(set(seen) - set(entries))
            changed = sorted(k for k in set(seen) & set(entries) if seen[k] != entries[k])
            raise OffloadRefused(f'restored tree differs from manifest: missing={missing[:5]} '
                                 f'extra={extra[:5]} changed={changed[:5]}')
        expected_external = {name: {k: row[k] for k in ('sha256', 'size', 'mode')} for name, row in externals.items()}
        if external_seen != expected_external:
            raise OffloadRefused('external files differ from manifest')
        if finalized is not None:
            # The external closure must hold on THIS host before the tree is published (R17 review F1).
            _verify_closure(finalized['closure'], staging, mirror_identity=mirror_identity,
                            transported=frozenset(row['path'] for row in externals.values()), where='unpack')
        for name, row in sorted(externals.items()):
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
