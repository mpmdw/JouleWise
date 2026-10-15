"""The single path fence and all kit-owned filesystem operations."""
from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
from pathlib import Path

ARCHIVE = Path('/Users/edr/night-archive/threshold-validation')
BLINDED = (Path('/Users/edr/night-custody'), Path('/Users/edr/night-b5'),
           Path('/Users/edr/night-g2a'))


def fence(path: str | Path) -> Path:
    """Reject lexical and symlink aliases before opening a path.

The lexical test runs before resolution, so a directly forbidden input is
never statted. Symlink aliases are resolved without listing their targets.
"""
    def check(p: Path) -> None:
        # The Mac's usual APFS volume is case-insensitive, and its Data
        # volume exposes /Users through a firmlink rather than a symlink.
        # Reject both spellings lexically, before any stat of their targets.
        parts = tuple(part.casefold() for part in p.parts)
        if parts[:4] == ('/', 'system', 'volumes', 'data'):
            parts = ('/', *parts[4:])
        roots = [tuple(part.casefold() for part in root.parts) for root in BLINDED]
        if any(parts[:len(root)] == root for root in roots):
            raise ValueError(f'blinded path: {p}')
        archive = ('/', 'users', 'edr', 'night-archive')
        if parts[:len(archive)] == archive and len(parts) > len(archive):
            part = parts[len(archive)]
            if part.startswith('harvest-v5-b5-'):
                raise ValueError(f'blinded path: {p}')
        # No ledger or head pin is an input to this calibration kit.
        if any('ledger' in part.lower() or 'head_pin' in part.lower()
               or 'head-pin' in part.lower() for part in p.parts):
            raise ValueError(f'ledger/head pin forbidden: {p}')
    candidate = Path(os.path.abspath(os.path.expanduser(str(path))))
    check(candidate)
    # Resolve one link at a time. Path.resolve() can otherwise traverse a
    # blinded target before the final check sees the alias.
    links = 0
    pending = list(candidate.parts[1:])
    cursor = Path(candidate.anchor)
    while pending:
        part = pending.pop(0)
        next_path = cursor / part
        check(next_path)
        try:
            mode = os.lstat(next_path).st_mode
        except FileNotFoundError:
            cursor = next_path
            continue
        if stat.S_ISLNK(mode):
            links += 1
            if links > 40:
                raise ValueError('too many symbolic links')
            link = Path(os.readlink(next_path))
            expanded = Path(os.path.abspath((link if link.is_absolute() else cursor/link).joinpath(*pending)))
            check(expanded)
            pending = list(expanded.parts[1:])
            cursor = Path(expanded.anchor)
        else:
            cursor = next_path
    check(cursor)
    return cursor


def mkdir(path: str | Path) -> Path:
    target = fence(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def executable(path: str | Path) -> str:
    """Fence aliases but retain the invocation path (a venv depends on it)."""
    fence(path)
    return os.path.abspath(os.path.expanduser(str(path)))


def read_bytes(path: str | Path) -> bytes:
    return fence(path).read_bytes()


def read_json(path: str | Path, default=None):
    try:
        return json.loads(read_bytes(path))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def fsync_dir(path: str | Path) -> None:
    fd = os.open(fence(path), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic(path: str | Path, data: bytes) -> None:
    target = fence(path)
    mkdir(target.parent)
    fd, name = tempfile.mkstemp(prefix='.' + target.name + '-', dir=fence(target.parent))
    temporary = fence(name)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(fence(temporary), fence(target))
        fsync_dir(target.parent)
    finally:
        if fence(temporary).exists():
            fence(temporary).unlink()


def atomic_json(path: str | Path, value) -> None:
    atomic(path, (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode())


def append(path: str | Path, value, *, sync=True) -> None:
    target = fence(path)
    mkdir(target.parent)
    with target.open('ab') as handle:
        handle.write((json.dumps(value, sort_keys=True, allow_nan=False) + '\n').encode())
        handle.flush()
        if sync:
            os.fsync(handle.fileno())


def create_once(path: str | Path, data: bytes) -> bool:
    target = fence(path)
    mkdir(target.parent)
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(fd, 'wb') as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    fsync_dir(target.parent)
    return True


def children(path: str | Path) -> list[Path]:
    target = fence(path)
    if not target.exists():
        return []
    return [fence(p) for p in target.iterdir()]


def files(path: str | Path):
    """Traverse only this explicit directory, checking each entry before descent."""
    for child in sorted(children(path)):
        if child.is_dir():
            yield from files(child)
        elif child.is_file():
            yield child


def inventory(directory: Path) -> list[dict]:
    return [{'path': str(p.relative_to(directory)), 'size': len(raw),
             'sha256': hashlib.sha256(raw).hexdigest()}
            for p in files(directory) if p.name not in {'result.json', 'summary.md', 'attempt.json'}
            and not p.name.startswith('analysis')
            for raw in [read_bytes(p)]]
