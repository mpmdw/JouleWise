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
import plistlib
from pathlib import Path, PurePosixPath
import re
import runpy
import shutil
import signal
import stat
import subprocess
import sys
import tarfile
import time
import unicodedata
from urllib.parse import quote
from urllib.request import Request, urlopen

MANDATORY_KEEP = tuple(Path(p) for p in (
    '/Users/edr/code/JouleWise', '/Users/edr/night-custody',
    '/Users/edr/night-b5', '/Users/edr/night-g2a', '/Users/edr/night-archive',
    '/Users/edr/night-plan-staging', '/Users/edr/night-b6', '/Users/edr/night-bytes',
    '/Users/edr/jw_models', '/Users/edr/.cache/huggingface/hub',
    '/Users/edr/Library/LaunchAgents', '/Users/edr/night-align',
))
ALIGN_ROOT = Path('/Users/edr/night-align')
HOME = Path('/Users/edr')
# Every existing home-level measurement root must be in KEEP by inode, even one
# this list has never heard of (N3). Case-insensitive, like APFS.
MEASUREMENT_ROOT = re.compile(r'(?i)(?:night-.+|jw-b5-.+|jw_models)')
MODEL_ROOTS = (Path('/Users/edr/jw_models'), Path('/Users/edr/.cache/huggingface/hub'))
STOP_PATH = Path('/Users/edr/night-custody/magistrate/STOP')
VOLUME_ROOT = Path('/Volumes')
# diskutil BusProtocol of real external media. 'Disk Image', 'Apple Fabric',
# 'Virtual Interface' and unknown values refuse (N7).
PHYSICAL_BUSES = frozenset({'USB', 'PCI-Express', 'PCI', 'Thunderbolt'})
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
    sha_file(keep_file)  # reject missing, aliased or dataless control data before read
    lines = keep_file.read_text().splitlines()
    require(bool(lines) and len(lines) == len(set(lines)), 'empty/duplicate KEEP')
    keeps = [exact_path(line) for line in lines]  # missing entries refuse
    # Every mandatory spelling must be present, and must exist on this host.
    require(all(str(p) in lines for p in mandatory), 'missing mandatory KEEP')
    keep_ids = {identity(k) for k in keeps}
    for p in (*mandatory, *measurement_roots()):
        try:
            present = identity(p) in keep_ids
        except OSError:
            present = False
        require(present, 'missing mandatory KEEP (inode): ' + p.name)
    for keep in keeps:
        if (public_path == src and keep in mandatory and keep in MODEL_ROOTS and
                src != keep and keep in src.parents):
            continue  # only this approved model's mandatory-root containment
        require(not overlaps(src, keep), 'KEEP inode overlap')


def measurement_roots(home=None):
    home = HOME if home is None else home
    try:
        children = sorted(home.iterdir())
    except FileNotFoundError:
        return []  # no such home on this host
    return [p for p in children if MEASUREMENT_ROOT.fullmatch(p.name) and p.is_dir()]


def under_align_root(src):
    """Inode test: a case/Unicode spelling variant of night-align still matches."""
    try:
        align = identity(ALIGN_ROOT)
    except FileNotFoundError:
        return src.parent == ALIGN_ROOT
    return src.parent == ALIGN_ROOT or any(identity(p) == align for p in src.parents)


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


AGENT_NAMES = frozenset({'claude', 'claude-code', 'codex'})
SCRIPT_STEMS = frozenset({'offload', 'align_pilot_session', 'magistrate_watchdog',
                          'advance_b5_ledger_pin', 'align_r0_checks', 'run_night',
                          'run_b5_analysis', 'align_offload_disk_guard', 'mlx_lm'})
WRITER_NAMES = frozenset({'tar', 'gtar', 'bsdtar', 'zstd', 'pzstd', 'unzstd', 'zstdmt',
                          'zstdcat', 'rsync', 'cp', 'ditto', 'dd'})
SCRIPT_SUFFIXES = ('.py', '.sh', '.zsh', '.js', '.mjs', '.cjs')


def _stem(name):
    name = name.casefold()
    for suffix in SCRIPT_SUFFIXES:
        if name.endswith(suffix):
            return name[:-len(suffix)]
    return name


def _named(token):
    """Executable/script basename, or any agent path component (versions dir)."""
    parts = [p for p in token.split('/') if p]
    if not parts:
        return False
    base = _stem(parts[-1])
    return (base in AGENT_NAMES or base in SCRIPT_STEMS or base in WRITER_NAMES or
            base.startswith('harvest') or
            any(p.casefold() in AGENT_NAMES for p in parts[:-1]))


