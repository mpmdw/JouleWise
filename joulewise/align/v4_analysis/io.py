"""Explicit, digest-bound desk files only; no bundle/data discovery or symlinks."""
import hashlib
import json
import os
from pathlib import Path
from copy import deepcopy


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                       allow_nan=False)+'\n').encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw, *, exact_seconds=False):
    """Reject duplicate/nonfinite JSON; preserve the recorded numeric type.

    The harness records seconds as binary floats. A JSON real is decoded to
    that float with float(lexeme); exact rational conversion to ns happens
    afterwards (P2 corrected, A21), never from the decimal spelling. Integers
    stay exact. String-valued endpoint/stamp seconds are not a recording and
    are refused by the raw release adapter. exact_seconds is accepted and
    ignored, for older callers.
    """
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def invalid(_):
        raise ValueError('nonfinite JSON')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid,
                      parse_float=float)


def local_path(root, name):
    path = Path(name)
    if (path.is_absolute() or not path.parts or any(p in ('.', '..', 'restricted')
            or p.startswith(('night-', 'jw-b5-')) for p in path.parts)):
        raise ValueError('source path refused')
    # Check each ancestor before touching the next: never follow a symlink into
    # sealed locations, even to stat or resolve its target.
    cursor = Path(root)
    if cursor.is_symlink():
        raise ValueError('source path symlink refused')
    for part in path.parts:
        cursor /= part
        if cursor.is_symlink():
            raise ValueError('source path symlink refused')
    return cursor


def input_path(path):
    """Reject sealed/external-user paths lexically, before any filesystem probe."""
    path = Path(os.path.abspath(path))
    cwd = Path.cwd()
    if ('restricted' in path.parts or any(p.startswith(('night-', 'jw-b5-')) for p in path.parts)
            or (path == Path('/Users/edr') or str(path).startswith('/Users/edr/')) and not path.is_relative_to(cwd)):
        raise ValueError('input path refused')
    base = cwd if path.is_relative_to(cwd) else Path(path.anchor)
    cursor = base
    for part in path.relative_to(base).parts:
        cursor /= part
        # /tmp itself is a system alias on macOS, not a data alias. Resolve
        # that known lexical alias without probing any link target.
        if str(cursor) in ('/tmp', '/var'):
            continue
        if cursor.is_symlink():
            raise ValueError('input path symlink refused')
    return path


def read_source(root, reference):
    return strict_json(read_blob(root, reference))


def read_blob(root, reference):
    root = input_path(root)
    path = local_path(root, reference['path'])
    raw = path.read_bytes()
    if digest(raw) != reference['sha256']:
        raise ValueError('source digest differs')
    return raw


