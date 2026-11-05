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
import runpy
import shutil
import stat
import subprocess
import sys
import tarfile
import unicodedata
from urllib.parse import quote
from urllib.request import Request, urlopen

MANDATORY_KEEP = tuple(Path(p) for p in (
    '/Users/edr/code/JouleWise', '/Users/edr/night-custody',
    '/Users/edr/night-b5', '/Users/edr/night-g2a', '/Users/edr/night-archive',
    '/Users/edr/night-plan-staging', '/Users/edr/night-b6', '/Users/edr/night-bytes',
    '/Users/edr/jw_models', '/Users/edr/.cache/huggingface/hub',
    '/Users/edr/Library/LaunchAgents',
))
ALIGN_ROOT = Path('/Users/edr/night-align')
MODEL_ROOTS = (Path('/Users/edr/jw_models'), Path('/Users/edr/.cache/huggingface/hub'))
STOP_PATH = Path('/Users/edr/night-custody/magistrate/STOP')
DATALESS = 0x40000000
LOCK_FLAGS = (0x2 | 0x4 | 0x20000 | 0x40000 |  # uchg/uappnd/schg/sappnd
              0x100000 | 0x80000 | 0x80)  # SF_NOUNLINK/SF_RESTRICTED/UF_DATAVAULT
# Deliberately unpinned. Step 5 must capture real macOS evaluate output; a
# reviewed code change must install its exact safe grammar/sample and digest.
# Synthetic tests do not supply operational upload authority.
UPLOAD_SUCCESS_SAMPLE = None
UPLOAD_SAMPLE_SHA256 = None


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


def check_keep(src, keep_file, mandatory=None, public_path=None):
    mandatory = MANDATORY_KEEP if mandatory is None else mandatory
    lines = keep_file.read_text().splitlines()
    require(bool(lines) and len(lines) == len(set(lines)), 'empty/duplicate KEEP')
    keeps = [exact_path(line) for line in lines]  # missing entries refuse
    # Every mandatory spelling must be present, and must exist on this host.
    require(all(str(p) in lines for p in mandatory), 'missing mandatory KEEP')
    for keep in keeps:
        if (public_path == src and keep in mandatory and keep in MODEL_ROOTS and
                src != keep and keep in src.parents):
            continue  # only this approved model's mandatory-root containment
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
    require(not getattr(p.lstat(), 'st_flags', 0) & LOCK_FLAGS, 'immutable/append/protected flag')
    result = subprocess.run(['/bin/ls', '-lde', str(p)], check=True,
                            text=True, capture_output=True)
    require(not re.search(r'^\s*\d+:', result.stdout, re.M), 'ACL present')


def parse_uploaded(text):
    require(UPLOAD_SUCCESS_SAMPLE is not None and UPLOAD_SAMPLE_SHA256 is not None,
            'cloud upload parser unpinned: record and review step-5 real sample')
    require(hashlib.sha256(UPLOAD_SUCCESS_SAMPLE.encode()).hexdigest() == UPLOAD_SAMPLE_SHA256,
            'cloud upload sample pin mismatch')
    # Scaffold only until the real sample is reviewed. No substring matching,
    # optional keys, uploadingError (even empty), duplicate or unknown fields.
    safe = 'isUploaded=1\nisUploading=0\nhasUnresolvedConflicts=0\n'
    require(UPLOAD_SUCCESS_SAMPLE == safe and text == UPLOAD_SUCCESS_SAMPLE,
            'cloud upload unknown format, pending, error or conflict')


def check_uploaded(p):
    result = subprocess.run(['/usr/bin/fileproviderctl', 'evaluate', str(p)],
                            check=True, text=True, capture_output=True)
    require(not result.stderr.strip(), 'cloud upload diagnostic unrecognized')
    parse_uploaded(result.stdout)


def busy_processes(table):
    """ps comm is executable identity, never arbitrary argv/path arguments."""
    pattern = re.compile(r'(?i)(?:claude|codex|offload\.py|align_pilot_session(?:\.py)?|harvest[\w.-]*|zstd|tar)')
    busy = []
    for row in table.splitlines():
        fields = row.strip().split(None, 1)
        require(len(fields) == 2 and fields[0].isdigit(), 'unknown process census format')
        pid, executable = fields
        if (pattern.fullmatch(PurePosixPath(executable).name) or
                re.fullmatch(r'.*/claude/versions/[\d.]+', executable)):
            busy.append(pid)
    return busy


def process_census():
    return busy_processes(subprocess.run(['/bin/ps', '-axo', 'pid=,comm='],
                          check=True, text=True, capture_output=True).stdout)