def _module(token):
    parts = [p.casefold() for p in token.split('.')]
    return any(p in SCRIPT_STEMS or p.startswith('harvest') for p in parts)


def _table(text):
    if isinstance(text, bytes):
        text = text.decode('utf-8', 'replace')
    require(bool(text.strip()), 'empty process census')
    rows = {}
    for row in text.splitlines():
        if not row.strip():
            continue
        m = re.fullmatch(r'\s*(\d+)(?:\s+(.*))?', row)
        require(m is not None, 'unknown process census format')
        rows[m[1]] = (m[2] or '').strip()
    return rows


def busy_processes(comm_table, args_table, executables=None):
    """Inspect executable paths and argv locally; return PIDs only.

    Three independent views, each untruncated (review N1):
    - comm_table: `ps -axww -o pid=,comm=` with comm LAST (macOS truncates a
      non-last comm to 16 characters). On macOS this is the launch name/path.
    - args_table: `ps -axww -o pid=,args=` with args LAST, unlimited width:
      interpreter-launched scripts, `python -m` modules, argv[0] spellings.
    - executables: pid -> kernel proc_pidpath(), the real executable image,
      e.g. .../claude/versions/X even when launched via a `claude` symlink or
      with a disguised argv[0].
    Never print or journal any of them: argv may contain secrets.
    Ambiguous matching is conservatively busy.
    """
    comm, args = _table(comm_table), _table(args_table)
    executables = executables or {}
    busy = set()
    for pid in set(comm) | set(args):
        if _named(comm.get(pid, '')) or _named(executables.get(pid, '')):
            busy.add(pid)
            continue
        tokens = args.get(pid, '').split()
        if any(_named(t) for t in tokens) or any(
                tokens[i] == '-m' and _module(tokens[i + 1]) for i in range(len(tokens) - 1)):
            busy.add(pid)
    return sorted(busy, key=int)


def ps_table(field):
    return subprocess.run(['/bin/ps', '-axww', '-o', 'pid=,' + field + '='],
                          check=True, capture_output=True).stdout


def executable_paths(pids):
    """Kernel executable path per PID via libproc proc_pidpath (no argv)."""
    import ctypes
    lib = ctypes.CDLL('/usr/lib/libproc.dylib')
    lib.proc_pidpath.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32)
    buf = ctypes.create_string_buffer(4096)  # PROC_PIDPATHINFO_MAXSIZE
    paths = {}
    for pid in pids:
        if lib.proc_pidpath(int(pid), buf, len(buf)) > 0:
            paths[pid] = buf.value.decode('utf-8', 'replace')
    return paths


def process_census():
    comm, args = ps_table('comm'), ps_table('args')
    pids = set(_table(comm)) | set(_table(args))
    return busy_processes(comm, args, executable_paths(pids) if sys.platform == 'darwin' else {})


def external_info(mount):
    result = subprocess.run(['/usr/sbin/diskutil', 'info', '-plist', str(mount)],
                            check=True, capture_output=True, timeout=30)
    return plistlib.loads(result.stdout)


def volume_device(path):
    return path.stat().st_dev


def physical_external(info):
    """Volume, its APFS physical store and that store's whole disk must all be
    real external USB/Thunderbolt/PCIe(NVMe) media. A disk image on the internal
    SSD reports Internal=false but BusProtocol 'Disk Image' (N7): refused."""
    def physical(d):
        return (isinstance(d, dict) and d.get('Internal') is False and
                d.get('BusProtocol') in PHYSICAL_BUSES and
                d.get('VirtualOrPhysical') != 'Virtual' and d.get('MediaName') != 'Disk Image')
    reason = 'independent copy not on physical external USB/Thunderbolt/NVMe media'
    require(physical(info), reason)
    stores = info.get('APFSPhysicalStores')
    require(isinstance(stores, list) and len(stores) > 0, reason)
    wholes = []
    for row in stores:
        device = row.get('APFSPhysicalStore') if isinstance(row, dict) else None
        require(isinstance(device, str) and re.fullmatch(r'disk\d+(?:s\d+)*', device), reason)
        store = external_info(device)
        parent = store.get('ParentWholeDisk') if isinstance(store, dict) else None
        require(isinstance(parent, str) and re.fullmatch(r'disk\d+', parent), reason)
        whole = external_info(parent)
        require(physical(store) and physical(whole), reason)
        wholes.append(whole)
    return wholes


