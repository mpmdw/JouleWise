#!/usr/bin/env python3
"""Prepare, hand off, and desk the isolated NON-CLAIM BYTES item-H session.

Prepare never installs. Install is the lead's final action before exiting.
No watchdog collection.active marker is used: the real installer publishes
~/Library/LaunchAgents/com.joulewise.night{,.deadman}.plist with --plan.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import datetime as dt
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.b5 import chain, plan
from joulewise.b5.harvest import member_spans
from joulewise.b6 import desk_identity, plan_inputs, registration
from joulewise.b6.archive import bundle_of
from joulewise.desk_compress import read_bytes
from joulewise.hazards.clock import FREQUENCY_SCALE, WINDOW_SKEW_MAX_NS

KIT = Path('configs/campaigns/bytes_mac_check')
PACK_ID = 'bytes-mac-check'
# DriverLane's default lead: 420 s, rounded up to a minute; the installer
# requires 300 s. Use the measurement checkout's loop.json value verbatim.
DEFAULT_LEAD_S = 420
# DriverLane.launch and night_agent_install require this preparation lead.
MIN_LEAD_S = 300
# DriverLane/DeskLane's existing harvest budget, not a measured allowance.
HARVEST_TIMEOUT_S = 4 * 3600


class PhysicalHazard(ValueError):
    """Missing model payload or insufficient physical storage for this window."""


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n'
    temporary = path.with_name('.' + path.name + '.tmp')
    temporary.write_text(raw)
    temporary.replace(path)


def read(path, default=None):
    try:
        return json.loads(read_bytes(Path(path)))
    except FileNotFoundError:
        return {} if default is None else default


def rows(path):
    try:
        return [json.loads(line) for line in read_bytes(Path(path)).splitlines() if line.strip()]
    except FileNotFoundError:
        return []


def locator(path):
    path = Path(path)
    actual = path if path.is_file() else Path(str(path) + '.zst')
    return {'path': str(actual), 'sha256': hashlib.sha256(actual.read_bytes()).hexdigest()}


def disk_bytes(root, *, excluded=(), seen=None):
    """du-style allocated bytes, including directory blocks; never follow links."""
    root = Path(root)
    excluded = set(map(Path, excluded))
    seen = set() if seen is None else seen
    total = 0
    if not root.exists():
        return 0
    for directory, children, files in os.walk(root, followlinks=False):
        directory = Path(directory)
        children[:] = [n for n in children if directory / n not in excluded]
        for path in (directory, *(directory / name for name in files)):
            stat = path.lstat()
            key = stat.st_dev, stat.st_ino
            if key not in seen:
                total += stat.st_blocks * 512  # POSIX st_blocks units are 512 bytes.
                seen.add(key)
    return total


def measurement_view(source, session):
    """Disposable launch attachment; original tree/configs/code stay read-only.

    Mirrors the sparse measurement setup used for B6's one-off non-claim
    smoke. Only the session's calibration ledger and pin are independent
    copies. The fixed roster, manifests and configs are never rewritten.
    """
    view = session / 'measurement'
    view.mkdir()
    for p in source.iterdir():
        if p.name not in ('configs', 'runs'):
            (view / p.name).symlink_to(p, target_is_directory=p.is_dir())
    for relative, omitted in (('configs', {'campaigns', 'calibration'}),
                              ('configs/campaigns', set()), ('configs/calibration', {Path(plan.HEAD_PIN_RELATIVE).name})):
        directory = view / relative
        directory.mkdir(parents=True, exist_ok=True)
        for p in (source / relative).iterdir():
            if p.name not in omitted:
                (directory / p.name).symlink_to(p, target_is_directory=p.is_dir())
    shutil.copyfile(source / plan.HEAD_PIN_RELATIVE, view / plan.HEAD_PIN_RELATIVE)
    ledger = view / plan.DEFAULT_LEDGER_RELATIVE
    ledger.parent.mkdir(parents=True, exist_ok=True)
    if (source / plan.DEFAULT_LEDGER_RELATIVE).is_file():
        shutil.copyfile(source / plan.DEFAULT_LEDGER_RELATIVE, ledger)
    pack = view / 'configs/campaigns' / PACK_ID
    pack.mkdir()
    for p in (source / KIT).iterdir():
        if p.name != 'plan_tree.json':
            (pack / p.name).symlink_to(p, target_is_directory=p.is_dir())
    tree = read(source / KIT / 'plan_tree.json')
    template = read(source / 'configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json')
    launch = template['arm_attachments']['launch']
    for row in launch.get('bindings', []):
        if row['name'] == 'claim_runs_root': row['leaf'] = tree['roots']['claim_root_leaf']
        if row['name'] == 'bound_runs_root': row['leaf'] = tree['roots']['bound_root_leaf']
    tree.setdefault('arm_attachments', {})['launch'] = launch
    # The generated scaffold carries external_inputs as two mapping-key
    # strings. Reconstruct its manifests from the very same collection
    # dispatches. Membership comes solely from the fixed tree, not inference.
    science = {r['run_id'] for r in tree['science']}
    manifests = []
    for stage in tree['stage_graph']:
        if stage['kind'] != 'campaign_collection':
            continue
        ref = stage['input']
        manifest_path = source / ref['path']
        members = []
        for row in read(manifest_path)['executed_order'][:stage['expected_count']]:
            if row['run_id'] in science:
                continue
            config = manifest_path.parent / row['config']
            members.append({'run_id': row['run_id'], 'ordinal': row.get('index'),
                'path': config.relative_to(source).as_posix(), 'sha256': locator(config)['sha256']})
        if members:
            manifests.append({'external_input_id': stage['stage_id'],
                'manifest': {'path': ref['path'], 'sha256': locator(manifest_path)['sha256']}, 'members': members})
    tree['external_inputs'] = {'manifests': manifests, 'artifacts': []}
    write(pack / 'plan_tree.json', tree)
    write(session / 'staging/measurement-view.json', {
        'source_measurement_root': str(source), 'measurement_root': str(view),
        'source_tree': locator(source / KIT / 'plan_tree.json'), 'launch_template':
            locator(source / 'configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json'),
        'staged_tree': locator(pack / 'plan_tree.json'),
        'changes': ['arm_attachments.launch: existing fourteen-binding interface; kit root leaves',
                    'pack directory spelling: governed b6_layout.packs[0]',
                    'external_inputs: same scaffold members resolved from collection manifests'],
        'ledger': 'independent copy when present; never fabricate a missing ledger',
        'read_only_source': True})
    return view, pack


def important_capacity(root, *, run=subprocess.run):
    """macOS volume available-for-important-usage, queried through Foundation."""
    script = ('ObjC.import("Foundation"); var e=Ref(); var u=$.NSURL.fileURLWithPath('
              + json.dumps(str(root)) + '); var v=u.resourceValuesForKeysError('
              '[$.NSURLVolumeAvailableCapacityForImportantUsageKey],e); '
              'v.objectForKey($.NSURLVolumeAvailableCapacityForImportantUsageKey).stringValue.js')
    result = run(['/usr/bin/osascript', '-l', 'JavaScript', '-e', script],
                 capture_output=True, text=True, check=False, timeout=30)
    return int(result.stdout.strip()) if result.returncode == 0 else None


def disk_snapshot(root, *, statvfs=os.statvfs, capacity=important_capacity):
    stat = statvfs(root)
    free = int(stat.f_bavail) * int(stat.f_frsize)
    try:
        important = capacity(root)
    except (OSError, ValueError, subprocess.SubprocessError):
        important = None
    return {'free_bytes': free, 'f_bavail': int(stat.f_bavail), 'f_frsize': int(stat.f_frsize),
            'available_for_important_usage_bytes': important,
            'purgeable_bytes': important - free if important is not None else None,
            'flags': [] if important is not None else ['disk.purgeable_unreadable']}


def prepare(measurement_root, session_root, *, run=subprocess.run, now=time.time,
            statvfs=os.statvfs, capacity=important_capacity):
    measurement, session = Path(measurement_root).resolve(), Path(session_root).resolve()
    reg = measurement / KIT / 'registration'
    sized = registration.load_sizing(reg)['packs'][PACK_ID]
    pins = registration.load_identity_pins(reg)
    inventory = read(reg / 'model_artifact_inventory.json')['artifacts']
    for name, unit in pins['units'].items():
        source = Path(unit['model_source'])
        if not source.is_dir() or any(not (source / f['path']).is_file() for f in inventory[name]['inventory']):
            raise PhysicalHazard('models missing: ' + str(source))
    if session.exists() and any(session.iterdir()):
        raise ValueError('session root must be empty; preserve the existing session')
    session.mkdir(parents=True, exist_ok=True)
    clock = now()
    session_id = 'bytes-h-' + dt.datetime.fromtimestamp(clock, dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    config = read(measurement / 'configs/b6/loop.json')
    lead = config.get('launch_lead_s', DEFAULT_LEAD_S)
    if not finite(lead) or lead < MIN_LEAD_S:
        raise ValueError("launch_lead_s must leave the installer's 300 seconds")
    t0 = 60 * math.ceil((clock + lead) / 60)
    expected_max = plan_inputs.window_max_s({'programmed_span_s': {'seconds': sized['programmed_span_s']}})
    print('session_id: ' + session_id)
    print('candidate_t0: ' + dt.datetime.fromtimestamp(t0, dt.timezone.utc).isoformat())
    print(f"maximum_duration_s: {expected_max}; programmed_span_s: {math.ceil(sized['programmed_span_s'])}")
    snapshot = disk_snapshot(session, statvfs=statvfs, capacity=capacity)
    required = sized['estimated_footprint_bytes']
    # H-DISK-RULING addendum 1: the native arm budgets raw plus two
    # full-roster backup targets, although the physical backups partition
    # one roster copy. Encode P in its existing integer caller fields.
    terms = sized['disk_derivation']
    native_copies = 3
    per_member, remainder = divmod(terms['peak_copies'] * terms['B_bytes'],
                                 native_copies * sized['member_count'])
    native_budget = {
        'kind': 'budget encoding derived from P',
        'formula': 'q=floor(c*B/(native_copies*member_count)); headroom=(c*B-native_copies*member_count*q)+c*WAIT+fixed',
        'native_copies': native_copies, 'bytes_per_member': per_member,
        'rounding_remainder_bytes': remainder,
        'headroom_bytes': remainder + terms['extra_wait_peak_bytes'] + terms['fixed_retained_bytes']}
    disk = {**snapshot, 'prepare_free_bytes': snapshot['free_bytes'],
            'estimated_footprint_bytes': required, 'required_free_bytes': required,
            'derivation': terms, 'member_count': sized['member_count'],
            'native_arm_budget': native_budget,
            'flags': snapshot['flags'] + ['disk.budget_encoded_from_p']}
    print('disk: ' + json.dumps(disk, sort_keys=True))
    if snapshot['free_bytes'] < required:
        raise PhysicalHazard('not enough disk for the planned physical allocation P')
    for name in ('runs-parent', 'staging'):
        (session / name).mkdir()
    identities, notes = desk_identity.collect(measurement, session / 'staging/inputs', run=run)
    # Existing builder already exposes registration_dir. Only this caller's
    # kit path, bytes and registration locator differ from DriverLane inputs.
    inputs = plan_inputs.build(measurement, reg, PACK_ID, session_id, identities,
        custody_root=session / 'custody', runs_parent=session / 'runs-parent',
        claim_backup=session / 'backup-claim', bound_backup=session / 'backup-bound', run=run)
    view, pack = measurement_view(measurement, session)
    inputs.update(measurement_root=str(view), pack_root=str(pack),
                  bytes_per_member=per_member)
    inputs['thresholds']['disk']['headroom_bytes'] = native_budget['headroom_bytes']
    inputs['t0_epoch_s'] = t0
    record = None
    try:
        record = plan.write_window_plan(inputs, now=now)
    except plan.WindowPlanError as exc:
        # A missing/stale calibration ledger or another record condition is a
        # printed preparation flag, not a new physical collection refusal. The
        # unmodified writer never publishes a malformed plan.
        notes.append({'kind': 'plan.not_written', 'detail': str(exc)})
    if record and record['window_max_s'] != expected_max:
        raise ValueError('prepared and written window_max_s disagree')
    status = run(['git', '-C', str(measurement), 'status', '--porcelain'],
                 capture_output=True, text=True, check=False, timeout=30)
    if status.returncode or status.stdout.strip():
        notes.append({'kind': 'measurement_checkout_dirty_or_unobserved', 'status': status.stdout.strip()})
    notes.extend({'kind': 'runtime_stack_unobserved', 'model_id': name} for name in pins['units'])
    notes.append({'kind': 'sizing.planning_bound_interpolated', 'model_id': 'qwen3-8b-8bit'})
    state = {'schema_version': 'joulewise.bytes_h_session.v1', 'non_claim': True,
        'session_id': session_id, 'source_measurement_root': str(measurement),
        'measurement_root': str(view), 'registration_dir': str(view / KIT / 'registration'),
        'session_root': str(session), 'preparation_status': 'STAGED' if record else 'INPUTS_ONLY',
        'plan_path': record['plan']['path'] if record else str(session / 'custody/night_plan.json'),
        'plan_sha256': record['plan']['sha256'] if record else None, 'inputs': inputs, 'disk': disk, 'flags': notes,
        'runs_roots': record['runs_roots'] if record else {}, 't0_epoch_s': t0,
        'window_max_s': expected_max}
    write(session / 'staging/plan-inputs.json', inputs)
    write(session / 'session.json', state)
    print('t0: ' + dt.datetime.fromtimestamp(state['t0_epoch_s'], dt.timezone.utc).isoformat())
    print('preparation_status: ' + state['preparation_status'])
    for flag in notes:
        print('flag: ' + json.dumps(flag, sort_keys=True))
    return state


def install(session_root, *, run=subprocess.run, home=None, now=time.time):
    session = Path(session_root).resolve()
    state = read(session / 'session.json')
    installed = state.get('install', {})
    # Same durable idempotency key as DriverLane.launch. A terminal receipt
    # or a loaded calendar job also survives a crash before install recording.
    if installed.get('exit_code') == 0 or (Path(state['inputs']['custody_root']) / 'night/result.json').is_file():
        print('install already completed or session terminal; installer not called')
        return installed
    label = 'com.joulewise.night'
    job = run(['launchctl', 'print', f'gui/{os.getuid()}/{label}'],
              check=False, capture_output=True, text=True, timeout=10)  # DriverLane._job census budget.
    if job.returncode == 0:
        print('launchd already holds the night job; installer not called')
        return installed
    absent = f'Could not find service "{label}" in domain for user gui: {os.getuid()}'
    if job.returncode != 113 or absent not in (job.stderr or '').splitlines():
        raise RuntimeError('launchd job state unavailable')
    measurement = Path(state['measurement_root'])
    plan_path = Path(state['plan_path'])
    if locator(plan_path)['sha256'] != state['plan_sha256']:
        raise ValueError('prepared plan bytes changed')
    t0 = read(plan_path).get('t0_epoch_s')
    if not finite(t0) or t0 <= now():
        message = 'plan t0 has passed or is unavailable; prepare again in a new empty session root'
        print(message)
        raise ValueError(message)
    argv = [str(measurement / 'scripts/install_night_agent.sh'), '--plan', str(plan_path),
            '--python', str(measurement / '.venv/bin/python'), '--courier-bin',
            str(measurement / 'scripts/b6_courier.sh'), '--launchctl-bin', 'launchctl']
    attempt = 1
    # Existing logs reserve their number even if a crash lost session.json.
    while any((session / f'staging/install-{attempt:03d}.{suffix}').exists() for suffix in ('stdout', 'stderr')):
        attempt += 1
    stdout = session / f'staging/install-{attempt:03d}.stdout'
    stderr = session / f'staging/install-{attempt:03d}.stderr'
    # Same installer timeout as DriverLane._installer.
    result = run(argv, check=False, capture_output=True, text=True, timeout=180)
    with stdout.open('x') as stream:
        stream.write(result.stdout or '')
    with stderr.open('x') as stream:
        stream.write(result.stderr or '')
    state['install'] = {'argv': argv, 'exit_code': result.returncode, 'attempt': attempt,
                        'stdout_path': str(stdout), 'stderr_path': str(stderr)}
    # The installer owns publication at Path.home()/Library/LaunchAgents. Both
    # plists contain the absolute --plan path; the watchdog's installed-agent
    # fence reads them. No local or global collection.active is written (F1).
    directory = Path(home or Path.home()) / 'Library/LaunchAgents'
    paths = [str(directory / (name + '.plist')) for name in ('com.joulewise.night', 'com.joulewise.night.deadman')]
    state['install']['plist_paths'] = paths
    state.setdefault('install_attempts', []).append(state['install'])
    write(session / 'session.json', state)
    if result.returncode:
        raise RuntimeError('night job installer failed; see ' + str(stderr))
    for path in paths:
        print('installed_plist: ' + path)
    print('Lead handoff: exit this agent session now; the chain also checks its agent census.')
    return state['install']


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def numeric_receipt(value):
    if type(value) not in (int, float, str):
        return False
    try:
        return Decimal(str(value)).is_finite()
    except (InvalidOperation, ValueError):
        return False


def interval(start, end):
    return end - start if finite(start) and finite(end) and end >= start else None


def event_duration(events, start, end):
    a = next((r.get('timestamp_s') for r in events if r.get('event_type') == start), None)
    b = next((r.get('timestamp_s') for r in reversed(events) if r.get('event_type') == end), None)
    return interval(a, b)


def mapping(value):
    return value if isinstance(value, dict) else {}


def clock_span(metadata):
    anchor = mapping(mapping(metadata.get('uncertainty_evidence')).get('clock_anchor'))
    stamps = mapping(anchor.get('clock_stamps'))
    first, last = mapping(stamps.get('pre_spawn')), mapping(stamps.get('post_parse'))
    # Same paired clock endpoints used by the native anchor fit. Include the
    # read half-widths, not request-only sampling markers or calibration time.
    return interval(first.get('monotonic_before_s'), last.get('monotonic_after_s'))


def journal_span(row):
    a = mapping(row.get('started')).get('monotonic_ns')
    b = mapping(row.get('finished')).get('monotonic_ns')
    return (a, b) if type(a) is int and type(b) is int and b >= a else None


def union_seconds(spans):
    merged = []
    for a, b in sorted(spans):
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return sum(b - a for a, b in merged)


def cpu_overlap(journal, start, end):
    """Sum whole native census quanta overlapping the request; never prorate.

    contention.flags uses this request-overlap support. The census gives a
    CPU delta per full interval, not its unknown distribution inside it.
    """
    spans, quanta, cpu = [], 0, 0.0
    for row in journal:
        values = mapping(row.get('values'))
        span = mapping(values.get('interval')).get('monotonic_ns')
        rate = values.get('outside_total_cpu_s_per_s')
        elapsed = values.get('elapsed_s')
        if (row.get('error') or not isinstance(span, (list, tuple)) or len(span) != 2
            or not all(type(t) is int for t in span) or not finite(rate) or rate < 0
            or not finite(elapsed) or elapsed <= 0):
            continue
        a, b = max(start, span[0]), min(end, span[1])
        if b > a:
            spans.append((a, b)); quanta += 1
            cpu += rate * elapsed
    if union_seconds(spans) != end - start or sum(b - a for a, b in spans) != end - start:
        return None, None  # no gap-filled zero, no double-counting overlapping journal rows
    return cpu, quanta


def fitted_clock(clock_rows):
    """OLS slope plus the review's read-skew noise model, not a new gate.

    Assume independent uniform anchor error over +/- WINDOW_SKEW_MAX_NS:
    sigma = bound/sqrt(3); SE(slope) = sigma/sqrt(sum((x-x_mean)**2)).
    At the monitor's 1 s cadence, Sxx is about n*span**2/12, so a
    150 s / ~150-anchor member has SE ~0.27 ppm at the 250 us limit.
    Use actual admitted anchors below. This modeled single-fit SE is not
    an empirical uncertainty or a correction for worst-of-members selection.
    """
    anchors = [mapping(r.get('values')).get('anchor') for r in clock_rows if not r.get('error')]
    anchors = [r for r in anchors if isinstance(r, dict) and type(r.get('monotonic_raw_ns')) is int
               and type(r.get('anchor_ns')) is int
               and 0 <= r.get('read_skew_ns', -1) <= WINDOW_SKEW_MAX_NS]
    if len(anchors) < 2:  # a line's rank requires two distinct abscissae.
        return None
    origin = anchors[0]['monotonic_raw_ns']
    xs = [Fraction(r['monotonic_raw_ns'] - origin) for r in anchors]
    ys = [Fraction(r['anchor_ns']) for r in anchors]
    xm, ym = sum(xs) / len(xs), sum(ys) / len(ys)
    denominator = sum((x - xm)**2 for x in xs)
    if not denominator:
        return None
    return {'rate_ppm': float(sum((x - xm) * (y - ym) for x, y in zip(xs, ys)) / denominator * 1e6),
            'span_s': float((max(xs) - min(xs)) / 10**9), 'n': len(anchors),
            'standard_error_ppm': math.sqrt(float(Fraction(WINDOW_SKEW_MAX_NS**2, 3) / denominator)) * 1e6}


def receipt(session, name, session_id, sources, flags):
    path = session / 'receipts' / (name + '.json')
    try:
        value = read(path)
        if not value:
            return {}
        sources[str(path)] = locator(path)
    except (OSError, ValueError):
        flags.append({'code': 'records.receipt_unusable', 'path': str(path)})
        return {}
    if (not isinstance(value, dict) or value.get('non_claim') is not True or value.get('session_id') != session_id
        or value.get('schema_version') != 'joulewise.bytes_h_' + name + '.v1' or not value.get('derivation')):
        flags.append({'code': 'records.receipt_unusable', 'path': str(path)})
        return {}
    return mapping(value.get('values'))


def measurements(state, export_csv):
    """Extract every v1 field; unavailable observations stay null with flags."""
    session, measurement = Path(state['session_root']), Path(state['measurement_root'])
    archive = session / 'archive'
    night_plan = read(state['plan_path'])
    custody = Path(night_plan['custody_root'])
    flags, sources = [], {}

    def unavailable(path):
        flags.append({'code': 'records.measurement_source_unreadable', 'path': str(path)})

    def journal(path):
        path = Path(path)
        try:
            if path.is_file() or Path(str(path) + '.zst').is_file():
                sources[str(path)] = locator(path)
            result = rows(path)
        except (OSError, ValueError):
            unavailable(path)
            return []
        if any(not isinstance(r, dict) for r in result):
            unavailable(path)
            return []
        return result

    def object_source(path):
        if path is None:
            return {}
        try:
            value = read(path)
            if Path(path).is_file() or Path(str(path) + '.zst').is_file():
                sources[str(path)] = locator(path)
            if isinstance(value, dict):
                return value
        except (OSError, ValueError):
            pass
        unavailable(path)
        return {}

    run_clock = journal(custody / 'collection/run_clock.jsonl')
    pairs = defaultdict(dict)
    for row in run_clock:
        ids = row.get('unit_run_ids')
        if not isinstance(ids, (list, tuple)):
            ids = [row.get('run_id')]
        for rid in ids:
            if isinstance(rid, str) and rid and row.get('event') in ('start', 'end'):
                pairs[rid][row['event']] = mapping(row.get('clock'))
    contention = journal(custody / 'hazards/monitor/contention.jsonl')
    thermal = journal(custody / 'hazards/monitor/thermal.jsonl')
    clocks = journal(custody / 'hazards/monitor/clock.jsonl')
    stages = journal(custody / 'night/chain-stages.jsonl')
    with Path(export_csv).open(newline='') as stream:
        exported = list(csv.DictReader(stream))
    sources[str(export_csv)] = locator(export_csv)
    sidecar_path = Path(str(export_csv).removesuffix('.runs.csv') + '.session.json')
    sidecar = read(sidecar_path)
    session_id = sidecar['session_id']
    if (sidecar.get('non_claim') is not True or session_id != state['inputs']['bracket_session_id']
        or not exported or any(r['non_claim'] != 'True' or r['session_id'] != session_id
                              or r['pack_id'] != PACK_ID for r in exported)):
        raise ValueError('foreign or claim export supplied to BYTES H')
    sources[str(sidecar_path)] = locator(sidecar_path)
    tree = read(measurement / KIT / 'plan_tree.json')
    kit = read(measurement / KIT / 'collection_plan.json')
    by_model = {m['run_id']: m['model_id'] for m in kit['members']}
    result = {'schema_version': 'joulewise.bytes_mac_measurements.v1', 'non_claim': True,
              'session_id': session_id, 'runs': {}, 'regimes': {},
              'clock': {}, 'cpu_contention': {}, 'disk': {}, 'sizing': {}}
    per_stage = defaultdict(list)
    bundle_dirs, seen = [], set()
    rate_observations = []
    for row in exported:
        rid = row['run_id']
        pair = pairs[rid]
        begin, end = pair.get('start', {}), pair.get('end', {})
        raw = [Path(p) / rid for p in state['runs_roots'].values()]
        bundle = bundle_of(archive, night_plan, rid)
        paths = [p for p in [*raw, bundle] if p and p.is_dir()]
        bundle_dirs.extend(paths)
        try:
            retained = sum(disk_bytes(p, seen=seen) for p in paths)
        except OSError:
            retained = None
            unavailable('bundle disk usage: ' + rid)
        events = journal(bundle / 'events.jsonl') if bundle else []
        meta_path = bundle / 'metadata.json' if bundle else None
        metadata = object_source(meta_path)
        wall = interval(begin.get('wall_s'), end.get('wall_s'))
        request = event_duration(events, 'sampling_started', 'sampling_stopped')
        stream = clock_span(metadata)
        a, b = begin.get('monotonic_ns'), end.get('monotonic_ns')
        cpu, k, level = None, None, None
        request_span = member_spans(metadata, events).get('request')
        if request_span and request_span[1] > request_span[0]:
            cpu, k = cpu_overlap(contention, *request_span)
        if type(a) is int and type(b) is int and b > a:
            levels = []
            for t in thermal:
                span = journal_span(t)
                value = mapping(t.get('values')).get('level')
                if span and a <= span[1] and span[0] <= b and type(value) is int and not t.get('error'):
                    levels.append(value)
            level = max(levels) if levels else None
            selected = [r for r in clocks if (span := journal_span(r)) and a <= span[1] and span[0] <= b]
            fit = fitted_clock(selected)
            if fit is not None:
                rate_observations.append({'run_id': rid, 'samples': len(selected), **fit})
        result['runs'][rid] = {'request_s': request, 'member_wall_s': wall, 'stream_s': stream,
            'retained_bytes': retained, 'thermal_level': level, 'outside_cpu_s': cpu, 'census_quanta': k}
        if wall is not None:
            per_stage[row['stage_id']].append((begin['wall_s'], end['wall_s']))
    frequencies = [v['frequency']['raw_word'] / FREQUENCY_SCALE for r in clocks
                   if not r.get('error') and isinstance((v := mapping(r.get('values'))).get('frequency'), dict)
                   and type(v['frequency'].get('raw_word')) is int]
    selected_rate = max(rate_observations, key=lambda v: abs(v['rate_ppm']), default={})
    result['clock'] = {'rate_ppm': selected_rate.get('rate_ppm'),
        'rate_member_span_s': selected_rate.get('span_s'), 'rate_member_n': selected_rate.get('n'),
        'rate_standard_error_ppm': selected_rate.get('standard_error_ppm'),
        'frequency_word_ppm': max(frequencies, key=abs, default=None)}
    result['cpu_contention'] = {k: None for k in ('w_j_per_cpu_s', 'c_q_cpu_s')}
    result['cpu_contention'].update({k: v for k, v in receipt(session, 'cpu_contention', session_id, sources, flags).items()
                                     if k in result['cpu_contention']})
    regime_receipts = receipt(session, 'regimes', session_id, sources, flags)
    for model in sorted(set(by_model.values()) - {'reference'}):
        observed = mapping(regime_receipts.get(model))
        result['regimes'][model] = {k: observed.get(k) for k in ('F_min_j', 'census_resolution_w', 'outside_power_w')}
        result['regimes'][model].update(operative_bound_s=sidecar.get('operative_bound_s'),
                                       registered_T10_s=None, registered_T_phase_s=None)
    collection_rows = [s for s in stages if s.get('kind') == 'campaign_collection']
    overheads = []
    for s in collection_rows:
        spans = per_stage[s['stage_id']]
        total = interval(s.get('started_epoch_s'), s.get('ended_epoch_s'))
        if spans and total is not None and all(s['started_epoch_s'] <= a <= b < s['ended_epoch_s'] + 1 for a, b in spans):
            overhead = total - union_seconds(spans)
            if overhead >= 0: overheads.append(overhead)
    expected = [s for s in chain.stage_plan(tree)]
    fixed_ids = {s.stage_id for s in expected if s.kind != 'campaign_collection'}
    fixed_rows = [s for s in stages if s.get('kind') != 'campaign_collection']
    timed_fixed = [s for s in fixed_rows
                   if interval(s.get('started_epoch_s'), s.get('ended_epoch_s')) is not None]
    complete_fixed = fixed_ids <= {s.get('stage_id') for s in timed_fixed}
    fixed_spans = [(s['started_epoch_s'], s['ended_epoch_s']) for s in timed_fixed]
    # No pilot/fixed estimates enter this measured file. Missing backup or
    # post-harvest verdict timestamps leave fixed_desk_s unobserved.
    result['sizing'] = {'fixed_desk_s': union_seconds(fixed_spans) if complete_fixed else None,
        'collection_stage_overhead_s': sum(overheads) / len(overheads)
        if len(overheads) == len([s for s in expected if s.kind == 'campaign_collection']) else None}
    arm_path = custody / 'hazards/arm.json'
    arm = object_source(arm_path)
    free_readings = [t['free_bytes'] for r in arm.get('hazards', {}).get('disk', [])
        if not (r.get('measurement') or {}).get('error')
        for t in (r.get('measurement') or {}).get('values', {}).get('targets', [])
        if not t.get('error') and type(t.get('free_bytes')) is int]
    backup_dirs = [session / name for name in ('backup-claim', 'backup-bound')]
    try:
        fixed_retained = disk_bytes(session, excluded=[*bundle_dirs, *backup_dirs], seen=seen)
    except OSError:
        fixed_retained = None
        unavailable('fixed session disk usage')
    try:
        backup_retained = sum(disk_bytes(p, seen=seen) for p in backup_dirs)
    except OSError:
        backup_retained = None
        unavailable('backup disk usage')
    result['disk'] = {'pre_arm_free_bytes': min(free_readings, default=None),
                      'fixed_retained_bytes': fixed_retained, 'backup_retained_bytes': backup_retained}
    for section in ('runs', 'regimes'):
        for key, value in result[section].items():
            for field, observed in value.items():
                if observed is not None and not numeric_receipt(observed):
                    value[field] = observed = None
                if observed is None:
                    flags.append({'code': 'records.measurement_unavailable', 'field': f'{section}.{key}.{field}'})
    for section in ('clock', 'cpu_contention', 'sizing', 'disk'):
        for field, value in result[section].items():
            if value is not None and not numeric_receipt(value):
                result[section][field] = value = None
            if value is None:
                flags.append({'code': 'records.measurement_unavailable', 'field': section + '.' + field})
    result.update(flags=flags, sources=sources, derivation={
        'request_s': 'native sampling_started to sampling_stopped event wall timestamps',
        'member_wall_s': 'collection/run_clock start/end pair, including preparation, reduction and sampler wind-down',
        'stream_s': 'native clock_anchor.clock_stamps pre_spawn.monotonic_before_s to post_parse.monotonic_after_s',
        'outside_cpu_s': 'sum of outside_total_cpu_s_per_s * native elapsed_s for whole census quanta overlapping the native member_spans request; never prorated; null on gaps or duplicates',
        'census_quanta': 'number of the same overlapping census intervals used for CPU seconds',
        'thermal_level': 'max observed native OS thermal level overlapping the member',
        'rate_ppm': 'worst signed per-member OLS slope of monitor anchor_ns against monotonic_raw_ns, multiplied by 1e6',
        'rate_member_span_s': 'last minus first admitted RAW-clock anchor of the member selected by largest absolute rate_ppm',
        'rate_member_n': 'number of admitted anchors in that same selected member fit',
        'rate_standard_error_ppm': 'single-fit noise model: independent uniform +/- WINDOW_SKEW_MAX_NS anchor error; SE = (WINDOW_SKEW_MAX_NS/sqrt(3))/sqrt(Sxx)*1e6, Sxx=sum((RAW_ns-mean_RAW_ns)^2). At 1 s monitor cadence Sxx~n*span_ns^2/12: about 0.27 ppm for a 150 s member with n~150 and the admitted 250000 ns skew limit. Actual admitted timestamps/count used; not empirical uncertainty or a multiplicity correction for worst-of-members selection; registered gate unchanged',
        'frequency_word_ppm': 'worst signed observed kernel raw_word / hazards.clock.FREQUENCY_SCALE',
        'retained_bytes': 'POSIX st_blocks*512 for raw and archive bundle trees, inode-deduplicated; disk usage at desk snapshot',
        'fixed_retained_bytes': 'remaining allocated session bytes, excluding per-run bundle subtrees and backup-claim/backup-bound',
        'backup_retained_bytes': 'POSIX st_blocks*512 for backup-claim and backup-bound trees, inode-deduplicated against raw/archive/fixed bytes at desk snapshot',
        'pre_arm_free_bytes': 'minimum observed native arm disk target free_bytes; null when no arm receipt exists; prepare snapshot is not substituted',
        'stage_timestamp_resolution': 'chain shell date +%s records integer seconds; member endpoints can occupy the final second bucket',
        'sizing': 'disjoint journal union for fixed work; mean(stage span - union member wall spans) for collection overhead; registered settles excluded',
        'regimes': 'optional session-bound floor/census derivation receipts; operative bound from native session sidecar; registered T10/T_phase absent',
        'cpu_contention': 'optional session-bound measured coefficient/quiet-quantum derivation receipt',
    }, clock_fit_observations=rate_observations,
        stage_timestamps=stages)
    return result


def window_allocation(state, *, statvfs=os.statvfs):
    """Whole session-volume drawdown, before harvest or any desk outputs."""
    session = Path(state['session_root'])
    flags = []
    try:
        disk = statvfs(session)
        free_at_desk = int(disk.f_bavail) * int(disk.f_frsize)
    except OSError:
        free_at_desk = None
        flags.append('disk.desk_free_unavailable')
    device = session.stat().st_dev
    custody = Path(read(state['plan_path'])['custody_root'])
    try:
        arm = read(custody / 'hazards/arm.json')
        targets = [t for row in arm.get('hazards', {}).get('disk', [])
                   if not (row.get('measurement') or {}).get('error')
                   for t in (row.get('measurement') or {}).get('values', {}).get('targets', [])
                   if not t.get('error') and t.get('device') == device and type(t.get('free_bytes')) is int]
        free_at_arm = min((t['free_bytes'] for t in targets), default=None)
    except (OSError, ValueError, AttributeError, TypeError):
        free_at_arm = None
    if free_at_arm is None:
        flags.append('disk.arm_free_unavailable')
    return {'free_at_arm_bytes': free_at_arm, 'free_at_desk_start_bytes': free_at_desk,
            'whole_window_allocation_bytes': free_at_arm - free_at_desk
                if free_at_arm is not None and free_at_desk is not None else None,
            'peak_copies': state['disk']['derivation']['peak_copies'],
            'required_free_bytes': state['disk']['required_free_bytes'],
            'arm_receipt': str(custody / 'hazards/arm.json'), 'device': device,
            'derivation': 'whole_window_allocation_bytes = free_at_arm_bytes - free_at_desk_start_bytes; session volume statvfs f_bavail*f_frsize; includes every writer; disclosure only',
            'flags': flags}


def desk(session_root, *, run=subprocess.run, statvfs=os.statvfs):
    session = Path(session_root).resolve()
    state = read(session / 'session.json')
    custody = Path(read(state['plan_path'])['custody_root'])
    if not (custody / 'night/result.json').is_file():
        raise ValueError('terminal record is required before desk')
    allocation = window_allocation(state, statvfs=statvfs)
    print('disk_window_allocation: ' + json.dumps(allocation, sort_keys=True))
    measurement = Path(state['measurement_root'])
    argv = [str(measurement / '.venv/bin/python'), str(measurement / 'scripts/harvest_b6_session.py'),
        '--plan', state['plan_path'], '--archive-root', str(session / 'archive'),
        '--registration-dir', state['registration_dir'], '--pack-records-root', str(session / 'private'),
        '--export-dir', str(session / 'export'), '--non-claim']
    result = run(argv, check=False, capture_output=True, text=True, timeout=HARVEST_TIMEOUT_S)
    (session / 'staging/harvest.stdout').write_text(result.stdout or '')
    (session / 'staging/harvest.stderr').write_text(result.stderr or '')
    if result.returncode not in (0, 6):
        raise RuntimeError('harvest program fault: exit ' + str(result.returncode))
    native = json.loads(result.stdout.strip().splitlines()[-1])['export']
    export_csv = Path(native['csv'])
    measured = measurements(state, export_csv)
    gate_argv = [str(measurement / '.venv/bin/python'), str(measurement / 'scripts/bytes_gates.py'),
        '--runs', str(export_csv), '--measurements', str(session / 'MEASUREMENTS.json'),
        '--kit-plan', str(measurement / KIT / 'collection_plan.json'), '--out', str(session / 'C5.json')]
    # Include the desk's own retained outputs in fixed disk usage. Re-evaluate
    # only when that integer byte count changes; allocation converges once the
    # JSON/log files occupy their final filesystem blocks. The final C5 hashes
    # then name exactly the final MEASUREMENTS bytes.
    while True:
        write(session / 'MEASUREMENTS.json', measured)
        gates = run(gate_argv, check=False, capture_output=True, text=True, timeout=HARVEST_TIMEOUT_S)
        (session / 'staging/gates.stdout').write_text(gates.stdout or '')
        (session / 'staging/gates.stderr').write_text(gates.stderr or '')
        status = {'schema_version': 'joulewise.bytes_h_desk.v1', 'non_claim': True,
            'session_id': measured['session_id'], 'plan_id': state['session_id'],
            'harvest_argv': argv, 'harvest_exit': result.returncode,
            'gates_argv': gate_argv, 'gates_exit': gates.returncode,
            'measurements': str(session / 'MEASUREMENTS.json'), 'export': native,
            'status': 'unavailable' if gates.returncode == 1 else 'fail' if gates.returncode == 2
                      else 'pass' if gates.returncode == 0 else 'program_fault',
            'flags': measured['flags'], 'registration_ready': False, 'disk': allocation}
        write(session / 'desk.json', status)
        refreshed = measurements(state, export_csv)
        if refreshed['disk']['fixed_retained_bytes'] == measured['disk']['fixed_retained_bytes']:
            break
        measured = refreshed
    print('harvest_exit: ' + str(result.returncode))
    print('MEASUREMENTS: ' + str(session / 'MEASUREMENTS.json'))
    print((gates.stdout or gates.stderr or '').strip())
    print('gates_exit: ' + str(gates.returncode))
    return status


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('prepare')
    p.add_argument('--measurement-root', type=Path, required=True)
    p.add_argument('--session-root', type=Path, required=True)
    for name in ('install', 'desk'):
        commands.add_parser(name).add_argument('--session-root', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'prepare':
            prepare(args.measurement_root, args.session_root)
        elif args.command == 'install':
            install(args.session_root)
        else:
            status = desk(args.session_root)
            return status['gates_exit']
        return 0
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print('bytes_h_session: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
