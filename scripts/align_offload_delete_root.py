#!/usr/bin/env python3
"""Ed-only offload guard; stdlib, no environment imports, no shell deletion.

All preflight refusals precede rmtree. A later OS/I/O failure can still leave a
partial tree; it is logged FAILED_PARTIAL, never DELETED. Requires quiescence.
Non-delete subcommands only inventory opaque bytes or compute a tar budget.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import unicodedata

MANDATORY_KEEP = tuple(Path(p) for p in (
    '/Users/edr/code/JouleWise', '/Users/edr/night-custody',
    '/Users/edr/night-b5', '/Users/edr/night-g2a', '/Users/edr/night-archive',
    '/Users/edr/night-plan-staging', '/Users/edr/night-b6', '/Users/edr/night-bytes',
    '/Users/edr/jw_models', '/Users/edr/.cache/huggingface/hub',
    '/Users/edr/Library/LaunchAgents',
))
ALIGN_ROOT = Path('/Users/edr/night-align')
DATALESS = 0x40000000
LOCK_FLAGS = 0x2 | 0x4 | 0x20000 | 0x40000  # uchg/uappnd/schg/sappnd


class Refusal(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise Refusal(reason)


def digest(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
        h.update(chunk)
    return h.hexdigest()


def safe_name(name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts and
            not {'restricted', 'withheld'} & {x.casefold() for x in p.parts},
            'unsafe or blinded member')
    return p.as_posix()


def exact_path(raw):
    require(isinstance(raw, str) and raw == raw.strip() and
            unicodedata.normalize('NFC', raw) == raw and
            not any(c in raw for c in '\t\n\r\0'), 'non-canonical path text')
    p = Path(raw)
    require(p.is_absolute() and str(p) == raw and '..' not in p.parts and
            not {'restricted', 'withheld'} & {x.casefold() for x in p.parts},
            'non-canonical or blinded path')
    # lstat each component: no symlink ancestors, even a link back into tree.
    for part in reversed((p, *p.parents)):
        require(not stat.S_ISLNK(part.lstat().st_mode), 'symlink path component')
    require(p.resolve(strict=True) == p, 'unresolved path')
    return p


def identity(p):
    s = p.stat()
    return s.st_dev, s.st_ino


def overlaps(src, keep):
    # Do NOT intersect both ancestor sets: their common filesystem root is OK.
    return (identity(src) in {identity(p) for p in (keep, *keep.parents)} or
            identity(keep) in {identity(p) for p in (src, *src.parents)})


def check_keep(src, keep_file, mandatory=None):
    mandatory = MANDATORY_KEEP if mandatory is None else mandatory
    lines = keep_file.read_text().splitlines()
    require(bool(lines) and len(lines) == len(set(lines)), 'empty/duplicate KEEP')
    keeps = [exact_path(line) for line in lines]  # missing entries refuse
    # Every mandatory spelling must be present, and must exist on this host.
    require(all(str(p) in lines for p in mandatory), 'missing mandatory KEEP')
    for keep in keeps:
        require(not overlaps(src, keep), 'KEEP inode overlap')


def tree(root):
    root = exact_path(str(root))
    require(root.is_dir(), 'source not directory')
    device, rows = root.stat().st_dev, []

    def walk(directory):
        for p in sorted(directory.iterdir()):
            name = safe_name(p.relative_to(root).as_posix())
            s = p.lstat()
            require(s.st_dev == device, 'nested filesystem')
            require(not getattr(s, 'st_flags', 0) & DATALESS, 'dataless source')
            mode = stat.S_IMODE(s.st_mode)
            if stat.S_ISLNK(s.st_mode):
                rows.append([name, 'link', mode, os.readlink(p)])
            elif stat.S_ISDIR(s.st_mode):
                rows.append([name, 'dir', mode])
                walk(p)
            elif stat.S_ISREG(s.st_mode):
                require(s.st_nlink == 1, 'hardlink source')
                with p.open('rb') as f:
                    sha = digest(f)
                after = p.lstat()
                require((s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns) ==
                        (after.st_dev, after.st_ino, after.st_size,
                         after.st_mtime_ns, after.st_ctime_ns), 'source changed')
                rows.append([name, 'file', mode, s.st_size, sha])
            else:
                raise Refusal('special file')
    require(not getattr(root.stat(), 'st_flags', 0) & DATALESS, 'dataless root')
    walk(root)
    return sorted(rows)


def archive(stream):
    rows, seen = [], set()
    with tarfile.open(fileobj=stream, mode='r|') as tf:
        for m in tf:
            name = safe_name(m.name)
            if name == '.' and m.isdir():
                continue
            require(name not in seen, 'duplicate archive member')
            seen.add(name)
            mode = stat.S_IMODE(m.mode)
            if m.issym():
                rows.append([name, 'link', mode, m.linkname])
            elif m.isdir():
                rows.append([name, 'dir', mode])
            elif m.isfile():
                with tf.extractfile(m) as f:
                    sha = digest(f)
                rows.append([name, 'file', mode, m.size, sha])
            else:
                raise Refusal('unsupported archive member')
    return sorted(rows)


def encoded(rows):
    return (json.dumps(rows, ensure_ascii=True, separators=(',', ':')) + '\n').encode()


def sha_file(p):
    exact_path(str(p))
    require(p.is_file() and not getattr(p.stat(), 'st_flags', 0) & DATALESS,
            'receipt/archive missing or dataless')
    with p.open('rb') as f:
        return digest(f)


def check_acl_flags(p):
    require(not getattr(p.lstat(), 'st_flags', 0) & LOCK_FLAGS, 'immutable/append flag')
    result = subprocess.run(['/bin/ls', '-lde', str(p)], check=True,
                            text=True, capture_output=True)
    require(not re.search(r'^\s*\d+:', result.stdout, re.M), 'ACL present')


def check_uploaded(p):
    result = subprocess.run(['/usr/bin/fileproviderctl', 'evaluate', str(p)],
                            check=True, text=True, capture_output=True)
    require(bool(re.search(r'\bisUploaded\s*=\s*1\b', result.stdout)) and
            not re.search(r'\bisUploaded\s*=\s*0\b', result.stdout),
            'cloud upload unconfirmed')


def checksum_receipt(receipt, target):
    # One exact sha256sum/shasum line; never run shell text from the receipt.
    match = re.fullmatch(r'([0-9a-f]{64}) [ *](.+)\n?', receipt.read_text())
    require(match is not None and match[2] == str(target) and
            match[1] == sha_file(target), 'checksum receipt mismatch')
    return match[1]


def audit(journal, src, state, manifest_sha='', archive_sha=''):
    with journal.open('a', encoding='utf-8') as f:
        f.write('\t'.join((datetime.now(timezone.utc).isoformat(), str(src), state,
                           manifest_sha, archive_sha)) + '\n')
        f.flush()
        os.fsync(f.fileno())


def delete_root(item, keep, remote, journal):
    """Production policy constants cannot be overridden through CLI or env."""
    src = 'UNRESOLVED'
    started = False
    try:
        item, keep, remote = (exact_path(str(p)) for p in (item, keep, remote))
        exact_path(str(journal.parent))
        require(not journal.is_symlink(), 'journal symlink')
        raw = (item / 'source-path.txt').read_text()
        require(raw.endswith('\n') and raw.count('\n') == 1, 'source-path format')
        src = exact_path(raw[:-1])
        require(src.is_dir(), 'source not directory')
        require(not overlaps(src, item) and not overlaps(src, remote) and
                not overlaps(src, journal.parent), 'control/source overlap')
        check_keep(src, keep)
        approved = item.parent / 'approved-models.txt'
        model_dirs = approved.read_text().splitlines() if approved.exists() else []
        for line in model_dirs:
            exact_path(line)
        pilot = src.parent == ALIGN_ROOT and re.fullmatch(r'pilot-v[0-9]+-[A-Za-z0-9_-]+', src.name)
        require(pilot or str(src) in model_dirs, 'source outside allowed roots')
        require(not (src.parent == ALIGN_ROOT and src.name.startswith('pilot-v8-')),
                'pilot 9 retained until release')
        pointer = src.with_name(src.name + '.OFFLOADED.json')
        require(not os.path.lexists(pointer), 'pointer already exists')
        source = item / 'source.json'
        manifest_sha = checksum_receipt(item / 'source.sha256', source)
        archive_path = remote / (item.name + '.tar.zst')
        cloud_manifest = remote / (item.name + '.manifest.json')
        archive_sha = checksum_receipt(item / 'archive.sha256', archive_path)
        require(sha_file(cloud_manifest) == manifest_sha, 'cloud manifest mismatch')
        for name in ('cloud-local.json', 'source-after.json', 'cloud-roundtrip.json'):
            require(sha_file(item / name) == manifest_sha, 'verification manifest mismatch')
        for name in ('independent-receipt.txt', 'ed-approval.txt'):
            receipt = (item / name).read_text()
            require(str(src) in receipt and manifest_sha in receipt and archive_sha in receipt,
                    'receipt not bound to this source/manifest/archive')
        retention = json.loads((item / 'retention-review.json').read_text())
        require(retention == dict(source=str(src), manifest_sha256=manifest_sha,
                                 archive_sha256=archive_sha, no_retained_ledger_locators=True),
                'retention review absent or mismatched')
        rows = tree(src)
        require(encoded(rows) == source.read_bytes(), 'predelete source mismatch')
        require(not any('instrument_validation' in PurePosixPath(r[0]).parts for r in rows),
                'capture retention: keep root and request ruling')
        for p in (src.parent, item, journal.parent, src, *(src / r[0] for r in rows)):
            # Symlinks inside an archived tree are removed as links, not followed.
            if not p.is_symlink():
                check_acl_flags(p)
        require(os.access(src.parent, os.W_OK | os.X_OK), 'source parent not writable')
        for p in (src, *(src / r[0] for r in rows if r[1] == 'dir')):
            require(os.access(p, os.W_OK | os.X_OK), 'source directory not writable')
        before_identity = identity(src)
        # No operator gap after these fresh upload checks. Ambiguous/failed tool refuses.
        check_uploaded(archive_path)
        check_uploaded(cloud_manifest)
        check_keep(src, keep)
        require(identity(src) == before_identity and encoded(tree(src)) == source.read_bytes(),
                'source changed before delete')
        payload = dict(source=str(src), archive=str(archive_path), manifest=str(cloud_manifest),
                       manifest_sha256=manifest_sha, archive_sha256=archive_sha,
                       independent_receipt=str(item / 'independent-receipt.txt'))
        # Probe pointer publication before irreversible work, without replacing any file.
        staged = pointer.with_name(pointer.name + '.pending')
        with staged.open('x', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        audit(journal, src, 'DELETE_AUTHORIZED', manifest_sha, archive_sha)
        started = True
        shutil.rmtree(src)
        require(not os.path.lexists(src), 'source remains')
        os.link(staged, pointer)  # exclusive publication; never clobber a pointer
        staged.unlink()
        audit(journal, src, 'DELETED', manifest_sha, archive_sha)
    except Exception:
        audit(journal, src, 'FAILED_PARTIAL' if started else 'REFUSED_NO_DELETE')
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('archive')
    for name in ('tree', 'budget'):
        sub.add_parser(name).add_argument('path', type=Path)
    d = sub.add_parser('delete')
    for name in ('item', 'keep', 'remote', 'journal'):
        d.add_argument('--' + name, required=True, type=Path)
    args = p.parse_args()
    if args.command == 'delete':
        require(sys.platform == 'darwin', 'deletion requires macOS file flags/ACL tools')
        # Serialize this operation. Process quiescence is also mandatory externally.
        with (args.item.parent / '.delete.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            delete_root(args.item, args.keep, args.remote, args.journal)
    elif args.command == 'budget':
        rows = json.loads(args.path.read_text())
        total = sum(r[3] for r in rows if r[1] == 'file')
        # tar data padding + ample PAX/header allowance per entry, plus zstd bound
        # and manifest/control copies. No compression savings assumed.
        tar_bound = sum(((r[3] + 511) // 512) * 512 for r in rows if r[1] == 'file')
        tar_bound += sum(8192 + 4 * len(str(r).encode()) for r in rows) + 10240
        print(tar_bound + tar_bound // 100 + 1048576 + 4 * args.path.stat().st_size)
        print('source_regular_bytes=' + str(total), file=sys.stderr)
    else:
        rows = tree(args.path) if args.command == 'tree' else archive(sys.stdin.buffer)
        sys.stdout.buffer.write(encoded(rows))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('STOP: ' + type(exc).__name__ + ': ' + str(exc), file=sys.stderr)
        sys.exit(1)