def load(path, *, calibration_only=False, through_window=None, cache_dir=None, workers=1,
         document=None, source_session=None):
    """Input contains explicit thermal PILOT and raw alternative-desk exports.

    One in-invocation byte read per (relative path,digest), with every reference
    rechecked. This is read deduplication, not a persisted decision/refusal cache.
    """
    from . import calibration_identity
    calibration_identity.check()  # live predicate identity, before any source or calibration use
    path = input_path(path)
    payload = deepcopy(document) if document is not None else strict_json(path.read_bytes())
    if (any(k in payload for k in ('selection_desk', 'selection_source'))
            and not any(w['window'] == 'W1' for w in payload['windows'])):
        raise ValueError('selection-only W1 refused; W1 must be a window record')
    if through_window is not None:
        from .engine import ORDER
        order = ['W1', *ORDER]
        if through_window not in order:
            raise ValueError('window prefix differs')
        payload['windows'] = [w for w in payload['windows'] if order.index(w['window']) <= order.index(through_window)]
    root, sources, census = path.parent, (source_session if source_session is not None else {}), []
    if 'series_source' in payload:
        ref = payload['series_source']
        identity = (ref['path'], ref['sha256'])
        if identity not in sources:
            sources[identity] = read_source(root, ref)
        payload['series_manifest'] = sources[identity]
        census.append(dict(path=ref['path'], sha256=ref['sha256']))
    from .engine import slot_run_id, R24_SERIES_ORDER
    manifest = payload.get('series_manifest')
    if manifest is None:
        raise ValueError('release input requires the frozen R24 series manifest (series_source)')
    if tuple(w.get('window', w.get('id')) for w in manifest.get('windows', [])) != R24_SERIES_ORDER:
        raise ValueError('release series manifest must carry the full R24 allocation (W1, C1-C14, T1-T3)')
    for window in (payload.get('series_manifest') or {}).get('windows', []):
        for slot in window['members']:
            slot_run_id(slot, window.get('window', window.get('id')), strict=True)
    for window in payload['windows']:
        if calibration_only and window['window'].startswith('T'):
            continue
        if 'terminal_result' in window:
            # R23j P1: the terminal result is read only from its digest-bound
            # source; an inline value could substitute or manufacture a bar.
            raise ValueError('inline terminal_result refused on release input; use terminal_result_source')
        if 'terminal_result_source' in window:
            ref = window['terminal_result_source']
            identity = (ref['path'], ref['sha256'])
            if identity not in sources:
                sources[identity] = read_source(root, ref)
            window['terminal_result'] = sources[identity]
            if not any(r['path'] == ref['path'] and r['sha256'] == ref['sha256'] for r in census):
                census.append(dict(path=ref['path'], sha256=ref['sha256']))
        if 'members' in window:
            raise ValueError('file input requires source-bound desk exports')
        for slot in window['roster']:
            slot_run_id(slot, window['window'], strict=True)
        if 'raw_source' in window:
            from . import raw as adapter
            ref = window['raw_source']
            native = strict_json(read_blob(root, ref), exact_seconds=True)
            window['members'] = adapter.window(root, native, window.pop('roster'), window_id=window['window'],
                                              cache_dir=cache_dir, workers=workers)
            census.append(dict(path=ref['path'], sha256=ref['sha256']))
            continue
        records = []
        for key in ('thermal_source', 'residual_source'):
            ref = window[key]
            identity = (ref['path'], ref['sha256'])
            if identity not in sources:
                sources[identity] = read_source(root, ref)
            if not any(r['path'] == ref['path'] and r['sha256'] == ref['sha256'] for r in census):
                census.append(dict(path=ref['path'], sha256=ref['sha256']))
            records.append(sources[identity])
        thermal, residual = records
        thermals = {m['id']: m for m in thermal['members']}
        raw_members = residual['members']
        summaries = {m['run_id']: m for m in raw_members}
        if len(thermals) != len(thermal['members']) or len(summaries) != len(raw_members):
            raise ValueError('duplicate desk member')
        slots = window['roster']
        if set(thermals) != {s['run_id'] for s in slots} or set(summaries) != set(thermals):
            raise ValueError('desk roster differs')
        for slot in slots:
            run = slot['run_id']
            native = summaries[run]
            captured = native.get('captured', native.get('summary') is not None)
            if captured and 'owned_energy_flags' not in thermals[run]:
                # A2(4) release rule: no fallback to episode-level coverage flags.
                raise ValueError('release desk export lacks owned_energy_flags')
            window.setdefault('members', []).append(dict(slot=slot, thermal=thermals[run],
                summary=native.get('summary'), captured=captured,
                dc=native.get('dc_secondary'), source_flags=native.get('exclusion_codes', [])))
        window.pop('roster')
    for window in payload['windows']:
        # R22-2 bars are recomputed from the committed terminal result, so
        # every captured calibration window must carry it on the release path.
        if (window['window'].startswith('C') and any(m['captured'] for m in window.get('members', []))
                and 'terminal_result_source' not in window):
            raise ValueError('release C window lacks terminal_result_source: ' + window['window'])
    if calibration_only:
        payload['windows'] = [w for w in payload['windows'] if not w['window'].startswith('T')]
    payload['input_census'] = census
    return payload