def external_volume_identity(mount, uuid, media=None):
    """Enrolled VolumeUUID AND physical external media (optionally its name)."""
    require(mount.parent == VOLUME_ROOT and os.path.ismount(mount),
            'independent volume not mounted')
    info = external_info(mount)
    require(isinstance(uuid, str) and bool(uuid) and info.get('VolumeUUID') == uuid and
            info.get('Internal') is False and info.get('MountPoint') == str(mount) and
            info.get('FilesystemType', '').casefold() == 'apfs',
            'independent volume identity mismatch')
    wholes = physical_external(info)
    if media is not None:
        require(bool(media) and all(w.get('MediaName') == media for w in wholes),
                'independent volume physical media mismatch')
    return info


def independent_copy(item, src, manifest_sha, archive_sha=None):
    """Re-read the mounted SSD, archive, manifest AND restored tree, not a claim.

    The exact UUID is enrolled by Ed; a same-name replacement or a bare mount
    point on the internal disk refuses. All paths must stay on that volume.
    """
    receipt = json.loads((item / 'independent-copy.json').read_text())
    require(set(receipt) == {'schema', 'source', 'manifest_sha256', 'archive_sha256',
                            'volume', 'volume_uuid', 'archive', 'manifest', 'restore', 'verified_utc'},
            'independent copy receipt fields')
    require(receipt['schema'] == 'joulewise.offload.independent-copy.v1' and
            receipt['source'] == str(src) and receipt['manifest_sha256'] == manifest_sha and
            re.fullmatch('[0-9a-f]{64}', receipt['archive_sha256']) and
            (archive_sha is None or receipt['archive_sha256'] == archive_sha),
            'independent copy binding mismatch')
    mount = exact_path(receipt['volume'])
    external_volume_identity(mount, receipt['volume_uuid'])
    device = volume_device(mount)
    require(device not in (volume_device(src), volume_device(item)),
            'second copy shares source/journal device')
    paths = [exact_path(receipt[key]) for key in ('archive', 'manifest', 'restore')]
    require(all(mount in p.parents and volume_device(p) == device for p in paths),
            'independent copy outside enrolled device')
    archive_path, manifest, restore = paths
    require(sha_file(archive_path) == receipt['archive_sha256'] and
            sha_file(manifest) == manifest_sha and
            hashlib.sha256(encoded(tree(restore))).hexdigest() == manifest_sha,
            'independent copy bytes mismatch')
    return receipt


def enroll_second(item, volume, uuid, archive_path, manifest, restore):
    """Publish one immutable SSD receipt only after full member/restore checks."""
    item = exact_path(str(item))
    volume, archive_path, manifest, restore = (
        exact_path(str(p)) for p in (volume, archive_path, manifest, restore))
    src = exact_path((item / 'source-path.txt').read_text().rstrip('\n'))
    manifest_sha = checksum_receipt(item / 'source.sha256', item / 'source.json')
    require(sha_file(manifest) == manifest_sha and encoded(tree(restore)) == (item / 'source.json').read_bytes(),
            'second-copy manifest/restore mismatch')
    archive_sha = sha_file(archive_path)  # refuse dataless before decompression
    with subprocess.Popen(['zstd', '-dc', str(archive_path)], stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL) as child:
        rows = archive(child.stdout)
        require(child.wait() == 0, 'second-copy decompression failed')
    require(encoded(rows) == (item / 'source.json').read_bytes(), 'second-copy member mismatch')
    receipt = dict(schema='joulewise.offload.independent-copy.v1', source=str(src),
                   manifest_sha256=manifest_sha, archive_sha256=archive_sha,
                   volume=str(volume), volume_uuid=uuid, archive=str(archive_path),
                   manifest=str(manifest), restore=str(restore),
                   verified_utc=datetime.now(timezone.utc).isoformat())
    with (item / 'independent-copy.json').open('x') as f:
        json.dump(receipt, f, sort_keys=True)
    # A failed device check leaves a receipt but never authorizes deletion.
    independent_copy(item, src, manifest_sha, receipt['archive_sha256'])


def wait_dataless(path, expected):
    for _ in range(240):
        if bool(path.lstat().st_flags & DATALESS) == expected:
            return
        time.sleep(5)
    raise Refusal('cloud dataless transition not observed')