def check_pause_and_disk(op):
    stop = exact_path(str(STOP_PATH))
    ours = exact_path(str(op / 'our-STOP.txt'))
    expected = ('ALIGN paused for MBP offload and gold validation; ' + str(op) + '\n').encode()
    require(stop.read_bytes() == ours.read_bytes() == expected, 'pause STOP mismatch')
    s = os.statvfs(op)
    require(s.f_bavail * s.f_frsize >= 30_000_000_000, 'disk floor')
    require(not process_census(), 'writer/agent census busy')


def checksum_receipt(receipt, target):
    # One exact sha256sum/shasum line; never run shell text from the receipt.
    match = re.fullmatch(r'([0-9a-f]{64}) [ *](.+)\n?', receipt.read_text())
    require(match is not None and match[2] == str(target) and
            match[1] == sha_file(target), 'checksum receipt mismatch')
    return match[1]


def open_journal(journal, item):
    """Validate before even a refusal row. Never follow an audit alias."""
    parent = exact_path(str(journal.parent))
    require(parent == exact_path(str(item.parent)) and journal.name == 'deletions.tsv',
            'journal must be item.parent/deletions.tsv')
    if os.path.lexists(journal):
        s = journal.lstat()
        require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1,
                'journal must be regular, not symlink or hardlink')
    fd = os.open(journal, os.O_WRONLY | os.O_NOFOLLOW | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        validate_journal_fd(fd, journal)
        return fd
    except BaseException:
        os.close(fd)
        raise


def validate_journal_fd(fd, journal):
    s, named = os.fstat(fd), journal.lstat()
    require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1 and
            stat.S_ISREG(named.st_mode) and named.st_nlink == 1 and
            (s.st_dev, s.st_ino) == (named.st_dev, named.st_ino),
            'journal alias or replacement')


def audit(fd, journal, src, state, manifest_sha='', archive_sha=''):
    validate_journal_fd(fd, journal)
    row = '\t'.join((datetime.now(timezone.utc).isoformat(), str(src), state,
                     manifest_sha, archive_sha)) + '\n'
    require(os.write(fd, row.encode('utf-8')) == len(row.encode('utf-8')), 'short audit write')
    os.fsync(fd)



def replay_census(census):
    helper = runpy.run_path(str(Path(__file__).with_name('align_offload_model_keep.py')))
    require(census.get('schema') == 'joulewise.offload.model-census.v2', 'model census schema')
    refs = census['reviewed_refs']
    require(set(refs) == set(helper['ROLES']) and all(
        re.fullmatch('[0-9a-f]{40}', value) for value in refs.values()), 'model census full ref pins')
    repo = Path(__file__).resolve().parents[1]
    require(refs['bytes'] == helper['commit'](repo, 'c58282f87') and
            refs['b6'] == helper['commit'](repo, 'dda456f98'), 'model census lane pins')
    actual = helper['derive'](repo, refs, census['r0_config'])
    def normalized(value):
        value = json.loads(json.dumps(value))
        for row in value['inputs']:
            row.pop('ref', None)  # full commit SHA remains authoritative
        return value
    require(normalized(actual) == normalized(census), 'model census replay mismatch')


def unreferenced(src, repo_id, census):
    # Text only. Never stat paths extracted from registration/plan blobs.
    for text in census['paths']:
        p = PurePosixPath(text)
        candidate = PurePosixPath(str(src))
        require(not (p == candidate or p in candidate.parents or candidate in p.parents),
                'model referenced by census path')
    def alias(value):
        return value.casefold().replace('_', '-').replace('.', '-')
    candidates = {alias(src.name), alias(repo_id.split('/')[1])}
    for name in census['model_ids']:
        pin = alias(name)
        require(not any(c == pin or c.startswith(pin + '-') or pin.startswith(c + '-')
                        for c in candidates), 'model referenced by census identity')


