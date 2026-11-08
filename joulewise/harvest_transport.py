"""Local compressed raw handoff, authenticated by an EXTERNAL finalized manifest.

No discovery of plans, host probes, network, deletion, or locator rewriting.
Call under the offload lane's exclusive cool-down lease. The caller commits
the manifest on the source machine and transports it by an authenticated route.
This module alone neither establishes that provenance nor authorizes an arm.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile

from joulewise.desk_compress import CHUNK_BYTES, zstd_path


def _manifest(value):
    if not isinstance(value, dict):
        raise ValueError('manifest must be an object')
    if any(not isinstance(name, str) for name in value):
        raise ValueError('manifest paths must be strings')
    result = {}
    for name, row in sorted(value.items()):
        if (not isinstance(name, str) or not name or '\\' in name
                or PurePosixPath(name).is_absolute() or str(PurePosixPath(name)) != name
                or any(p in ('..', '.') for p in name.split('/'))
                or not isinstance(row, dict)):
            raise ValueError('invalid manifest entry')
        is_directory = set(row) == {'directory'} and row['directory'] is True
        if not is_directory and (set(row) != {'sha256', 'size'}
                or type(row['size']) is not int or row['size'] < 0
                or not isinstance(row['sha256'], str)
                or not re.fullmatch('[0-9a-f]{64}', row['sha256'])):
            raise ValueError('invalid manifest entry')
        result[name] = dict(row)
    for name in result:
        for parent in PurePosixPath(name).parents:
            if str(parent) != '.' and result.get(str(parent)) != {'directory': True}:
                raise ValueError('manifest omits a directory or overlaps a file')
    return result


def _directories(root):
    return {str((Path(directory)/name).relative_to(root))
            for directory, dirs, _ in os.walk(root, followlinks=False) for name in dirs}


def _names(root):
    # Reject links before following them, including root/ancestor links.
    for path in (root, *root.parents):
        if path.is_symlink():
            raise ValueError('symlink input')
    if not root.is_dir():
        raise ValueError('missing input tree')
    result = set()
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(directory)/name
            if path.is_symlink():
                raise ValueError('symlink input')
            if name in files:
                if not path.is_file():
                    raise ValueError('nonregular input')
                result.add(path.relative_to(root).as_posix())
    return result


def _signature(path):
    s = path.stat()
    return s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns


def _hash_read(source, expected, sink=None):
    before = _signature(source)
    digest, size = hashlib.sha256(), 0
    with source.open('rb') as stream:
        for block in iter(lambda: stream.read(CHUNK_BYTES), b''):
            digest.update(block)
            size += len(block)
            if sink is not None:
                sink.write(block)
    if (size != expected['size'] or digest.hexdigest() != expected['sha256']
            or _signature(source) != before):
        raise ValueError('raw digest/size changed: ' + str(source))


def _compress(source, target, expected):
    # Fixed one-thread zstd and content size: deterministic at a pinned version.
    # Tee the single source read into SHA-256 and compression; no hash pre-pass.
    process = subprocess.Popen([zstd_path(), '-3', '-q', '-T1',
        '--stream-size=' + str(expected['size']), '-o', str(target)],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        _hash_read(source, expected, process.stdin)
        process.stdin.close()
        if process.wait() != 0:
            raise ValueError('compression_failed')
        with target.open('rb') as stream:
            os.fsync(stream.fileno())
    finally:
        if not process.stdin.closed:
            try:
                process.stdin.close()
            except BrokenPipeError:
                pass
        if process.poll() is None:
            process.kill()
        process.wait()


def _publish(stage, destination, marker):
    # Exclusive ownership, receipt LAST. A crash leaves an incomplete directory,
    # never a verified copy. The offload lease serializes readers/publishers.
    destination.mkdir(exist_ok=False)
    for path in stage.iterdir():
        if path.name != marker:
            path.rename(destination/path.name)
    if marker is not None:
        (stage/marker).rename(destination/marker)
    for directory, _, _ in os.walk(destination, topdown=False):
        fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    fd = os.open(destination.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def pack_raw(source, destination, finalized_manifest, *, workers=1):
    """Create an immutable transport tree; never replace/delete source files.

    Unique contents compress in parallel; duplicate files are independently
    hashed but compressed only once. Every source byte is read once. The
    receiver must still decompress/hash against the separately pinned manifest.
    """
    if type(workers) is not int or not 1 <= workers <= 8:
        raise ValueError('workers must be in 1..8')
    source, destination = Path(source).absolute(), Path(destination).absolute()
    if (source == destination or source in destination.parents or destination in source.parents):
        raise ValueError('source/destination overlap')
    expected = _manifest(finalized_manifest)
    files = {name: row for name, row in expected.items() if 'sha256' in row}
    directories = set(expected)-set(files)
    if _names(source) != set(files) or _directories(source) != directories:
        raise ValueError('missing or extra raw file')
    signatures = {name: _signature(source/name) for name in files}
    destination.parent.mkdir(parents=True, exist_ok=True)
    groups = {}
    for name, row in files.items():
        groups.setdefault(row['sha256'], []).append(name)

    with tempfile.TemporaryDirectory(prefix='.raw-pack-', dir=destination.parent) as tmp:
        stage = Path(tmp)
        (stage/'payloads').mkdir()

        def group(names):
            first, *duplicates = names
            row = expected[first]
            _compress(source/first, stage/'payloads'/(row['sha256']+'.zst'), row)
            for name in duplicates:
                _hash_read(source/name, expected[name])

        # Bounded submission, deterministic error order, one zstd thread/job.
        with ThreadPoolExecutor(max_workers=workers) as pool:
            pending = []
            for names in groups.values():
                pending.append(pool.submit(group, names))
                if len(pending) == 2*workers:
                    pending.pop(0).result()
            for future in pending:
                future.result()
        if (_names(source) != set(files) or _directories(source) != directories
                or any(_signature(source/name) != signatures[name] for name in files)):
            raise ValueError('raw tree changed during pack')
        (stage/'manifest.json').write_text(json.dumps(expected, sort_keys=True)+'\n')
        with (stage/'manifest.json').open('rb') as stream:
            os.fsync(stream.fileno())
        payload_bytes = sum(p.stat().st_size for p in (stage/'payloads').iterdir())
        _publish(stage, destination, 'manifest.json')
    return {'files': len(files), 'payloads': len(groups),
            'raw_bytes': sum(r['size'] for r in files.values()), 'payload_bytes': payload_bytes}


def unpack_raw(package, destination, finalized_manifest):
    """Restore into a new tree; verify EVERY raw file before publishing receipt.

    Restored bytes, hence the canonical custody SHA256SUMS, are identical. File
    times/modes are not custody bytes and are intentionally not copied. A
    transport manifest is not accepted as its own source of provenance.
    """
    package, destination = Path(package).absolute(), Path(destination).absolute()
    if package == destination or package in destination.parents or destination in package.parents:
        raise ValueError('package/destination overlap')
    expected = _manifest(finalized_manifest)
    files = {name: row for name, row in expected.items() if 'sha256' in row}
    payloads = {'payloads/'+r['sha256']+'.zst' for r in files.values()}
    if _names(package) != payloads | {'manifest.json'}:
        raise ValueError('missing or extra transport file')
    if json.loads((package/'manifest.json').read_bytes()) != expected:
        raise ValueError('transport differs from finalized manifest')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.raw-unpack-', dir=destination.parent) as tmp:
        stage = Path(tmp)
        (stage/'raw').mkdir()
        for name in set(expected)-set(files):
            (stage/'raw'/name).mkdir(parents=True, exist_ok=True)
        for name, row in files.items():
            target = stage/'raw'/name
            target.parent.mkdir(parents=True, exist_ok=True)
            digest, size = hashlib.sha256(), 0
            with target.open('xb') as stream, subprocess.Popen([zstd_path(), '-d', '-q', '-c',
                    str(package/'payloads'/(row['sha256']+'.zst'))], stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL) as process:
                try:
                    for block in iter(lambda: process.stdout.read(CHUNK_BYTES), b''):
                        size += len(block)
                        if size > row['size']:
                            raise ValueError('restored size exceeds manifest')
                        digest.update(block)
                        stream.write(block)
                    if process.wait() != 0 or size != row['size'] or digest.hexdigest() != row['sha256']:
                        raise ValueError('restored digest/size mismatch')
                    stream.flush()
                    os.fsync(stream.fileno())
                finally:
                    if process.poll() is None:
                        process.kill()
        (stage/'raw').mkdir(exist_ok=True)
        # No marker is inserted into the raw tree: its exact file set is preserved.
        # A successful return plus the caller's offload receipt authenticates it.
        _publish(stage/'raw', destination, None)
    return destination