def cloud_roundtrip(item, remote):
    """Guarded Ed-only writer: record actual eviction/hydration and full hashes."""
    item, remote = exact_path(str(item)), exact_path(str(remote))
    source = item / 'source.json'
    manifest_sha = checksum_receipt(item / 'source.sha256', source)
    archive_path, manifest = remote / (item.name + '.tar.zst'), remote / (item.name + '.manifest.json')
    archive_sha = checksum_receipt(item / 'archive.sha256', archive_path)
    for name in ('cloud-proof.json', 'cloud-roundtrip.json'):
        require(not os.path.lexists(item / name), 'roundtrip output already exists')
    for path in (archive_path, manifest):
        exact_path(str(path))
        check_uploaded(path)
        subprocess.run(['/usr/bin/brctl', 'evict', str(path)], check=True, capture_output=True)
        wait_dataless(path, True)
        subprocess.run(['/usr/bin/brctl', 'download', str(path)], check=True, capture_output=True)
        wait_dataless(path, False)
    require(sha_file(manifest) == manifest_sha and sha_file(archive_path) == archive_sha,
            'cloud roundtrip digest mismatch')
    with subprocess.Popen(['zstd', '-dc', str(archive_path)], stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL) as child:
        rows = archive(child.stdout)
        require(child.wait() == 0, 'cloud decompression failed')
    require(encoded(rows) == source.read_bytes(), 'cloud member mismatch')
    with (item / 'cloud-roundtrip.json').open('xb') as f:
        f.write(encoded(rows))
    proof = dict(schema='joulewise.offload.cloud-roundtrip.v1', source_manifest_sha256=manifest_sha,
                 archive_sha256=archive_sha, archive=str(archive_path), manifest=str(manifest),
                 evicted_dataless=True, hydrated_not_dataless=True)
    with (item / 'cloud-proof.json').open('x') as f:
        json.dump(proof, f, sort_keys=True)


def check_pause_and_disk(op):
    stop = exact_path(str(STOP_PATH))
    ours = exact_path(str(op / 'our-STOP.txt'))
    expected = ('ALIGN paused for MBP offload and gold validation; ' + str(op) + '\n').encode()
    require(stop.read_bytes() == ours.read_bytes() == expected, 'pause STOP mismatch')
    lock = STOP_PATH.with_name('magistrate.lock')
    if os.path.lexists(lock):
        state = json.loads(exact_path(str(lock)).read_text())
        require(state.get('schema') == 'joulewise.magistrate_lock.v1' and
                type(state.get('pid')) is int and state['pid'] > 1, 'unknown magistrate lock')
        try:
            os.kill(state['pid'], 0)
        except ProcessLookupError:
            pass
        else:
            raise Refusal('magistrate lock owner alive')
    for argv in (['/bin/launchctl', 'list'], ['sudo', '-n', '/bin/launchctl', 'list']):
        loaded = subprocess.run(argv, check=True, text=True, capture_output=True).stdout
        require('com.joulewise.' not in loaded, 'JouleWise launcher loaded')
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
        require(model_class == 'archived',
                'all deletions require SSD plus server-confirmed iCloud; public-only deletion retired')
        item, keep, remote = (exact_path(str(p)) for p in (item, keep, remote))
        names = ('source-path.txt', 'source.json', 'source.sha256', 'archive.sha256',
                 'source-after.json', 'cloud-local.json', 'cloud-roundtrip.json',
                 'cloud-proof.json', 'independent-copy.json', 'independent-receipt.txt',
                 'ed-approval.txt', 'retention-review.json')
        for name in names:
            control = exact_path(str(item / name))
            require(control.is_file() and not getattr(control.stat(), 'st_flags', 0) & DATALESS,
                    'control receipt missing or dataless')
        raw = (item / 'source-path.txt').read_text()
        require(raw.endswith('\n') and raw.count('\n') == 1, 'source-path format')
        src = exact_path(raw[:-1])
        require(src.is_dir(), 'source not directory')
        require(not overlaps(src, item) and not overlaps(src, remote) and
                not overlaps(src, journal.parent), 'control/source overlap')
        source = item / 'source.json'
        manifest_sha = checksum_receipt(item / 'source.sha256', source)
        pointer = src.with_name(src.name + '.OFFLOADED.json')
        require(not os.path.lexists(pointer), 'pointer already exists')
        archive_sha = ''
        # Inode-keyed, before KEEP: nothing under night-align (any spelling) is
        # deletable; night-align is also mandatory KEEP (N3, defense in depth).
        require(not under_align_root(src), 'pilot roots retained until block-5 release')
        check_keep(src, keep)
        approved = item.parent / 'approved-models.txt'
        if os.path.lexists(approved):
            sha_file(approved)
            model_dirs = approved.read_text().splitlines()
        else:
            model_dirs = []
        for line in model_dirs:
            exact_path(line)
        require(str(src) in model_dirs, 'source outside allowed roots')
        archive_path = remote / (item.name + '.tar.zst')
        cloud_manifest = remote / (item.name + '.manifest.json')
        archive_sha = checksum_receipt(item / 'archive.sha256', archive_path)
        require(sha_file(cloud_manifest) == manifest_sha, 'cloud manifest mismatch')
        for name in ('cloud-local.json', 'source-after.json', 'cloud-roundtrip.json'):
            require(sha_file(item / name) == manifest_sha, 'verification manifest mismatch')
        proof = json.loads((item / 'cloud-proof.json').read_text())
        require(proof == dict(schema='joulewise.offload.cloud-roundtrip.v1',
                              source_manifest_sha256=manifest_sha, archive_sha256=archive_sha,
                              archive=str(archive_path), manifest=str(cloud_manifest),
                              evicted_dataless=True, hydrated_not_dataless=True),
                'cloud roundtrip proof mismatch')
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
        require(not any('instrument_validation' in {p.casefold() for p in PurePosixPath(r[0]).parts}
                        for r in rows),
                'capture retention: keep root and request ruling')
        for p in (src.parent, item, journal.parent, src, *(src / r[0] for r in rows)):
            # ls -d and lstat check links themselves, never their targets.
            check_acl_flags(p)
        require(os.access(src.parent, os.W_OK | os.X_OK), 'source parent not writable')
        for p in (src, *(src / r[0] for r in rows if r[1] == 'dir')):
            require(os.access(p, os.W_OK | os.X_OK), 'source directory not writable')
        check_pause_and_disk(item.parent)
        before_identity = identity(src)
        # Re-read the second failure domain before the final source/server checks.
        independent_copy(item, src, manifest_sha, archive_sha)
        require(volume_device(archive_path) == volume_device(src),
                'cloud staging must be on internal source device')
        check_keep(src, keep)
        payload = dict(source=str(src), archive=str(archive_path), manifest=str(cloud_manifest),
                       manifest_sha256=manifest_sha, archive_sha256=archive_sha,
                       independent_receipt=str(item / 'independent-receipt.txt'))
        require(identity(src) == before_identity and encoded(tree(src)) == source.read_bytes(),
                'source changed before delete')
        check_pause_and_disk(item.parent)
        check_uploaded(archive_path)
        check_uploaded(cloud_manifest)
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
    except BaseException:  # Ctrl-C/SIGTERM during rmtree still gets its row (N8)
        try:
            audit(journal_fd, journal, src, 'FAILED_PARTIAL' if started else 'REFUSED_NO_DELETE')
        except (OSError, Refusal):
            pass  # preserve the original failure; never fall back to another path
        raise
    finally:
        os.close(journal_fd)


