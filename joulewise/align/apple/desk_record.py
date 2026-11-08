"""Laptop replay of an explicitly exported, hash-bound terminal v4 record.

The descriptor is read from a pinned Git commit. Evidence is supplied locally;
this module never fetches, launches hardware, restores archives, or harvests.
Absolute locators in the original session/plan are replaced, never followed.
"""
from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile

SCHEMA = 'joulewise.align_v4.desk_record.v1'
ROOT_FIELDS = ('session', 'measurement_root', 'registration_dir', 'runs_root', 'custody_root', 'plan')


def relative_path(value):
    if (not isinstance(value, str) or not value or '\\' in value or '\n' in value
            or PurePosixPath(value).is_absolute()
            or any(p in ('', '.', '..', 'restricted') for p in value.split('/'))):
        raise ValueError(f'desk record requires a relative contained path: {value!r}')
    return value


def committed_descriptor(repository, commit, record):
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('desk record requires a full 40-character commit SHA')
    relative_path(record)
    result = subprocess.run(['git', '-C', str(repository), 'show', f'{commit}:{record}'],
                            check=True, capture_output=True, env=dict(os.environ, GIT_NO_LAZY_FETCH='1'))
    value = json.loads(result.stdout)
    if not isinstance(value, dict) or value.get('schema') != SCHEMA:
        raise ValueError('unsupported desk record schema')
    for key in ROOT_FIELDS:
        relative_path(value[key])
    files = value.get('files')
    if not isinstance(files, dict) or not files:
        raise ValueError('desk record requires a complete file/digest inventory')
    for path, digest in files.items():
        relative_path(path)
        if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise ValueError(f'desk record invalid SHA-256: {path}')
    targets = value.get('targets', {})
    if not isinstance(targets, dict) or any(
        not isinstance(paths, list) or any(not isinstance(path, list) or not path
            or any(not isinstance(key, str) for key in path) for path in paths)
        for paths in targets.values()):
        raise ValueError('desk record invalid target-precheck paths')
    return value


def _files(root):
    if root.is_symlink():
        raise ValueError('desk record root must not be a symlink')
    for directory, dirs, names in os.walk(root, followlinks=False):
        dirs.sort()
        for name in dirs:
            if name == 'restricted' or (Path(directory)/name).is_symlink():
                raise ValueError('desk record contains a restricted directory or symlink')
        for name in sorted(names):
            path = Path(directory)/name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink() or not path.is_file():
                raise ValueError(f'desk record nonregular file: {relative}')
            yield relative, path


def describe(inputs, layout):
    """Author a descriptor for an explicitly exported, terminal local tree.

    The caller exports evidence; this helper does not discover source-Mac
    directories or copy anything from locators in session/plan/config text.
    """
    root = Path(inputs)
    roots = {key: relative_path(layout[key]) for key in ROOT_FIELDS}
    files = {}
    for relative, path in _files(root):
        digest = hashlib.sha256()
        with path.open('rb') as handle:
            for chunk in iter(lambda: handle.read(1024*1024), b''):
                digest.update(chunk)
        files[relative] = digest.hexdigest()
    if not (root/roots['custody_root']/'night/result.json').is_file():
        raise ValueError('terminal record is required before desk export')
    return {'schema': SCHEMA, **roots, 'files': files,
            **({'targets': layout['targets']} if 'targets' in layout else {})}


def authenticate(root, files):
    """No-follow inventory: every consumer-visible file must be committed."""
    observed, total = set(), 0
    for relative, path in _files(root):
        if relative not in files:
            raise ValueError(f'desk record unlisted file: {relative}')
        digest = hashlib.sha256()
        with path.open('rb') as handle:
            for chunk in iter(lambda: handle.read(1024*1024), b''):
                total += len(chunk)
                digest.update(chunk)
        if digest.hexdigest() != files[relative]:
            raise ValueError(f'desk record digest mismatch: {relative}')
        observed.add(relative)
    if observed != set(files):
        raise ValueError('desk record missing files: '+', '.join(sorted(set(files)-observed)))
    return total


def replay(repository, commit, record, inputs, output, *, workers=1, profile=None):
    """Replay the full desk consumer chain; terminal harvest remains upstream."""
    from joulewise.align.apple.desk_execution import DeskExecution
    from scripts import align_v4_session as v4
    root, output = Path(inputs).absolute(), Path(output).absolute()
    # /tmp is a platform alias on macOS; compare resolved paths for containment.
    real_root = root.resolve()
    if root.is_symlink():
        raise ValueError('desk record root must not be a symlink')
    if output.exists():
        raise ValueError('desk output directory already exists')
    if output.resolve().is_relative_to(real_root):
        raise ValueError('desk output must be outside the immutable record')
    if profile is not None and Path(profile).resolve().is_relative_to(real_root):
        raise ValueError('desk profile must be outside the immutable record')
    descriptor = committed_descriptor(repository, commit, record)
    # The caller chooses the local input root. Only descriptor-relative paths
    # are used below, never the original host's absolute locators.
    with DeskExecution(workers, profile) as execution:
        byte_count = execution.call('record.authenticate_before', authenticate, real_root, descriptor['files'])
        paths = {key: real_root/descriptor[key] for key in ROOT_FIELDS}
        state = json.loads((paths['session']/'session.json').read_bytes())
        plan = json.loads(paths['plan'].read_bytes())
        collection = json.loads((paths['registration_dir'].parent/'collection_plan.json').read_bytes())
        for member in collection['members']:
            relative_path(member['run_id'])
            if '/' in member['run_id']:
                raise ValueError('desk record run_id must be a single path component')
        if state.get('inputs', {}).get('pack_root') and 'targets' not in descriptor:
            raise ValueError('desk record requires the original pack target-precheck paths')
        if state.get('inputs', {}).get('pack_root') and any(
                m['run_id'] not in descriptor['targets'] for m in collection['members']):
            raise ValueError('desk record target-precheck paths must cover every roster member')
        state.update(measurement_root=str(paths['measurement_root']), registration_dir=str(paths['registration_dir']),
                     plan_path=str(paths['plan']), runs_roots={'claim': str(paths['runs_root'])},
                     inputs={'custody_root': str(paths['custody_root'])})
        plan['custody_root'] = str(paths['custody_root'])
        # Retain stdout until the second authentication succeeds. No source
        # archive or canonical PILOT/desk file is rewritten by this replay.
        stream = io.StringIO()
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.v4-desk-', dir=output.parent) as temporary:
            staging = Path(temporary)/'report'
            with redirect_stdout(stream):
                status = v4.pilot._desk(paths['session'], harvest=False, output=staging, report_root=output,
                    state=state, plan=plan, targets=descriptor.get('targets', {}), kit=v4.kit.KIT,
                    desk_schema=v4.kit.DESK_SCHEMA, extra_checks=v4.powermode_desk_check, execution=execution)
            execution.call('record.authenticate_after', authenticate, real_root, descriptor['files'])
            provenance = {'schema': SCHEMA, 'commit': commit, 'record': record,
                          'authenticated_files': len(descriptor['files']), 'authenticated_bytes': byte_count,
                          'harvest': 'previously recorded; not rerun'}
            (staging/'REPLAY.json').write_text(json.dumps(provenance, indent=2, sort_keys=True)+'\n')
            staging.rename(output)
        print(stream.getvalue(), end='')
        return status