def public_evidence(item, src, manifest_sha):
    require(any(root in src.parents for root in MODEL_ROOTS) and src not in MODEL_ROOTS,
            'public weights must be a strict model-root descendant')
    claim = json.loads((item / 'public-weights.json').read_text())
    require(set(claim) == {'source', 'repo_id', 'revision', 'manifest_sha256', 'census_sha256', 'files'},
            'public weights claim fields')
    require(claim['source'] == str(src) and claim['manifest_sha256'] == manifest_sha,
            'public weights exact source/manifest mismatch')
    require(isinstance(claim['repo_id'], str) and re.fullmatch(
        r'[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*', claim['repo_id']) and
        re.fullmatch(r'[0-9a-f]{40}', claim['revision']), 'exact HF repo/revision required')
    require(sha_file(item / 'model-census.json') == claim['census_sha256'], 'model census digest')
    census = json.loads((item / 'model-census.json').read_text())
    replay_census(census)
    unreferenced(src, claim['repo_id'], census)
    approval = json.loads((item / 'ed-approval.json').read_text())
    require(approval == {'approver': 'Ed', 'approved': [claim]},
            'Ed specific public-model list approval missing/mismatched')
    receipt = (item / 'independent-receipt.txt').read_text()
    require(all(value in receipt for value in (str(src), manifest_sha, claim['repo_id'],
                                               claim['revision'], claim['census_sha256'])),
            'independent public-model receipt not bound')
    retention = json.loads((item / 'retention-review.json').read_text())
    require(retention == dict(source=str(src), manifest_sha256=manifest_sha,
                             model_class='public-weights', no_retained_ledger_locators=True,
                             no_measurement_data=True), 'public-model retention review')
    return claim


def check_hf_downloadable(claim, rows):
    files = {r[0] for r in rows if r[1] == 'file'}
    require(isinstance(claim['files'], dict) and set(claim['files']) == files and
            len(set(claim['files'].values())) == len(files), 'HF file/blob mapping incomplete')
    require(files and not any(r[1] == 'link' for r in rows), 'public model must contain blobs, not symlinks')
    base = 'https://huggingface.co/'
    repo, rev = claim['repo_id'], claim['revision']
    urls = [base + 'api/models/' + quote(repo, safe='/') + '/revision/' + rev]
    for remote in claim['files'].values():
        require(isinstance(remote, str) and safe_name(remote) == remote and remote != '.',
                'unsafe HF filename')
        urls.append(base + quote(repo, safe='/') + '/resolve/' + rev + '/' + quote(remote, safe='/'))
    # Operator-time network only, without credentials; gated/private/missing
    # revisions or any unavailable file fail. Never called by offline authoring.
    for url in urls:
        with urlopen(Request(url, method='HEAD'), timeout=15) as response:
            require(response.status == 200, 'public HF revision/file unavailable')
    return dict(checked_utc=datetime.now(timezone.utc).isoformat(), method='HEAD',
                revision_url=urls[0], files_checked=len(files))