def interrupted(signum, frame):
    raise KeyboardInterrupt('signal ' + str(signum))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('archive')
    sub.add_parser('census')
    sub.add_parser('uploaded').add_argument('path', type=Path)
    rt = sub.add_parser('cloud-roundtrip')
    rt.add_argument('--item', required=True, type=Path)
    rt.add_argument('--remote', required=True, type=Path)
    second = sub.add_parser('second-copy')
    for name in ('item', 'volume', 'archive', 'manifest', 'restore'):
        second.add_argument('--' + name, required=True, type=Path)
    second.add_argument('--uuid', required=True)
    check = sub.add_parser('volume-check')
    check.add_argument('--volume', required=True, type=Path)
    check.add_argument('--uuid', required=True)
    check.add_argument('--media', required=True, help='whole-disk MediaName enrolled at 9a')
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
            for signum in (signal.SIGTERM, signal.SIGHUP):
                signal.signal(signum, interrupted)  # journaled like Ctrl-C (N8)
            require(args.model_class == 'public-weights' or args.remote is not None, '--remote required')
            result = delete_root(args.item, args.keep, args.remote, args.journal, args.model_class)
            print(json.dumps(result, sort_keys=True))
    elif args.command == 'volume-check':
        info = external_volume_identity(exact_path(str(args.volume)), args.uuid, args.media)
        print(json.dumps(dict(volume=str(args.volume), volume_uuid=info.get('VolumeUUID'),
                              bus=info.get('BusProtocol'), media=args.media,
                              result='external volume identity PASS'), sort_keys=True))
    elif args.command == 'cloud-roundtrip':
        cloud_roundtrip(args.item, args.remote)
    elif args.command == 'second-copy':
        enroll_second(args.item, args.volume, args.uuid, args.archive, args.manifest, args.restore)
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
    except KeyboardInterrupt as exc:
        print('STOP: interrupted: ' + str(exc), file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print('STOP: ' + type(exc).__name__ + ': ' + str(exc), file=sys.stderr)
        sys.exit(1)
