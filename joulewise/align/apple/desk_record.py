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

SCHEMA = 'joulewise.align_v4.desk_record.v2'
FINALIZE_SCHEMA = 'joulewise.align_v4.desk_finalize.v1'
ROOT_FIELDS = ('session', 'measurement_root', 'registration_dir', 'runs_root', 'custody_root', 'plan')


def relative_path(value):
    if (not isinstance(value, str) or not value or '\\' in value or '\n' in value
            or PurePosixPath(value).is_absolute()
            or any(p in ('', '.', '..', 'restricted', '.git') for p in value.split('/'))):
        raise ValueError(f'desk record requires a relative contained path: {value!r}')
    return value


def _git(repository, *args):
    return subprocess.run(['git', '-C', str(repository), *args], check=True, capture_output=True,
                          timeout=30, env=dict(os.environ, GIT_NO_LAZY_FETCH='1',
                                              GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1')).stdout


def committed_descriptor(repository, commit, record):
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('desk record requires a full 40-character commit SHA')
    relative_path(record)
    value = json.loads(_git(repository, 'show', f'{commit}:{record}'))
    if not isinstance(value, dict) or value.get('schema') != SCHEMA:
        raise ValueError('unsupported desk record schema')
    for key in ROOT_FIELDS:
        relative_path(value[key])
    if 'pack_root' in value:
        relative_path(value['pack_root'])
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


def describe(inputs, layout, *, repository=None):
    """Author a descriptor for an explicitly exported, terminal local tree.

    The caller exports evidence; this helper does not discover source-Mac
    directories or copy anything from locators in session/plan/config text.
    """
    root = _input_root(inputs)
    roots = {key: relative_path(layout[key]) for key in ROOT_FIELDS}
    if layout.get('pack_root') is not None:
        roots['pack_root'] = relative_path(layout['pack_root'])
    files = {}
    for relative, path in _files(root):
        digest = hashlib.sha256()
        with path.open('rb') as handle:
            for chunk in iter(lambda: handle.read(1024*1024), b''):
                digest.update(chunk)
        files[relative] = digest.hexdigest()
    if not (root/roots['custody_root']/'night/result.json').is_file():
        raise ValueError('terminal record is required before desk export')
    value = {'schema': SCHEMA, **roots, 'files': files,
             **({'targets': layout['targets']} if 'targets' in layout else {})}
    # Without a finalize manifest this is an inspection inventory only. Replay
    # refuses it; legacy callers cannot turn a self-authored inventory into a gate.
    if 'finalize_manifest' in layout:
        ref = layout['finalize_manifest']
        path = relative_path(ref['path'] if isinstance(ref, dict) else ref)
        repo = Path(repository or '.')
        raw = _contained_file(repo, path).read_bytes()
        value.update(finalize_manifest={'path': path, 'sha256': hashlib.sha256(raw).hexdigest()},
                     records_ref=layout['records_ref'])
    return value


def _input_root(inputs):
    path = Path(inputs).absolute()
    if 'restricted' in path.parts:
        raise ValueError('desk record restricted input root')
    # Permit the platform /tmp alias, but never an operator-supplied symlink root.
    if path.is_symlink():
        raise ValueError('desk record root must not be a symlink')
    return path.resolve()


def _contained_file(root, relative):
    relative_path(relative)
    path = Path(root)
    for part in relative.split('/'):
        path = path/part
        if path.is_symlink():
            raise ValueError(f'desk record symlink: {relative}')
    return path


def _read(root, path):
    return json.loads(_contained_file(root, path).read_bytes())


def _identity(root, descriptor):
    state = _read(root, descriptor['session']+'/session.json')
    plan = _read(root, descriptor['plan'])
    terminal = _read(root, descriptor['custody_root']+'/night/result.json')
    session_id, plan_id = state.get('session_id'), plan.get('plan_id')
    if (not isinstance(session_id, str) or not session_id or plan_id != session_id
            or terminal.get('plan_id') != plan_id
            or terminal.get('session_id', session_id) != session_id):
        raise ValueError('desk record session/plan identity does not match night/result.json')
    return {'session_id': session_id, 'plan_id': plan_id}


def _pack_target_file(descriptor):
    candidates = [descriptor['pack_root']+'/'+name
                  for name in ('extraction_spec.json', 'analysis_manifest_v3.json')]
    for path in candidates:
        if path in descriptor['files']:
            return path
    raise ValueError('desk record missing required files: '+' or '.join(candidates))


def _required_files(root, descriptor):
    s, c, r = (descriptor[k] for k in ('session', 'custody_root', 'registration_dir'))
    required = [s+'/session.json', descriptor['plan'], r.rsplit('/', 1)[0]+'/collection_plan.json',
                *[r+'/'+n for n in ('inputs.json', 'u3_bar.json', 'wp19_receipt.json', 'r1_soak_reference.json')],
                *[s+'/'+n for n in ('desk.json', 'staging/harvest.stdout', 'staging/harvest.stderr',
                    'archive/derived/exclusions.json', 'archive/derived/flags.jsonl',
                    'archive/withheld/battery-assist.json')],
                c+'/night/result.json', c+'/night/hazard_result.json']
    for name in ('collection/run_clock.jsonl', 'hazards/monitor/thermal.jsonl'):
        path = c+'/'+name
        required.append(path if path in descriptor['files'] else path+'.zst' if path+'.zst' in descriptor['files'] else path)
    missing = set(required)-set(descriptor['files'])
    if missing:
        raise ValueError('desk record missing required files: '+', '.join(sorted(missing)))
    meter = _read(root, c+'/night/hazard_result.json').get('meter') or {}
    streams = meter.get('streams') or []
    if not streams:
        raise ValueError('desk record missing required files: '+c+'/hazards/meter/stream-*.jsonl[.zst]')
    for stream in streams:
        path = relative_path(stream['path'])
        if not path.startswith('hazards/meter/stream-'):
            raise ValueError('desk record invalid meter custody path: '+path)
        path = c+'/'+path
        required.append(path if path in descriptor['files'] else path+'.zst' if path+'.zst' in descriptor['files'] else path)
    if descriptor.get('pack_root'):
        required.append(descriptor['pack_root']+'/plan_tree.json')
        required.append(_pack_target_file(descriptor))
    missing = set(required)-set(descriptor['files'])
    if missing:
        raise ValueError('desk record missing required files: '+', '.join(sorted(missing)))
    return sorted(required)


def _targets(root, descriptor):
    state = _read(root, descriptor['session']+'/session.json')
    if not state.get('inputs', {}).get('pack_root'):
        if descriptor.get('targets') or descriptor.get('pack_root'):
            raise ValueError('desk record unexpected pack targets')
        return {}
    if not descriptor.get('pack_root'):
        raise ValueError('desk record missing required files: exported pack_root/plan_tree.json')
    pack = root/relative_path(descriptor['pack_root'])
    tree = _read(root, descriptor['pack_root']+'/plan_tree.json')
    _pack_target_file(descriptor)  # never silently fall back after an incomplete pack export
    # build_roster reads configs to select target cells. Validate every locator
    # it may use before invoking it; absolute host locators are never followed.
    external = tree.get('external_inputs') or {}
    manifests = external.get('manifests', []) if isinstance(external, dict) else external
    configs = [m.get('config_path') for m in tree.get('science', [])]
    configs += [m.get('path') for item in manifests for m in item.get('members', [])]
    configs += [m.get('path') for stage in tree.get('stage_graph', [])
                for m in (stage.get('spare_retry') or {}).get('members', [])]
    missing = []
    for path in configs:
        if path is None:
            continue
        relative_path(path)
        base = descriptor['measurement_root'] if path.startswith('configs/') else descriptor['pack_root']
        if base+'/'+path not in descriptor['files']:
            missing.append(base+'/'+path)
    if missing:
        raise ValueError('desk record missing required files: '+', '.join(sorted(missing)))
    from joulewise.b5.harvest import build_roster
    targets = {m['run_id']: [c['target_precheck_path'] for c in m.get('cells', [])
                if c.get('target') is not False and isinstance(c.get('target_precheck_path'), list)
                and c['target_precheck_path']]
               for m in build_roster(pack, root/descriptor['measurement_root'])['members']}
    collection = _read(root, descriptor['registration_dir'].rsplit('/', 1)[0]+'/collection_plan.json')
    if any(m['run_id'] not in targets for m in collection['members']):
        raise ValueError('desk record pack roster does not cover collection members')
    if 'targets' in descriptor and descriptor['targets'] != targets:
        raise ValueError('desk record target-precheck paths mismatch exported pack roster')
    return targets


def finalize(inputs, layout):
    """Seal the explicit export at MBP finalization, before transfer/record push.

    No host locators are followed and no harvest is launched. The pushed
    records ref is the custody trust anchor, not this producer label alone.
    """
    descriptor = describe(inputs, {k: v for k, v in layout.items() if k != 'finalize_manifest'})
    root = _input_root(inputs)
    return _finalize_record(root, descriptor)


def _finalize_record(root, descriptor):
    """Rebuild small receipt bindings over an already inventoried export."""
    required = _required_files(root, descriptor)
    identity = _identity(root, descriptor)
    _targets(root, descriptor)
    s = descriptor['session']
    desk = _read(root, s+'/desk.json')
    if (desk.get('plan_id') != identity['plan_id'] or desk.get('harvest_status') != 'ok'
            or type(desk.get('harvest_exit')) is not int or desk['harvest_exit'] not in (0, 6)):
        raise ValueError('desk record requires recorded MBP harvest success')
    archive = {p: digest for p, digest in descriptor['files'].items() if p.startswith(s+'/archive/')}
    return {'schema': FINALIZE_SCHEMA, 'producer': 'mbp_finalize', **identity,
            'roots': {k: descriptor[k] for k in (*ROOT_FIELDS, 'pack_root') if k in descriptor},
            'files': descriptor['files'], 'required_files': required,
            'harvest': {'status': 'ok', 'exit_code': desk['harvest_exit'], 'archive_files': archive,
                        'receipt': s+'/desk.json', 'stdout': s+'/staging/harvest.stdout',
                        'stderr': s+'/staging/harvest.stderr'}}


def verified_descriptor(repository, commit, record):
    descriptor = committed_descriptor(repository, commit, record)
    ref = descriptor.get('records_ref', '')
    if (not isinstance(ref, str) or not ref.startswith('refs/remotes/')
            or not re.search(r'[/_-]records(?:[/_-]|$)', ref)):
        raise ValueError('desk record requires a pushed records branch ref')
    _git(repository, 'check-ref-format', ref)
    tip = _git(repository, 'rev-parse', '--verify', ref+'^{commit}').decode().strip()
    _git(repository, 'merge-base', '--is-ancestor', commit, tip)
    binding = descriptor.get('finalize_manifest') or {}
    path = relative_path(binding.get('path'))
    raw = _git(repository, 'show', f'{commit}:{path}')
    if hashlib.sha256(raw).hexdigest() != binding.get('sha256'):
        raise ValueError('desk record finalize manifest digest mismatch')
    manifest = json.loads(raw)
    if (manifest.get('schema') != FINALIZE_SCHEMA or manifest.get('producer') != 'mbp_finalize'
            or manifest.get('files') != descriptor['files']
            or manifest.get('roots') != {k: descriptor[k] for k in (*ROOT_FIELDS, 'pack_root') if k in descriptor}
            or (manifest.get('harvest') or {}).get('status') != 'ok'):
        raise ValueError('desk record does not match successful MBP finalize manifest')
    harvest = manifest['harvest']
    s = descriptor['session']
    expected_harvest = {'status': 'ok', 'exit_code': harvest.get('exit_code'),
                        'receipt': s+'/desk.json', 'stdout': s+'/staging/harvest.stdout',
                        'stderr': s+'/staging/harvest.stderr',
                        'archive_files': {p: d for p, d in descriptor['files'].items() if p.startswith(s+'/archive/')}}
    if (harvest != expected_harvest or type(harvest['exit_code']) is not int
            or harvest['exit_code'] not in (0, 6) or not harvest['archive_files']
            or any(harvest[k] not in descriptor['files'] for k in ('receipt', 'stdout', 'stderr'))
            or not isinstance(manifest.get('required_files'), list) or not manifest['required_files']
            or any(p not in descriptor['files'] for p in manifest['required_files'])
            or not isinstance(manifest.get('session_id'), str) or not manifest['session_id']
            or manifest.get('plan_id') != manifest['session_id']):
        raise ValueError('desk record invalid MBP finalize/harvest binding')
    return descriptor, manifest


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


def _publish(staging, output):
    # Claim the name exclusively. rename() alone can replace an empty directory
    # created by another process after the earlier existence check.
    output.mkdir()
    moved = []
    try:
        for path in sorted(staging.iterdir()):
            destination = output/path.name
            path.rename(destination)
            moved.append(destination)
    except BaseException:
        for path in moved:
            path.unlink()
        try:
            output.rmdir()
        except OSError:
            pass
        raise


def replay(repository, commit, record, inputs, output, *, workers=1, profile=None):
    """Replay finalized, pushed evidence; require successful upstream harvest."""
    from joulewise.align.apple.desk_execution import DeskExecution
    from scripts import align_v4_session as v4
    real_root, output = _input_root(inputs), Path(output).absolute()
    if output.exists():
        raise ValueError('desk output directory already exists')
    if output.resolve().is_relative_to(real_root):
        raise ValueError('desk output must be outside the immutable record')
    if profile is not None and (Path(profile).resolve().is_relative_to(real_root)
                               or Path(profile).resolve().is_relative_to(output.resolve())):
        raise ValueError('desk profile must be outside the immutable record and report')
    descriptor, manifest = verified_descriptor(repository, commit, record)
    output.parent.mkdir(parents=True, exist_ok=True)
    stream = io.StringIO()
    with tempfile.TemporaryDirectory(prefix='.v4-desk-', dir=output.parent) as temporary:
        staging = Path(temporary)/'report'
        # Complete shutdown and profile publication BEFORE publishing reports.
        with DeskExecution(workers, profile) as execution:
            byte_count = execution.call('record.authenticate_before', authenticate, real_root, descriptor['files'])
            identity = _identity(real_root, descriptor)
            targets = _targets(real_root, descriptor)
            # Recompute the finalize receipt, including exact archive hashes and
            # harvest exit/log bindings, rather than trusting a status label.
            expected = _finalize_record(real_root, descriptor)
            if manifest != expected:
                raise ValueError('desk record MBP finalize/harvest receipt mismatch')
            paths = {key: real_root/descriptor[key] for key in ROOT_FIELDS}
            state = _read(real_root, descriptor['session']+'/session.json')
            plan = _read(real_root, descriptor['plan'])
            collection = _read(real_root, descriptor['registration_dir'].rsplit('/', 1)[0]+'/collection_plan.json')
            for member in collection['members']:
                relative_path(member['run_id'])
                if '/' in member['run_id']:
                    raise ValueError('desk record run_id must be a single path component')
            state.update(measurement_root=str(paths['measurement_root']), registration_dir=str(paths['registration_dir']),
                         plan_path=str(paths['plan']), runs_roots={'claim': str(paths['runs_root'])},
                         inputs={'custody_root': str(paths['custody_root'])})
            plan['custody_root'] = str(paths['custody_root'])
            with redirect_stdout(stream):
                status = v4.pilot._desk(paths['session'], harvest=False, output=staging, report_root=output,
                    state=state, plan=plan, targets=targets, kit=v4.kit.KIT,
                    desk_schema=v4.kit.DESK_SCHEMA, extra_checks=v4.powermode_desk_check, execution=execution)
            execution.call('record.authenticate_after', authenticate, real_root, descriptor['files'])
            status.update(harvest_status='ok', harvest_exit=manifest['harvest']['exit_code'])
            (staging/'desk.json').write_text(json.dumps(status, indent=2, sort_keys=True)+'\n')
            provenance = {'schema': SCHEMA, 'commit': commit, 'record': record, **identity,
                          'records_ref': descriptor['records_ref'],
                          'finalize_manifest': descriptor['finalize_manifest'],
                          'descriptor_sha256': hashlib.sha256(_git(repository, 'show', f'{commit}:{record}')).hexdigest(),
                          'authenticated_files': len(descriptor['files']), 'authenticated_bytes': byte_count,
                          'harvest_status': 'ok', 'harvest': manifest['harvest'],
                          'pilot_status': status['pilot_status'],
                          'pilot_sha256': hashlib.sha256((staging/'PILOT.json').read_bytes()).hexdigest()}
            (staging/'REPLAY.json').write_text(json.dumps(provenance, indent=2, sort_keys=True)+'\n')
        _publish(staging, output)
    print(stream.getvalue(), end='')
    return status


def gate_evidence(repository, commit, record, output):
    """Build the structured full_desk_gate artifact reference for triage."""
    descriptor, _ = verified_descriptor(repository, commit, record)
    return {'repository': str(Path(repository).resolve()), 'record_commit': commit, 'record': record,
            'records_ref': descriptor['records_ref'], 'harvest_status': 'ok',
            'reports': {name: {'path': str((Path(output)/name).resolve()),
                               'sha256': hashlib.sha256((Path(output)/name).read_bytes()).hexdigest()}
                        for name in ('PILOT.json', 'REPLAY.json')}}


def validate_gate(evidence, previous_window):
    """Verify report bytes and their binding to the pushed finalized record.

    This reads small committed/report artifacts, never raw export/host locators.
    """
    if not isinstance(evidence, dict):
        raise ValueError('full desk pass requires a structured artifact binding')
    repo, commit, record = (evidence[k] for k in ('repository', 'record_commit', 'record'))
    descriptor, manifest = verified_descriptor(repo, commit, record)
    reports = {}
    for name in ('PILOT.json', 'REPLAY.json'):
        ref = evidence['reports'][name]
        raw = Path(ref['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != ref['sha256']:
            raise ValueError('full desk report digest mismatch: '+name)
        reports[name] = json.loads(raw)
    pilot, receipt = reports['PILOT.json'], reports['REPLAY.json']
    if (evidence.get('harvest_status') != 'ok' or evidence.get('records_ref') != descriptor['records_ref']
            or receipt.get('schema') != SCHEMA or receipt.get('commit') != commit or receipt.get('record') != record
            or receipt.get('records_ref') != descriptor['records_ref']
            or receipt.get('finalize_manifest') != descriptor['finalize_manifest']
            or receipt.get('descriptor_sha256') != hashlib.sha256(_git(repo, 'show', f'{commit}:{record}')).hexdigest()
            or receipt.get('pilot_sha256') != evidence['reports']['PILOT.json']['sha256']
            or receipt.get('harvest_status') != 'ok' or receipt.get('harvest') != manifest['harvest']
            or receipt.get('pilot_status') != 'instrument_ok' or pilot.get('status') != 'instrument_ok'
            or not pilot.get('checks') or any(v is not True for v in pilot['checks'].values())
            or manifest.get('session_id') != previous_window or manifest.get('plan_id') != previous_window
            or receipt.get('session_id') != previous_window or receipt.get('plan_id') != previous_window
            or pilot.get('session_id') != previous_window or pilot.get('plan_id') != previous_window):
        raise ValueError('full desk pass does not bind successful harvest/reports to the previous window record')
    return True