def delete_root(item, keep, remote, journal, model_class='archived'):
    """Production policy constants cannot be overridden through CLI or env."""
    src = 'UNRESOLVED'
    started = False
    # Outside the audit-on-refusal block: invalid journals must receive no write.
    journal_fd = open_journal(journal, item)
    try:
        require(model_class in ('archived', 'public-weights'), 'unknown model class')
        public = model_class == 'public-weights'
        item, keep = (exact_path(str(p)) for p in (item, keep))
        if not public:
            remote = exact_path(str(remote))
        names = (('source-path.txt', 'source.json', 'source.sha256', 'source-after.json',
                  'independent-receipt.txt', 'retention-review.json', 'public-weights.json',
                  'model-census.json', 'ed-approval.json') if public else ('source-path.txt', 'source.json', 'source.sha256', 'archive.sha256',
                     'source-after.json', 'cloud-local.json', 'cloud-roundtrip.json',
                     'independent-receipt.txt', 'ed-approval.txt', 'retention-review.json'))
        for name in names:
            control = exact_path(str(item / name))
            require(control.is_file() and not getattr(control.stat(), 'st_flags', 0) & DATALESS,
                    'control receipt missing or dataless')
        raw = (item / 'source-path.txt').read_text()
        require(raw.endswith('\n') and raw.count('\n') == 1, 'source-path format')
        src = exact_path(raw[:-1])
        require(src.is_dir(), 'source not directory')
        require(not overlaps(src, item) and (public or not overlaps(src, remote)) and
                not overlaps(src, journal.parent), 'control/source overlap')
        source = item / 'source.json'
        manifest_sha = checksum_receipt(item / 'source.sha256', source)
        pointer = src.with_name(src.name + '.OFFLOADED.json')
        require(not os.path.lexists(pointer), 'pointer already exists')
        archive_sha = ''
        if public:
            claim = public_evidence(item, src, manifest_sha)
            check_keep(src, keep, public_path=src)
            require(sha_file(item / 'source-after.json') == manifest_sha, 'verification manifest mismatch')
        else:
            check_keep(src, keep)
            approved = item.parent / 'approved-models.txt'
            model_dirs = approved.read_text().splitlines() if approved.exists() else []
            for line in model_dirs:
                exact_path(line)
            pilot = src.parent == ALIGN_ROOT and re.fullmatch(r'pilot-v[0-9]+-[A-Za-z0-9_-]+', src.name)
            require(not pilot, 'pilot roots retained until block-5 release')
            require(pilot or str(src) in model_dirs, 'source outside allowed roots')
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
        if public:
            require(not any(r[1] == 'link' for r in rows), 'public model requires blobs, not symlinks')
            require(not any({'runs', 'runs-parent', 'measurement', 'captures'} &
                            set(PurePosixPath(r[0]).parts) for r in rows),
                    'capture-bearing tree is not public model weights')
        for p in (src.parent, item, journal.parent, src, *(src / r[0] for r in rows)):
            # ls -d and lstat check links themselves, never their targets.
            check_acl_flags(p)
        require(os.access(src.parent, os.W_OK | os.X_OK), 'source parent not writable')
        for p in (src, *(src / r[0] for r in rows if r[1] == 'dir')):
            require(os.access(p, os.W_OK | os.X_OK), 'source directory not writable')
        check_pause_and_disk(item.parent)
        before_identity = identity(src)
        # No operator gap after these fresh upload checks. Ambiguous/failed tool refuses.
        if public:
            require(public_evidence(item, src, manifest_sha) == claim, 'public-model evidence changed')
            head_receipt = check_hf_downloadable(claim, rows)
            check_keep(src, keep, public_path=src)
            payload = dict(model_class=model_class, **claim, hf_head=head_receipt)
        else:
            check_uploaded(archive_path)
            check_uploaded(cloud_manifest)
            check_keep(src, keep)
            payload = dict(source=str(src), archive=str(archive_path), manifest=str(cloud_manifest),
                           manifest_sha256=manifest_sha, archive_sha256=archive_sha,
                           independent_receipt=str(item / 'independent-receipt.txt'))
        require(identity(src) == before_identity and encoded(tree(src)) == source.read_bytes(),
                'source changed before delete')
        regular_bytes = sum(r[3] for r in rows if r[1] == 'file')
        payload['source_regular_bytes'] = regular_bytes
        free_before = shutil.disk_usage(src.parent).free
        # Probe pointer publication before irreversible work, without replacing any file.
        staged = pointer.with_name(pointer.name + '.pending')
        with staged.open('x', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        audit(journal_fd, journal, src, 'DELETE_AUTHORIZED', manifest_sha, archive_sha)
        started = True
        shutil.rmtree(src)
        require(not os.path.lexists(src), 'source remains')
        os.link(staged, pointer)  # exclusive publication; never clobber a pointer
        staged.unlink()
        audit(journal_fd, journal, src, 'DELETED', manifest_sha, archive_sha)
        return dict(source=str(src), model_class=model_class, source_regular_bytes=regular_bytes,
                    available_bytes_delta=shutil.disk_usage(src.parent).free - free_before)
    except Exception:
        try:
            audit(journal_fd, journal, src, 'FAILED_PARTIAL' if started else 'REFUSED_NO_DELETE')
        except (OSError, Refusal):
            pass  # preserve the original failure; never fall back to another path
        raise
    finally:
        os.close(journal_fd)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('archive')
    sub.add_parser('census')
    sub.add_parser('uploaded').add_argument('path', type=Path)
    for name in ('tree', 'budget'):
        sub.add_parser(name).add_argument('path', type=Path)
    d = sub.add_parser('delete')
    for name in ('item', 'keep', 'journal'):
        d.add_argument('--' + name, required=True, type=Path)
    d.add_argument('--remote', type=Path, help='required for archived class')
    d.add_argument('--model-class', choices=('archived', 'public-weights'), default='archived')
    args = p.parse_args()
    if args.command == 'delete':
        require(sys.platform == 'darwin', 'deletion requires macOS file flags/ACL tools')
        # Serialize this operation. Process quiescence is also mandatory externally.
        lock_path = exact_path(str(args.item.parent)) / '.delete.lock'
        require(not lock_path.is_symlink(), 'delete lock symlink')
        with lock_path.open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            require(args.model_class == 'public-weights' or args.remote is not None, '--remote required')
            result = delete_root(args.item, args.keep, args.remote, args.journal, args.model_class)
            print(json.dumps(result, sort_keys=True))
    elif args.command == 'census':
        busy = process_census()
        require(not busy, 'writer/agent census busy; PIDs=' + ','.join(busy))
    elif args.command == 'uploaded':
        check_uploaded(args.path)
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
