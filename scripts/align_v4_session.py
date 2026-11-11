#!/usr/bin/env python3
"""Guarded v4 session with prospective registration and thermal desk checks.

prepare refuses until the kit is W1-ready (inputs, D identity, R1-derived
sizing_b5.json, WP18 fixtures, signed registration receipt) and writes the frozen series AC powermode into
the night plan. install additionally requires the AC powermode to equal the
frozen series value, completed battery top-up/OBC attestation, current disk
floor and a fresh daytime offload receipt. Under an adopted
High Power (r1_slots ac_powermode 2, lead ruling R5-6) install sets
powermode 2 through the narrow sudo rule after writing the host-level High
Power marker (lead ruling R6-7), and restores Automatic if the arm refuses or
the installer installs nothing; run_night admits 2 only for a plan that
declares 2 and restores Automatic when that night closes. Every session start
(prepare, install) first restores a marker it does not own, never while a
measuring night holds the host night lock.
"""
from contextvars import ContextVar
from functools import wraps
import json
import os
from pathlib import Path
import plistlib
import re
import signal
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise import timing_receipts
from scripts import align_pilot_session as pilot, align_v4_kit as kit


def series_ac_powermode(measurement_root, kit_path=kit.KIT):
    """The R1-frozen series AC powermode the generated collection plan carries."""
    plan = json.loads((Path(measurement_root) / kit_path / 'collection_plan.json').read_bytes())
    value = (plan.get('runtime_requirements') or {}).get('ac_powermode')
    if type(value) is not int or value not in (0, 2):
        raise ValueError(f'v4 collection plan freezes no series AC powermode (got {value!r})')
    return value


def prepare(measurement_root, session_root, *, power_runner=None, window_id=None, extra_sentinels=0,
            frequency_reader=None, frequency_runner=None, frequency_preflight=None, weight_identity_fn=None, **kwargs):
    from joulewise.align.apple import powermode
    preflight = powermode.host_lock_preflight(role='v4-prepare-preflight')
    # Lead ruling R6-7: at every session start a host-level High Power marker
    # means an Automatic restore is owed. Restore it first (never under a
    # measuring night, which holds the host night lock and restores at its own
    # close) and refuse the session if the restore fails its read-back.
    start = session_start_restore(measurement_root, runner=power_runner)
    kit.generate(measurement_root, check=True, source_root=measurement_root)
    series_state = None
    if extra_sentinels not in (0, 2) or (extra_sentinels and window_id in (None, 'W1')):
        raise ValueError('escalation sentinels (R20) apply to a C/T window after a U4-inconclusive window only')
    if window_id is not None:
        from scripts import align_v4_series as series
        manifest = series.load(measurement_root)
        selected = series.selected(manifest, window_id)
        series.require_admission(measurement_root, manifest, post_w1=selected['id'] != 'W1')
        if selected['id'] != 'W1':
            series.generate(measurement_root, window_id, check=True, extra_sentinels=extra_sentinels)
            kwargs.update(kit=series.kit_path(selected['id']), pack_id=series.pack_id(selected['id']))
        series_state = dict(window_id=selected['id'], role=selected['role'], extra_sentinels=extra_sentinels,
            manifest_sha256=kit.sha((Path(measurement_root) / series.MANIFEST).read_bytes()),
            admission_sha256=kit.sha((Path(measurement_root) / series.ADMISSION).read_bytes()))
    # Lead ruling R5-6: the night plan declares the frozen series powermode, so
    # run_night admits a High Power host only for a W1 that adopted it.
    kwargs.setdefault('ac_powermode', series_ac_powermode(measurement_root, kwargs.get('kit', kit.KIT)))
    kwargs.setdefault('kit', kit.KIT)
    kwargs.setdefault('pack_id', kit.PACK_ID)
    kwargs.setdefault('session_prefix', 'align-v4-')
    try:
        state = pilot.prepare(measurement_root, session_root, **kwargs)
    except (pilot.h.PhysicalHazard, KeyError, OSError) as exc:
        # The shared caller's presence check precedes plan staging. A missing
        # shard/row or unreadable tree must still get RL-62's named refusal.
        # Never overwrite an existing session or replace another physical gate.
        if isinstance(exc, pilot.h.PhysicalHazard) and not str(exc).startswith('models missing:'):
            raise
        session = Path(session_root)
        if session.exists() and any(session.iterdir()):
            raise
        state = {'measurement_root': str(measurement_root), 'preparation_status': 'INPUTS_ONLY',
                 'registration_dir': str(Path(measurement_root) / kwargs['kit'] / 'registration'),
                 'host_state_preflight': preflight}
        weights = weight_digest_preflight(state, identity_fn=weight_identity_fn)
        if weights['ok']:
            raise
        state['weight_digest_preflight'] = weights
        pilot.h.write(session / 'session.json', state)
        raise ValueError('; '.join(weights['reasons'])) from exc
    state['host_state_preflight'] = preflight
    privileges = (host_privilege_preflight(runner=power_runner) if powermode.host_state_override() is None
                  else {'ok': True, 'skipped': 'host-state test override', 'reasons': []})
    state['host_privilege_preflight'] = privileges
    if series_state is not None and state.get('preparation_status') == 'STAGED':
        # Preserve the selected window even when the following preflight
        # refuses; a later install must still bind the correct frozen series.
        state['v4_series'] = series_state
    # The prepared plan supplies the actual stream span and registered budget.
    # A second, fresh check at install owns any intervening network-time ON.
    frequency = None
    weights = None
    if privileges['ok'] and state.get('preparation_status') == 'STAGED':
        # RL-62: prepare stages the plan; it never calls arm_checks or its
        # pre_dwell/stamp. Hashing ends here, long before that install path.
        weights = state['weight_digest_preflight'] = weight_digest_preflight(state, identity_fn=weight_identity_fn)
    if privileges['ok'] and (weights is None or weights['ok']) and state.get('preparation_status') == 'STAGED':
        lock = powermode.HostLock(role='v4-prepare-frequency')
        try:
            if not lock.acquire():
                raise ValueError('clock.frequency_word_nonzero: another night holds the host night lock')
            frequency = (frequency_preflight or frequency_word_preflight)(
                state, reader=frequency_reader, runner=frequency_runner or power_runner)
        finally:
            lock.release()
        state['clock_frequency_preflight'] = frequency
    pilot.h.write(Path(session_root) / 'session.json', state)
    if not privileges['ok']:
        raise ValueError('; '.join(privileges['reasons']))
    if weights is not None and not weights['ok']:
        raise ValueError('; '.join(weights['reasons']))
    if frequency is not None and not frequency['ok']:
        raise ValueError(f"{frequency['cause']}: {frequency['reason']}")
    if series_state is not None:
        if state.get('preparation_status') != 'STAGED':
            raise ValueError('series prepare produced no armable plan; inspect session flags')
    if start['action'] != 'none':
        try:
            pilot.h.write(Path(session_root) / f'staging/v4-session-start-restore-{time.time_ns()}.json', start)
        except Exception:  # noqa: BLE001 - the restore itself is what matters
            pass
    return state


def _registered_weight_roots(state, *, members=None):
    """Use the kit's existing unit IDs; never resolve or inspect model paths."""
    # Same selected registration as _member_rows and bytes_h_session.prepare:
    # W1 uses align_v4/registration; series kits project the registered units
    # with _identities for their own member run IDs (align_v4_series:418-429).
    directory = Path(state.get('registration_dir', Path(state['measurement_root']) / kit.KIT / 'registration'))
    inventory = pilot.h.read(directory / 'model_artifact_inventory.json')['artifacts']
    rows = pilot._member_rows(state, kit=kit.KIT) if members is None else members
    units = sorted({pilot.h.align_unit_id(row['model_id'], row['run_id']) for row in rows})
    groups, reasons = {}, []
    for unit in units:
        row = inventory.get(unit)
        if not isinstance(row, dict) or not isinstance(row.get('root'), str) or not row['root']:
            reasons.append(f'weight_digest_preflight: no_inventory_row: {unit}')
        else:
            groups.setdefault(row['root'], {})[unit] = row
    return dict(sorted(groups.items())), reasons


def weight_digest_preflight(state, *, identity_fn=None):
    """RL-62: the R0 identity function, once per planned root, at prepare only."""
    from joulewise.provenance import model_artifact_identity
    record = {'source': 'prepare', 'prepared_at_epoch_s': time.time(), 'roots': {}, 'ok': False, 'reasons': []}
    try:
        groups, record['reasons'] = _registered_weight_roots(state)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        record['reasons'].append(f'weight_digest_preflight: unavailable: model_artifact_inventory.json: '
                                 f'{type(exc).__name__}: {exc}')
        return record
    for root, units in groups.items():
        basename = Path(root).name
        started = time.monotonic()
        try:
            observed = (identity_fn or model_artifact_identity)(root)
        except (OSError, ValueError, RuntimeError) as exc:
            observed = {'status': 'unavailable', 'reason': f'{type(exc).__name__}: {exc}'}
        entry = record['roots'][root] = {
            'units': list(units), 'registered_folded_sha256': next(iter(units.values())).get('folded_sha256'),
            'observed_folded_sha256': observed.get('folded_sha256'),
            'file_count': len(observed.get('files') or {}),
            'total_bytes': sum(row['size_bytes'] for row in observed.get('inventory', [])),
            'elapsed_s': time.monotonic() - started, 'ok': False}
        reasons = []
        if observed.get('status') != 'ok' or observed.get('kind') != 'file_set':
            reason = observed.get('reason') or 'identity must be an ok file_set'
            reasons.append(f'weight_digest_preflight: unavailable: {basename}: {reason}')
        else:
            added, missing, changed = set(), set(), set()
            for unit, registered in units.items():
                expected = registered.get('folded_sha256')
                if not kit.valid_digest(expected) or observed.get('folded_sha256') != expected:
                    reasons.append(f'weight_digest_preflight: digest_mismatch: {unit} {basename}')
                expected_files, found_files = registered.get('files'), observed.get('files')
                if not isinstance(expected_files, dict) or not isinstance(found_files, dict):
                    reasons.append(f'weight_digest_preflight: unavailable: {basename}: file map unavailable')
                elif expected_files != found_files:
                    added.update(found_files.keys() - expected_files.keys())
                    missing.update(expected_files.keys() - found_files.keys())
                    changed.update(name for name in expected_files.keys() & found_files.keys()
                                   if expected_files[name] != found_files[name])
            if added or missing or changed:
                entry['file_set_diff'] = dict(added=sorted(added), missing=sorted(missing), changed=sorted(changed))
                reasons.append(f'weight_digest_preflight: file_set_differs: {basename}')
        entry['ok'] = not reasons
        record['reasons'].extend(dict.fromkeys(reasons))
    record['ok'] = not record['reasons']
    return record


def _attested_weight_digests(state, members, path):
    """Read a named operator's digest pairs, without touching any model tree."""
    record = {'source': 'attested', 'roots': {}, 'ok': False, 'reasons': []}
    try:
        document = pilot.h.read(path)
        record.update(attested_by=document.get('attested_by'),
                      attested_at_epoch_s=document.get('attested_at_epoch_s'), roots=document.get('roots'))
        if not isinstance(record['attested_by'], str) or not record['attested_by'].strip():
            raise ValueError('attested_by must name the operator')
        if not isinstance(record['roots'], dict):
            raise ValueError('roots must map each planned root to its registered and observed folded_sha256')
        groups, record['reasons'] = _registered_weight_roots(state, members=members)
        if set(record['roots']) != set(groups):
            raise ValueError('attested roots must equal the planned registered roots')
        for root, units in groups.items():
            pair = record['roots'][root]
            for unit, registered in units.items():
                expected = registered.get('folded_sha256')
                if (not kit.valid_digest(expected) or not isinstance(pair, dict)
                        or pair.get('registered_folded_sha256') != expected
                        or pair.get('observed_folded_sha256') != expected):
                    record['reasons'].append(f'weight_digest_preflight: digest_mismatch: {unit} {Path(root).name}')
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        record['reasons'].append(f'weight_digest_preflight: unavailable: attestation: {type(exc).__name__}: {exc}')
    record['ok'] = not record['reasons']
    return record


# Fixed, root-owned native executable; no Python interpreter or writable repo
# script is ever granted root. Provisioning and the exact sudoers rule are in
# the round-3 report. This command accepts NO arguments.
ZERO_FREQUENCY_ARGV = ('/usr/bin/sudo', '-n', '/Library/PrivilegedHelperTools/joulewise-zero-ntp-frequency')
FREQUENCY_CAUSE = 'clock.frequency_word_nonzero'


def host_privilege_rules():
    """The night's fixed sudo rules, from their owning constants, never setters here."""
    from joulewise import network_time_off
    from joulewise.align.apple import powermode
    from joulewise.b5 import driver
    from scripts import run_night
    # driver.NETWORK_TIME_OFF_ARGV and network_time_off.OFF_ARGV are the same
    # rule; retain both sources without issuing duplicate listings.
    rules = [('network_time_off', driver.NETWORK_TIME_OFF_ARGV),
             ('network_time_off_receipt', network_time_off.OFF_ARGV),
             ('network_time_on', run_night.NETWORK_TIME_ON_ARGV),
             ('network_time_query', run_night.NETWORK_TIME_QUERY_ARGV),
             ('powermode_automatic', powermode.RESTORE_AUTOMATIC),
             ('powermode_high', powermode.SET_HIGH_POWER),
             ('zero_ntp_frequency', ZERO_FREQUENCY_ARGV)]
    seen, unique = set(), []
    for name, argv in rules:
        command = tuple(argv[2:])
        if command not in seen:
            seen.add(command)
            unique.append((name, argv))
    return unique


def _stored_streams(result):
    """Bound staging evidence to 8 KiB per UTF-8 stream; parse the full output."""
    evidence = {}
    for name in ('stdout', 'stderr'):
        raw = (getattr(result, name) or '').encode('utf-8')
        evidence[name] = raw[:8192].decode('utf-8', errors='ignore')
        evidence[name + '_truncated'] = len(raw) > 8192
    return evidence


def host_privilege_preflight(*, runner=None):
    """W-2: LIST permissions, then reuse the night's read-only network-time reader."""
    from types import SimpleNamespace
    from scripts import run_night
    record = {'ok': False, 'rules': {}, 'network_time': None, 'reasons': []}

    def run(argv):
        return (runner(argv) if runner is not None else subprocess.run(
            argv, check=False, capture_output=True, text=True, timeout=10))

    for name, command in host_privilege_rules():
        argv = ('/usr/bin/sudo', '-n', '-l', *command[2:])
        evidence = record['rules'][name] = {'argv': list(argv), 'allowed': False}
        try:
            result = run(argv)
            evidence.update(exit_code=result.returncode, **_stored_streams(result),
                            allowed=result.returncode == 0)
        except (OSError, subprocess.SubprocessError) as exc:
            evidence['error'] = f'{type(exc).__name__}: {exc}'
        if not evidence['allowed']:
            record['reasons'].append(f'host_privilege_preflight: sudo_rule_missing: {name}')

    def query(argv):
        result = run(argv)
        return SimpleNamespace(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)

    # Do not execute even the query unless its sudo rule was admitted above.
    if record['rules']['network_time_query']['allowed']:
        record['network_time'] = run_night._leave_network_time(SimpleNamespace(run=query), skipped=False)
    if not (record['network_time'] or {}).get('verified'):
        record['reasons'].append('host_privilege_preflight: network_time_unreadable')
    record['ok'] = not record['reasons']
    return record


# Three supervisor polls, equal to the shortest standdown phase gap (30 s).
# magistrate_watchdog.py:99-104, 128, 440, 504: the process/remote probes
# each allow 10 s; 30 s allows both remote transports plus one local probe.
WATCHDOG_TIMEOUT_S = 30
WATCHDOG_PLAN_LEAD_S = 180  # magistrate_watchdog.py:104, plan_span_active:1328
# Closed output vocabulary: Decision constructors (_decide:2197-2408,
# _surface_unsafe_decision:2563), _unsafe_state:2411-2434, computed
# STANDDOWN phases:1444-1451/BACKOFF:2400-2405, supervisor IDLE:2887.
WATCHDOG_STATES = frozenset({
    'ACTIVE', 'FENCED', 'LAUNCHING', 'IDLE', 'BACKOFF', 'BACKOFF_USAGE', 'STOPPED',
    'STANDDOWN_REQUEST', 'STANDDOWN_TERM', 'STANDDOWN_KILL',
    'CLOCK_UNCERTAIN', 'NETWORK_UNCERTAIN', 'STRANDED', 'HOLD_CENSUS', 'HOLD_UNSAFE',
    'HOLD_PLAN_UNREADABLE', 'HOLD_PLAN_MALFORMED', 'HOLD_PLIST_UNREADABLE', 'HOLD_CONFLICT',
    'HOLD_LOCK', 'HOLD_PROCESS_TABLE', 'HOLD_DESK_FENCE', 'HOLD_STATUS_EXPORT',
    'HOLD_MODEL_CHECK', 'HOLD_MODEL_REJECTED'})
WATCHDOG_ADMITTED = frozenset({'FENCED', 'ACTIVE', 'LAUNCHING', 'IDLE', 'BACKOFF', 'BACKOFF_USAGE', 'STOPPED',
                              'STANDDOWN_REQUEST', 'STANDDOWN_TERM', 'STANDDOWN_KILL'})
# Installed-module API: Storage:311-344, PlanSnapshot:654-657,
# load_plans:757-818 and _installed_agent_plans:820-873 only read files.
# plan_span_active:1328 uses t0 - PLAN_LEAD_S (:104); standdown_phase:1444-1451
# uses REQUEST/TERM/KILL leads, not the span boundary. No main()/tick() here.
WATCHDOG_DISCOVERY_PROGRAM = '''import importlib.util, json, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("_arm_watchdog_discovery", sys.argv[1])
watchdog = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = watchdog
spec.loader.exec_module(watchdog)
storage = watchdog.Storage(Path(sys.argv[2]), dry_run=True)
snapshot = watchdog.load_plans(storage)
assert storage.dry_run and not storage.would_write, "plan discovery attempted a write"
print(json.dumps({"plans": [{"plan_id": p.plan_id, "t0_epoch_s": p.t0_epoch_s,
    "span_start_epoch_s": p.t0_epoch_s - watchdog.PLAN_LEAD_S} for p in snapshot.plans],
    "errors_count": len(snapshot.errors), "installed_source": "not_distinguishable"}))
'''


# Mirror ONLY load_plans' scanned-plan steps (magistrate_watchdog.py:765-805):
# read/JSON -> retired-v1 -> installed NightPlan -> authored time -> deadman.
# No main()/tick(), writes or host probes. The scan is informational here.
WATCHDOG_PLAN_FILE_PROGRAM = '''import importlib.util, json, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("_arm_watchdog_discovery", sys.argv[1])
watchdog = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = watchdog
spec.loader.exec_module(watchdog)
storage = watchdog.Storage(Path(sys.argv[2]), dry_run=True)
path = Path(sys.argv[3])
now = watchdog.time.time()
def parse():
    try:
        text = storage.read_text(path)
    except OSError as exc:
        return {"parse": "unreadable", "exception": type(exc).__name__}
    try:
        raw = watchdog.json.loads(text)
    except Exception as exc:
        return {"parse": "unreadable", "exception": type(exc).__name__}
    if watchdog.is_retired_v1_plan(raw):
        return {"parse": "retired_v1"}
    try:
        plan = watchdog.NightPlan.from_mapping(raw)
        if plan.authored_epoch_s > now:
            raise watchdog.PlanError("night_plan_malformed", "plan authored_epoch_s is in the future")
        watchdog.deadman_epoch(plan)
    except (watchdog.PlanError, OverflowError, ValueError) as exc:
        return {"parse": "malformed", "exception": type(exc).__name__}
    return {"parse": "ok", "plan_id": plan.plan_id, "t0_epoch_s": plan.t0_epoch_s,
            "span_start_epoch_s": plan.t0_epoch_s - watchdog.PLAN_LEAD_S}
result = parse()
snapshot = watchdog.load_plans(storage, now_epoch_s=now)
result["discovered_by_scan"] = (result["parse"] == "ok"
    and path.resolve(strict=False) in [p.resolve(strict=False) for p in storage.glob_plans()]
    and any(p.plan_id == result["plan_id"] and p.t0_epoch_s == result["t0_epoch_s"] for p in snapshot.plans))
assert storage.dry_run and not storage.would_write, "plan identification attempted a write"
print(json.dumps(result))
'''


def watchdog_acceptance(*, phase, runner=None, plist_path=None, plan=None, plan_path=None, now=None, deadline_ns=None):
    """W-1: run only the installed watchdog's read-only command, fail closed.

    Parse this plan directly before install; discover it after install (RL-56).
    Before its span, ordinary idle/launch/backoff states admit too; at/after
    its span boundary only FENCED/STANDDOWN admit. Both runs share one deadline.
    """
    started = time.monotonic_ns()
    deadline_ns = started + WATCHDOG_TIMEOUT_S * 1_000_000_000 if deadline_ns is None else deadline_ns
    record = {'ok': False, 'argv': None, 'state': 'UNAVAILABLE', 'reason': None,
              'plan_read_proven': False, 'stopped': False}
    try:
        path = Path(plist_path) if plist_path is not None else Path.home() / 'Library/LaunchAgents/com.joulewise.magistrate.plist'
        document = plistlib.loads(path.read_bytes())
        argv = document['ProgramArguments']
        cwd = document['WorkingDirectory']
        environment = document['EnvironmentVariables']
        if (document.get('Label') != 'com.joulewise.magistrate' or not isinstance(argv, list)
                or not all(isinstance(arg, str) and arg for arg in argv)
                or not argv or document.get('Program', argv[0]) != argv[0]
                or not isinstance(cwd, str) or not Path(cwd).is_absolute()
                or not isinstance(environment, dict)
                or not all(isinstance(k, str) and isinstance(v, str) for k, v in environment.items())):
            raise ValueError('invalid installed magistrate job')
        # Whitelist the production Python launch forms; never forward an
        # installed command/subcommand that might write or spawn a session.
        script = next(i for i, arg in enumerate(argv) if Path(arg).name == 'magistrate_watchdog.py')
        prefix = argv[:script]
        interpreter = prefix[1:] if prefix[:1] == ['/usr/bin/env'] else prefix
        if (not interpreter or not re.fullmatch(r'python3(?:\.[0-9]+)?', Path(interpreter[0]).name)
                or any(arg not in ('-B', '-u', '-s', '-S') for arg in interpreter[1:])
                or not Path(argv[script]).is_absolute()):
            raise ValueError('unsupported installed watchdog interpreter/script')
        tail = argv[script + 1:]
        if tail and (len(tail) != 2 or tail[0] != '--custody-root'):
            raise ValueError('unsupported installed watchdog arguments')
        custody = tail[1] if tail else environment.get('MAGISTRATE_WATCHDOG_CUSTODY_ROOT')
        if not isinstance(custody, str) or not Path(custody).is_absolute():
            raise ValueError('installed watchdog custody root unavailable')
        discovery_argv = argv[:script] + ['-c', WATCHDOG_DISCOVERY_PROGRAM, argv[script], custody]
        argv = argv[:script + 1] + ['--dry-run', '--custody-root', custody]
        record.update(argv=argv, cwd=cwd, custody_root=custody)
        environment = dict(os.environ, **environment)
        environment['PYTHONDONTWRITEBYTECODE'] = '1'  # module import is read-only too
        remaining = (deadline_ns - time.monotonic_ns()) / 1e9
        if remaining <= 0:
            raise TimeoutError('watchdog acceptance timeout')
        result = (runner or subprocess.run)(argv, cwd=cwd, env=environment,
            check=False, capture_output=True, text=True, timeout=remaining)
        record.update(exit_code=result.returncode, **_stored_streams(result))
        if result.returncode != 0:
            raise ValueError(f'installed watchdog exited {result.returncode}')
        lines = [line for line in (result.stdout or '').splitlines() if line.lstrip().startswith('decision=')]
        match = re.fullmatch(r'decision=([A-Z][A-Z0-9_]*) reason=(\S[^\r\n]*)', lines[0]) if len(lines) == 1 else None
        if match is None:
            raise ValueError('expected one well-formed decision= line')
        record.update(state=match[1], reason=match[2], stopped=match[1] == 'STOPPED')
        record['ok'] = (record['state'] in WATCHDOG_ADMITTED and not any(text in record['reason'] for text in
            ('night_plan_unreadable', 'night_plan_malformed', 'installed_agent_fence')))
        decision_ok = record['ok']
        if not decision_ok and phase != 'pre_install':
            return record
        identity = record['plan_identity'] = {'source': ('installed_parser_on_plan_file' if phase == 'pre_install'
            else 'installed_load_plans'), 'found': False, 'span_start_epoch_s': None, 'expected': None, 'ok': False}
        record['ok'] = False
        try:
            if (not isinstance(plan, dict) or not isinstance(plan.get('plan_id'), str) or not plan['plan_id']
                    or not pilot.h.finite(plan.get('t0_epoch_s'))):
                raise ValueError('arm plan identity unavailable')
            identity['expected'] = plan['t0_epoch_s'] - WATCHDOG_PLAN_LEAD_S
            if phase == 'pre_install':
                identity['discovered_by_scan'] = False
                if plan_path is None or not Path(plan_path).is_absolute():
                    raise ValueError('arm plan path must be absolute')
                discovery_argv = argv[:script] + ['-c', WATCHDOG_PLAN_FILE_PROGRAM,
                    argv[script], custody, str(plan_path)]
            remaining = (deadline_ns - time.monotonic_ns()) / 1e9
            if remaining <= 0:
                raise TimeoutError('watchdog acceptance timeout before discovery')
            discovery = record['discovery'] = {'argv': discovery_argv}
            found = (runner or subprocess.run)(discovery_argv, cwd=cwd, env=environment,
                check=False, capture_output=True, text=True, timeout=remaining)
            discovery['exit_code'] = found.returncode
            if found.returncode != 0:
                raise ValueError(f'installed discovery exited {found.returncode}')
            if time.monotonic_ns() > deadline_ns:
                raise TimeoutError('watchdog acceptance timeout after discovery')
            lines = (found.stdout or '').splitlines()
            snapshot = json.loads(lines[0]) if len(lines) == 1 else None
            if phase == 'pre_install':
                if (not isinstance(snapshot, dict) or snapshot.get('parse') not in
                        ('ok', 'retired_v1', 'unreadable', 'malformed')
                        or type(snapshot.get('discovered_by_scan')) is not bool):
                    raise ValueError('malformed parser snapshot')
                identity['discovered_by_scan'] = snapshot['discovered_by_scan']
                if snapshot['parse'] != 'ok':
                    record['reason'] = 'plan_identity: ' + snapshot['parse']
                    return record
                snapshot = {'plans': [{k: snapshot.get(k) for k in
                    ('plan_id', 't0_epoch_s', 'span_start_epoch_s')}],
                    'errors_count': 0, 'installed_source': 'not_distinguishable'}
            if (not isinstance(snapshot, dict) or not isinstance(snapshot.get('plans'), list)
                    or type(snapshot.get('errors_count')) is not int or snapshot['errors_count'] < 0
                    or snapshot.get('installed_source') not in ('installed', 'scanned', 'not_distinguishable')):
                raise ValueError('malformed discovery snapshot')
            discovery.update(errors_count=snapshot['errors_count'])
            record['installed_source'] = snapshot['installed_source']
            if snapshot['errors_count']:
                raise ValueError('discovery reported plan errors')
            for item in snapshot['plans']:
                if (not isinstance(item, dict) or set(item) != {'plan_id', 't0_epoch_s', 'span_start_epoch_s'}
                        or not isinstance(item['plan_id'], str) or not item['plan_id']
                        or not all(pilot.h.finite(item[k]) for k in ('t0_epoch_s', 'span_start_epoch_s'))):
                    raise ValueError('malformed discovered plan')
            matches = [item for item in snapshot['plans'] if item['plan_id'] == plan['plan_id']]
            identity['found'] = bool(matches)
            if len(matches) != 1:
                raise ValueError('arm plan missing or ambiguous')
            identity['span_start_epoch_s'] = matches[0]['span_start_epoch_s']
            if matches[0]['span_start_epoch_s'] != identity['expected'] or matches[0]['t0_epoch_s'] != plan['t0_epoch_s']:
                raise ValueError('arm plan span start mismatch')
            if phase == 'post_install' and snapshot['installed_source'] == 'scanned':
                raise ValueError('arm plan not discovered through installed plist')
            identity['ok'] = record['plan_read_proven'] = True
            record['ok'] = decision_ok
        except Exception as exc:
            record['reason'] = f'plan_identity: {type(exc).__name__}: {exc}'
        if record['ok'] and (now or time.time)() >= identity['expected']:
            if record['state'] != 'FENCED' and not record['state'].startswith('STANDDOWN_'):
                record.update(ok=False, reason='inside plan span without a fence')
    except Exception as exc:  # malformed plist/encoding or any failed read/run is a refusal
        record['ok'] = False
        record['reason'] = f'{type(exc).__name__}: {exc}'
    finally:
        record['elapsed_s'] = (time.monotonic_ns() - started) / 1e9
    return record


def _watchdog_refusal(phase, record):
    if record['reason'].startswith('plan_identity:'):
        return f"watchdog_acceptance: {phase}: {record['reason']}"
    return f"watchdog_acceptance: {phase}: {record['state']}: {record['reason']}"


def frequency_word_preflight(state, *, reader=None, runner=None):
    """Project a fresh kernel word through this arm's unchanged clock budget.

    Caller holds HostLock. The launchd census must prove no night installed
    before changing host state. Every passing arm authenticates network time
    OFF; a failing projection also requires OFF before zeroing the word. All failures retain evidence
    and refuse before the shared installer. This is preparation, not a
    replacement for the hazard's measured-rate/dwell gates or OFF receipt.
    """
    from joulewise import kernel_clock, network_time_off
    from joulewise.hazards import clock
    record = {'ok': False, 'cause': FREQUENCY_CAUSE, 'action': 'refused',
              'before': None, 'after': None, 'commands': [],
              'next_arm_owns_zeroing': True}

    def command(argv):
        evidence = {'argv': list(argv)}
        record['commands'].append(evidence)
        try:
            result = (runner(argv) if runner is not None else subprocess.run(
                argv, check=False, capture_output=True, text=True, timeout=10))
            evidence.update(exit_code=result.returncode, stdout=result.stdout or '', stderr=result.stderr or '')
        except (OSError, subprocess.SubprocessError) as exc:
            evidence['error'] = f'{type(exc).__name__}: {exc}'
        return evidence

    def read(point):
        probe = dict(kernel_clock.validate_probe((reader or clock.read_frequency)()))
        record[point] = probe
        gate = clock.frequency_bound(probe['raw_word'], limits)
        record[point + '_gate'] = gate
        return gate

    try:
        # Use the plan bytes that will actually be installed, not cached
        # prepare evidence or hard-coded 335/5764-second assumptions.
        night_plan = pilot.h.read(state['plan_path'])
        if pilot.h.locator(state['plan_path'])['sha256'] != state['plan_sha256']:
            raise ValueError('prepared plan bytes changed')
        t0 = night_plan.get('t0_epoch_s')
        if not pilot.h.finite(t0) or t0 <= time.time():
            raise ValueError('plan t0 has passed or is unavailable; prepare a fresh session')
        try:
            hazard = night_plan['hazard_window']
            limits = dict(hazard['thresholds']['clock'], t_stream_max_s=hazard['T_stream_max_s'])
        except (KeyError, TypeError) as exc:
            record['cause'] = 'clock.frequency_plan_invalid'
            raise ValueError(f'plan clock budget unavailable: {exc}') from exc
        passes = read('before')['passes']
        try:
            _require_night_job_absent(runner)
        except ValueError as exc:
            record['cause'] = ('prepare.night_job_loaded' if 'already holds the night job' in str(exc)
                               else 'prepare.night_job_state_unavailable')
            raise
        query_argv = ('/usr/bin/sudo', '-n', '/usr/sbin/systemsetup', '-getusingnetworktime')
        query = command(query_argv) if passes else None
        if (query is None or (query.get('exit_code') == 0
                              and query.get('stdout', '').strip().casefold() == 'network time: on')):
            off = command(network_time_off.OFF_ARGV)
            if off.get('exit_code') != 0 or not network_time_off.off_stdout_admitted(off.get('stdout')):
                raise ValueError('network time OFF setter unavailable or unverified')
            query = command(query_argv)
        if query.get('exit_code') != 0 or query.get('stdout', '').strip().casefold() != 'network time: off':
            raise ValueError('network time OFF read-back failed')
        record['network_time'] = {'observed': 'off', 'verified': True}
        # RL-26: the receipt binds C source; sudo runs this installed binary.
        # Keep both identities on every arm, including a no-op. The kit check
        # already validated the receipt; use its binding, not a prepare cache.
        from joulewise.align.apple import v4_registration
        source_path = 'scripts/zero_ntp_frequency.c'
        source_root = Path(state.get('source_measurement_root') or state.get('measurement_root') or ROOT)
        helper = Path(ZERO_FREQUENCY_ARGV[-1])
        identity = record['zero_helper'] = {'path': str(helper), 'sha256': None,
                                          'source': {'path': source_path, 'sha256': None}}
        try:
            receipt = pilot.h.read(source_root / v4_registration.REGISTRATION / 'registration_receipt.json')
            bound = receipt['artifacts'][source_path]
            identity['source']['sha256'] = bound
            if not v4_registration.is_digest(bound) or _sha256((source_root / source_path).read_bytes()) != bound:
                raise ValueError('helper source differs from its registration binding')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            record['cause'] = 'clock.frequency_helper_source_unbound'
            raise ValueError(f'helper source binding unavailable: {exc}') from exc
        try:
            identity['sha256'] = _sha256(helper.read_bytes())
        except OSError as exc:
            identity['error'] = f'{type(exc).__name__}: {exc}'
            if not passes:
                record['cause'] = 'clock.frequency_helper_unreadable'
                raise ValueError('needed installed frequency helper is missing or unreadable') from exc
        if passes:
            # A passing nonzero word also needs no correction: this preflight
            # uses the existing budget, never an extra word==0 threshold.
            read('after')
            record['action'] = 'no_op'
        else:
            zero = command(ZERO_FREQUENCY_ARGV)
            # Always retain the new word, including after helper denial/error.
            gate = read('after')
            if zero.get('exit_code') != 0:
                raise ValueError('frequency zero helper unavailable or failed (sudo -n; no prompt)')
            if record['after']['raw_word'] != 0 or not gate['passes']:
                raise ValueError('frequency zero read-back failed or projected bound still fails')
            record['action'] = 'zeroed'
        if not record['after_gate']['passes']:
            raise ValueError('frequency word changed to a failing bound during preflight')
        if t0 <= time.time():
            raise ValueError('plan t0 passed during preflight; prepare a fresh session')
        record.update(ok=True, cause=None, reason=None)
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        record['reason'] = f'{type(exc).__name__}: {exc}'
        # OFF/census failures still get a fresh after word when possible.
        if record['before'] is not None and record['after'] is None:
            try:
                read('after')
            except (OSError, ValueError, KeyError, TypeError, OverflowError) as after_error:
                record['after_error'] = f'{type(after_error).__name__}: {after_error}'
    return record


def frequency_word_pre_t0(state, *, reader=None):
    """Last read-only arm probe, after checks and before the quiet-dwell stamp.

    RL-26 requires the actual last pre-t0 word, separate from prepare and the
    correcting preflight. No new frequency threshold is introduced here.
    """
    from joulewise import kernel_clock
    from joulewise.hazards import clock
    record = {'ok': False, 'cause': 'clock.frequency_pre_t0_unavailable', 'reason': None,
              'probe': None, 't0_epoch_s': None,
              'read_started_epoch_s': None, 'read_finished_epoch_s': None}
    try:
        plan = pilot.h.read(state['plan_path'])
        if pilot.h.locator(state['plan_path'])['sha256'] != state['plan_sha256']:
            raise ValueError('prepared plan bytes changed')
        t0 = record['t0_epoch_s'] = plan.get('t0_epoch_s')
        if not pilot.h.finite(t0) or t0 <= time.time():
            raise ValueError('plan t0 has passed or is unavailable; prepare a fresh session')
        record['cause'] = 'clock.frequency_pre_t0_unreadable'
        record['read_started_epoch_s'] = time.time()
        record['probe'] = dict(kernel_clock.validate_probe((reader or clock.read_frequency)()))
        record['read_finished_epoch_s'] = time.time()
        record['cause'] = 'clock.frequency_pre_t0_unavailable'
        if record['read_finished_epoch_s'] >= t0:
            raise ValueError('plan t0 passed during the final frequency read')
        record.update(ok=True, cause=None)
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        record['reason'] = f'{type(exc).__name__}: {exc}'
    return record


def _power_markers(measurement_root):
    """The host-level marker (lead ruling R6-7) and the R1 chain's own
    ``$MEASUREMENT_ROOT`` marker."""
    from joulewise.align.apple import powermode
    return [Path(powermode.host_marker_path()), Path(measurement_root) / powermode.R1_HIGH_POWER_MARKER]


def session_start_restore(measurement_root, *, runner=None, lock=None, keep_owner=None):
    """Lead ruling R6-7: restore Automatic for any High Power marker at a
    session start (except one this session itself owns, ``keep_owner``), then
    re-check the mode (``restore_automatic`` reads it back). A measuring night
    holding the host night lock defers it: that night restores at its close.
    Raises ValueError when a restore ran and did not read back 0."""
    from joulewise.align.apple import powermode
    markers = [m for m in _power_markers(measurement_root)
               if os.path.lexists(m) and not (keep_owner and powermode.owned_by(m, **keep_owner))]
    record = powermode.restore_owed(markers, runner=runner, lock=lock, reason='session_start')
    record['host_state_dir'] = powermode.host_state_dir()   # lead ruling R7-10
    if record['action'] in ('restore_failed', 'error'):
        raise ValueError('v4 session start refused: a High Power marker is present and the Automatic restore '
                         'failed: ' + json.dumps(record.get('restore') or record.get('error'), sort_keys=True,
                                                 default=str))
    return record


def observe_ac_powermode(runner=None):
    """Read the host's AC-profile powermode (read-only ``pmset -g custom``)."""
    from joulewise.align.apple.powermode import observe_ac_powermode as observe
    return observe(runner)


def bundle_ac_powermode(bundle):
    """The AC powermode a member bundle recorded at episode start, or None."""
    from joulewise.desk_compress import read_bytes
    try:
        episode = json.loads(read_bytes(Path(bundle) / 'outputs/align_episode.json'))
    except (OSError, ValueError):
        return None
    record = (episode.get('hardware') or {}).get('ac_powermode')
    return record.get('value') if isinstance(record, dict) else None


X2_GATE_FLAGS = ('thermal.gate_timeout:', 'thermal.hold_timeout:')


def d_member_x2_report(plan_members, runs_root):
    """Print-only (LEAD-RULINGS-2 R10, lead ruling on open point (c)): W1's D
    members' X2 count and rate. X2 is a G0 that timed out (the member ends
    before turn 1; under R10-2(a) at the receipt's G0*) or a G1/hold timeout.
    A bundle that cannot be read is listed under ``unread`` and left out of
    the rate. Never an instrument check."""
    from joulewise.desk_compress import read_bytes
    rows, unread = [], []
    for member in plan_members:
        if member.get('role') != 'D':
            continue
        try:
            episode = json.loads(read_bytes(Path(runs_root) / member['run_id'] / 'outputs/align_episode.json'))
        except (OSError, ValueError):
            unread.append(member['run_id'])
            continue
        thermal = (episode.get('hardware') or {}).get('thermal') or {}
        g0 = next((r for r in thermal.get('intervals') or () if isinstance(r, dict) and r.get('kind') == 'G0'), None)
        flags = [str(f) for f in episode.get('flags') or ()]
        g0_timeout = bool(g0) and g0.get('outcome') == 'timeout'
        gate_timeout = any(f.startswith(X2_GATE_FLAGS) for f in flags)
        rows.append({'run_id': member['run_id'], 'ordinal': member.get('ordinal'),
                     'g0_outcome': g0.get('outcome') if g0 else None,
                     'g0_wait_s': g0.get('duration_s') if g0 else None,
                     'g0_timeout_x2': g0_timeout, 'gate_timeout_x2': gate_timeout,
                     'x2': g0_timeout or gate_timeout})
    count = sum(row['x2'] for row in rows)
    return {'print_only': True, 'authority': 'LEAD-RULINGS-2 R10, lead ruling on open point (c)',
            'd_members': len(rows) + len(unread), 'read': len(rows), 'unread': unread,
            'x2_count': count, 'g0_timeout_x2_count': sum(row['g0_timeout_x2'] for row in rows),
            'x2_rate': count / len(rows) if rows else None, 'members': rows}


def battery_windows_pass(windows):
    return bool(windows) and all(w.get('bar_pass') is True for w in windows.values())


# Lead ruling 9 (R14; W1-BLOCKERS-AGREEMENT): B is an operational stop with automatic
# resume. A false v4_B_bar is recorded but does not block the full-desk gate, and a
# member excluded ONLY for charging (v4_battery.EXCLUDE) is removed from the window
# without failing the common desk's exclusion-derived checks (Sol2 review S2-01).
# v4_cadence ``battery_window`` governs the resume.
FULL_DESK_GATE_EXEMPT = ('v4_B_bar',)
EXCLUSION_DERIVED = ('no_member_exclusions', 'chain_eligibility')


def _exclusion_codes(member):
    codes = [*(member.get('exclusion_codes') or []), *(member.get('calibration_exclusions') or [])]
    summary = member.get('summary') or {}
    codes += list(summary.get('exclusion_codes') or [])
    return {str(c).split(':')[0] for c in codes}


def charging_only_exclusion(member):
    """True iff the member is excluded and every exclusion code is a charging B code."""
    from joulewise.align.apple.v4_battery import EXCLUDE
    codes = _exclusion_codes(member)
    return bool(member.get('excluded')) and bool(codes) and codes <= set(EXCLUDE)


def neutral_exclusion(member):
    """True iff the member is excluded and every code is a charging B code or a disclosure-only contention code.

    R22-1: no ``contention.*`` code may affect any desk verdict, gate or count; ruling 9: B alone never fails the
    full desk. Real (other) exclusions keep failing it.
    """
    from joulewise.align.apple import v4_contention
    from joulewise.align.apple.v4_battery import EXCLUDE
    codes = _exclusion_codes(member)
    return (bool(member.get('excluded')) and bool(codes)
            and all(c in set(EXCLUDE) or v4_contention.is_disclosure_only(c) for c in codes))


def full_desk_gate_pass(checks, members=None):
    """The ``full_desk_gate`` verdict.

    Every desk check must be true except ``v4_B_bar``. With the desk's
    ``members`` (evidence-aware), the exclusion-derived checks are re-derived
    with charging-only exclusions not counted, so B alone never fails the gate;
    any other exclusion still does. Without members the checks stand as recorded.
    """
    gated = {k: v for k, v in (checks or {}).items() if k not in FULL_DESK_GATE_EXEMPT}
    if members is not None and any(k in gated for k in EXCLUSION_DERIVED):
        # Charging-only members stay in the window evidence (readability, prechecks);
        # only their B exclusion stops counting against the desk.
        neutral = [{**m, 'excluded': False} if neutral_exclusion(m) else m for m in members]
        recomputed, _, _ = pilot.instrument_checks(neutral)
        others = any(m.get('excluded') for m in neutral)
        if 'no_member_exclusions' in gated:
            gated['no_member_exclusions'] = not others
        if 'chain_eligibility' in gated:
            gated['chain_eligibility'] = recomputed['chain_eligibility'] is True and not others
    return bool(gated) and all(v is True for v in gated.values())


def assign_work_group(record, row):
    """The identical-work group of a desk record, from its planned member row.

    R20: a supplemental escalation sentinel joins NO group, so U3's frozen comparison scope and U4's
    W and W-1 df are unchanged; it is reported descriptively (``supplemental_report``).
    """
    if row.get('supplemental'):
        record.update(supplemental=True, escalation_sentinel=row.get('escalation_sentinel'),
                      replay_of=row.get('replay_of'))
    elif row.get('replay_of'):
        record['identical_work_group'] = row['replay_of']
    elif row.get('ordinal') == 5 or row.get('role', '').startswith(('X-', 'Y-')):
        record['identical_work_group'] = row['run_id']


def supplemental_report(records):
    """Descriptive-only report of the two R20 escalation sentinels against their W1:5-replay source."""
    supplemental = [r for r in records if r.get('supplemental')]
    if not supplemental:
        return None
    by_id = {r['id']: r for r in records}
    return {'status': 'descriptive_only', 'authority': 'RUN_STATE 226 R20',
            'note': 'two exact replays of the admitted W1:5 trajectory; no held-out seed; U4 W and W-1 df unchanged',
            'members': [{'run_id': r['id'], 'escalation_sentinel': r.get('escalation_sentinel'),
                         'replay_of': r.get('replay_of'),
                         'tokens_identical_to_replay_of': (r.get('tokens') is not None
                              and (by_id.get(r.get('replay_of')) or {}).get('tokens') == r.get('tokens')),
                         'gross_episode_j': r.get('gross_episode_j'),
                         'replay_of_gross_episode_j': (by_id.get(r.get('replay_of')) or {}).get('gross_episode_j'),
                         'excluded': bool(r.get('excluded'))} for r in supplemental]}


def powermode_desk_check(*, state, members, runs_root, kit_path):
    """Council ruling 7: any member whose bundle-recorded AC powermode differs
    from the frozen series value sets ``instrument_ok`` false. The report also
    carries the D members' X2 count and rate (print-only, LEAD-RULINGS-2 R10)."""
    plan = {'members': pilot._member_rows(state, kit=kit_path)}
    observed = {m['run_id']: bundle_ac_powermode(Path(runs_root) / m['run_id']) for m in plan['members']}
    verdict = kit.validate_powermode_members(plan, observed)
    checks = {'ac_powermode_members': verdict['instrument_ok']}
    report = {**verdict, 'd_member_x2': d_member_x2_report(plan['members'], runs_root)}
    if state.get('v4_series'):
        report['series'] = state['v4_series']
        report['pool_members'] = {role: [r['run_id'] for r in plan['members'] if r.get('pool_role') == role]
                                  for role in ('anchor', 'sentinel', 'fit', 'calibration', 'test')}
        report['calibration_counts_final'] = False
        report['calibration_counts_note'] = 'Final eligibility receipt required; desk diagnostics never imply pool entry.'
    from joulewise.align.apple import km003c
    try:
        custody = (state.get('inputs') or {}).get('custody_root')
        if custody is None and state.get('plan_path'):
            custody = pilot.h.read(state['plan_path'])['custody_root']
        dc = km003c.session_report(custody, plan['members'], runs_root, members)
    except Exception as exc:  # secondary diagnostics must never become a rails admission gate
        dc = km003c.unavailable_report(plan['members'], 'meter.desk_failed:' + type(exc).__name__,
                                       detail=str(exc))
    # MED-4: per-member DC residuals print for BENIGN members only; sabotage (any non-benign)
    # members' DC rows are sealed (hash only) until the v5 addendum registers.
    dc = km003c.seal_non_benign(dc, plan['members'])
    for rid, row in dc['members'].items():
        if row.get('sealed'):
            print(f'{rid} {km003c.LABEL}: ' + json.dumps({k: row[k] for k in
                  ('status', 'sealed', 'sealed_sha256', 'flags')}, sort_keys=True))
        else:
            print(f'{rid} {km003c.LABEL}: ' + json.dumps({k: row[k] for k in
                  ('status', 'dc_in_energy_j', 'dc_in_delta_j', 'dc_in_residual_j', 'flags')}, sort_keys=True))
    report['km003c'] = dc
    # Keep the common v3 desk unchanged. V4 adds its registered thermal desk.
    from scripts.align_v4_thermal_desk import registration_evidence, enrich_record, r1_soak_c, contrast_predeclaration
    from joulewise.align.apple.thermal_desk import read_bundle_record, window_report
    from joulewise.align.apple import v4_registration, light_triage
    registration_dir = Path(state.get('registration_dir', Path(state['measurement_root'])/kit.KIT/'registration'))
    try:
        bar, wp19 = registration_evidence(registration_dir)
    except (OSError, ValueError) as exc:
        checks['v4_registration_evidence'] = False
        report['registration_error'] = str(exc)
        return checks, report
    from joulewise.align.apple import v4_battery
    try:
        battery_policy = json.loads((registration_dir/'battery_window_policy.json').read_bytes())
    except (OSError, ValueError):
        battery_policy = None
    journal = v4_battery.load_journal(Path(custody)/'hazards/monitor/battery.jsonl') if custody else ([], None, 1)
    from joulewise.align.apple import v4_contention
    # R22-1: in-window contention is disclosure-only; every member records its outside-tree CPU-seconds.
    contention_journal = (v4_contention.load_journal(Path(custody)/'hazards/monitor/contention.jsonl')
                          if custody else ([], None, 1))
    records = []
    pilot_members = {m['run_id']: m for m in members}
    for row in plan['members']:
        path = Path(runs_root)/row['run_id']
        try:
            r = enrich_record(read_bundle_record(path), path)
        except (OSError, ValueError) as exc:
            r = {'id': row['run_id'], 'gated': row['ordinal'] >= 5, 'model': row.get('model_id'),
                 'flags': ['member.runtime_failure'], 'tokens': None, 'intervals': [],
                 'turn_observation': [], 'coverage': [], 'releases': [], 'turn_admissions': 0,
                 'pm_period_s': .1, 'calibration_exclusions': ['member.runtime_failure'], 'error': str(exc)}
        r.update({k: row[k] for k in ('ordinal', 'role', 'pool_role', 'condition', 'task_pair') if k in row},
                 window=(state.get('v4_series') or {}).get('window_id', state.get('window_id', 'W1')),
                 stage=row.get('stage_id'))
        v4_battery.attach(r, path, journal)
        v4_contention.attach(r, path, contention_journal)
        assign_work_group(r, row)
        if row.get('role', '').startswith(('X-', 'Y-')):
            r.update(template=row['role'][0], arm=row['role'][-1])
            fixture = json.loads((Path(state['measurement_root'])/kit.WP18_FIXTURES[r['template']]).read_bytes())
            expected = [{k: t[k] for k in ('prompt_token_ids', 'output_token_ids')} for t in fixture['turns']]
            r['pilot7_token_identical'] = r.get('tokens') == expected
        p = pilot_members.get(row['run_id'], {})
        codes, disclosed = v4_contention.split_codes(p.get('exclusion_codes', []))
        if disclosed:
            r['contention']['disclosed_codes'] = sorted(set(r['contention']['disclosed_codes']) | set(disclosed))
        # The only harvest input of the thermal section (light_triage proves U1-U3 ignore it); contention is
        # disclosure-only (R22-1) so only the effective codes reach it.
        light_triage.apply_harvest_codes(r, codes)
        records.append(r)
    policy = (kit.read_inputs(state['measurement_root']).get('R1') or {}).get('thermal_policy') or {}
    report['thermal'] = window_report(records, v4=True, u3_bar=bar,
        delta_slow_c=policy.get('delta_slow_c'), contrast_predeclared=contrast_predeclaration(wp19, policy))
    report['registration_diagnostics'] = v4_registration.desk_diagnostics(records,
        r1_soak=r1_soak_c(registration_dir), battery_policy=battery_policy)
    if state.get('v4_series', {}).get('window_id', 'W1') != 'W1':
        from joulewise.align.apple.v4_estimands import sentinel_admissibility
        report['registration_diagnostics']['sentinel'] = {
            'source': 'W1:5 (admitted before this series)',
            'candidates': {r['ordinal']: sentinel_admissibility(r) for r in records
                           if r.get('pool_role') == 'sentinel' and not r.get('supplemental')},
            'reference_status': 'requires authenticated R1/W1 E_ref for cross-window U4'}
    # R22-3: the printed balance check by condition (exclusions + flags per member-second); print only.
    from joulewise.align.apple import v4_balance
    report['balance_check'] = v4_balance.balance_check(records)
    for line in v4_balance.lines(report['balance_check']):
        print(line)
    if supplemental_report(records):
        report['supplemental_sentinels'] = supplemental_report(records)
    checks.update(light_triage.u_checks(report['thermal']))
    checks['v4_B_bar'] = battery_windows_pass(report['registration_diagnostics']['battery_windows'])
    for name, row in report['registration_diagnostics']['battery_windows'].items():
        print(f'{name} battery: '+json.dumps({k: row[k] for k in
              ('B_count', 'unobserved_count', 'assist_count', 'bar_pass', 'consequence')}, sort_keys=True))
    checks['v4_D_cohort'] = report['registration_diagnostics']['d_cohort']['instrument_ok']
    window_id = (state.get('v4_series') or {}).get('window_id', 'W1')
    if window_id != 'W1':
        # RUN_STATE 226 R15: the desk's provisional counts. The final adjudication
        # may lower them, never raise them (align_v4_series.calibration_rows).
        from scripts import align_v4_series as series
        d_window = (report['thermal'].get('model_windows') or {}).get(kit.D_TAG) or {}
        statuses = [(d_window.get(f'U{n}') or {}).get('status') for n in (1, 2, 3)]
        u_pass = True if statuses == ['pass'] * 3 else False if 'fail' in statuses else None
        report['series_desk_row'] = series.desk_row(
            series.load(state['source_measurement_root']), window_id,
            [{'run_id': r['id'], 'captured': (Path(runs_root) / r['id']).is_dir(), 'excluded': bool(r.get('excluded'))}
             for r in records], u_pass)
    return checks, report


def desk(session_root, **kwargs):
    state = pilot.h.read(Path(session_root) / 'session.json')
    if state.get('v4_series', {}).get('window_id', 'W1') != 'W1':
        from scripts import align_v4_series as series
        kwargs['kit'] = series.kit_path(state['v4_series']['window_id'])
    kwargs.setdefault('kit', kit.KIT)
    kwargs.setdefault('desk_schema', kit.DESK_SCHEMA)
    kwargs.setdefault('extra_checks', powermode_desk_check)
    from joulewise.align.apple import v4_contention
    kwargs.setdefault('exclusion_policy', v4_contention.split_codes)      # R22-1: contention is disclosure-only
    status = pilot.desk(session_root, **kwargs)
    # Evidence-aware full-desk verdict (ruling 9) beside the common desk status.
    try:
        members = pilot.h.read(status['pilot']).get('members', [])
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        members = None
    removed = [m.get('run_id') for m in members or () if charging_only_exclusion(m)]
    disclosed = [m.get('run_id') for m in members or () if m.get('disclosed_exclusion_codes')]
    status['full_desk_gate'] = {'pass': members is not None and full_desk_gate_pass(status.get('checks'), members),
                                'charging_only_members_removed': removed,
                                'contention_disclosed_members': disclosed,
                                'rule': 'all desk checks except v4_B_bar; charging-only exclusions removed (ruling 9)'}
    if status.get('pilot'):
        pilot.h.write(Path(status['pilot']).parent/'desk.json', status)
    print('full_desk_gate: ' + ('pass' if status['full_desk_gate']['pass'] else 'fail'))
    return status


def validate_series_state(state):
    """Recheck source kit and exact admission after prepare, before any arm."""
    from scripts import align_v4_series as series
    selection = state['v4_series']
    root = Path(state['source_measurement_root'])
    manifest = series.load(root)
    if (selection['manifest_sha256'] != kit.sha((root / series.MANIFEST).read_bytes())
            or selection['admission_sha256'] != kit.sha((root / series.ADMISSION).read_bytes())):
        raise ValueError('prepared series/admission changed; prepare a new session')
    window = series.selected(manifest, selection['window_id'])
    if window['role'] != selection['role']:
        raise ValueError('prepared series role changed')
    series.require_admission(root, manifest, post_w1=window['id'] != 'W1')
    if window['id'] != 'W1':
        series.generate(root, window['id'], check=True, extra_sentinels=selection.get('extra_sentinels', 0))
    directory = kit.KIT if window['id'] == 'W1' else series.kit_path(window['id'])
    return json.loads((root / directory / 'collection_plan.json').read_bytes())


ARM_RECORD_SCHEMA = 'joulewise.align_v4_arm.v1'
ARM_DWELL_SCHEMA = 'joulewise.align_v4_arm_dwell.v1'   # the dwell stamp, written alone after it is taken


def _sha256(raw):
    import hashlib
    return hashlib.sha256(raw).hexdigest()


def _commit_exists(root, commit):
    """Whether ``commit`` is a commit object in the repository at ``root`` (L3)."""
    import re
    if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit):
        return False
    try:
        return subprocess.run(['git', 'cat-file', '-e', f'{commit}^{{commit}}'], cwd=root,
                              capture_output=True, timeout=20, check=False).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _probe_meter_live(root, *, runner=None, seconds=3):
    """Verify the KM003C reader live at arm time (never lead-entered): run the monitor briefly.

    Live means: a stream with status streaming, samples, a clock fit, a closing line and a
    consistent raw offset. Secondary channel: the result gates nothing but this check itself.
    """
    import tempfile
    from joulewise.external import km003c_parse as kp
    from joulewise import t0_rehearsal
    with tempfile.TemporaryDirectory(prefix='v4-meter-probe-') as tmp:
        out = Path(tmp) / 'probe.jsonl'
        done = (runner or t0_rehearsal.observed_run)([sys.executable, '-B', str(Path(root) / 'scripts/km003c_monitor.py'), '--out', str(out),
                       '--duration', str(seconds)], cwd=root, capture_output=True, timeout=seconds+60, check=False)
        if getattr(done, 'returncode', 1) != 0 or not out.is_file():
            return {'live': False, 'reason': f'monitor probe exit {getattr(done, "returncode", None)}'}
        stream = kp.parse(out)
        offset = kp.raw_offset_ns(stream)
        live = bool(stream.present and stream.aligned and stream.trailer is not None and offset is not None)
        return {'live': live, 'samples': len(stream.host_ns), 'raw_offset_ns': offset,
                'stream_sha256': _sha256(out.read_bytes()), 'probe_seconds': seconds,
                **({} if live else {'reason': 'no aligned samples with a closing line'})}


def _record_bound(root, packet):
    """Whether the packet is bound to the LATEST committed window record (smoke G1, delta3).

    Three facts, all from committed Git objects: ``record_path`` at ``record_commit`` hashes to
    ``record_sha256`` and that commit is the last one that changed the record path (a re-committed
    record refuses); and the canonical series ledger (``series/state.json``) at HEAD names exactly
    this record as its ``previous_record`` and equals the packet's ``series_sha256`` (a newer
    window, even at a new record path, moves the ledger and stales an older window's packet).
    Unrelated commits do not stale a packet.
    """
    import re
    if not isinstance(packet, dict):
        return False
    commit, path, digest = packet.get('record_commit'), packet.get('record_path'), packet.get('record_sha256')
    series_path = packet.get('series_path')
    if (not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit) or not isinstance(path, str)
            or not path or Path(path).is_absolute() or '..' in Path(path).parts
            or not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest)
            or not isinstance(series_path, str) or Path(series_path).is_absolute() or '..' in Path(series_path).parts):
        return False
    try:
        blob = subprocess.run(['git', 'show', f'{commit}:{path}'], cwd=root, capture_output=True,
                              timeout=30, check=False)
        latest = subprocess.run(['git', 'log', '-1', '--format=%H', '--', path], cwd=root,
                                capture_output=True, text=True, timeout=30, check=False)
        ledger = subprocess.run(['git', 'show', f'HEAD:{series_path}'], cwd=root, capture_output=True,
                                timeout=30, check=False)
        state = json.loads(ledger.stdout) if ledger.returncode == 0 else None
    except (OSError, subprocess.SubprocessError, ValueError):
        return False
    return (blob.returncode == 0 and _sha256(blob.stdout) == digest
            and latest.returncode == 0 and latest.stdout.strip() == commit
            and isinstance(state, dict)
            and state.get('previous_record') == {'commit': commit, 'path': path, 'sha256': digest}
            and packet.get('series_sha256') == _sha256(ledger.stdout))


@timing_receipts.timed("arm", "v4_arm_checks")
def arm_checks(measurement_root, plan, *, runner=None, volume_runner=None, lock=None, owner=None,
               obc_off_attested_by=None, battery_runner=None, battery_log=None, window_battery_journal=None,
               now=None, next_arm_triage=None, commit_check=None, record_check=None,
               packet_builder=None, meter_probe=None, dwell_start=None, series_bind=None, pre_dwell=None,
               watchdog_plist=None, watchdog_check=None, watchdog_plan=None, watchdog_plan_path=None):
    """W1/D arm evidence: ruling 7 AC powermode and ruling 20 volumes.

    R17 review F7: every Git check (record commit, record binding) and the frozen-series binding
    (``series_bind(built) -> [reasons]``, from ``_arm_and_install``) run BEFORE the meter probe and
    before ``dwell_start_ns`` is recorded, so no Git or binding work falls inside the quiet dwell.
    Lead ruling on R17 review open item 5: ``pre_dwell(record)`` (from ``_arm_and_install``: the
    powermode check, the W1 disk gate and the arm-record write) also runs before the stamp. The
    stamp is the LAST step here; only in-memory work that depends on it (the probe-before-dwell
    order) follows, and it lands in ``record['quiet_dwell']``.

    Ruling 7: the AC-profile powermode must equal the plan's frozen series
    value; an R1 High Power marker under the measurement root is restored to
    Automatic first (narrow sudo rule) and the mode read again (HIGH-3). The
    observed value and the exact ``pmset -g custom`` text are recorded.
    Ruling 20: no external volume may be mounted; the configuration is pinned
    to status "off" (the SSD amendment is not adopted) and the census is
    recorded either way.
    """
    from joulewise.align.apple import external_volume, powermode
    expected = (plan.get('runtime_requirements') or {}).get('ac_powermode')
    marker = Path(measurement_root) / powermode.R1_HIGH_POWER_MARKER
    power = powermode.admit_ac_powermode(expected, marker=marker, markers=(powermode.host_marker_path(),),
                                         runner=runner, lock=lock, owner=owner)
    reasons = [] if power['admitted'] else ['ac_powermode: ' + str(power['reason'])]
    run = volume_runner or external_volume.run_command
    try:
        taken = external_volume.census(run)
        volumes = external_volume.arm_check(external_volume.validate_config(None), taken, run=run)
        volumes['mounts'] = [{k: row.get(k) for k in ('device', 'mount_point', 'fs_type', 'class')}
                             for row in taken.get('mounts', [])]
    except Exception as exc:  # noqa: BLE001 - an unmeasured census refuses
        volumes = {'verdict': external_volume.REFUSE, 'reasons': [f'census_failed:{type(exc).__name__}:{exc}']}
    if volumes['verdict'] != external_volume.PASS:
        reasons += ['external_volume: ' + reason for reason in volumes['reasons']]
    from joulewise import battery_float
    from joulewise.align.apple.v4_registration import battery_arm
    observed, raw = battery_float.observe(phase='arm_check', runner=battery_runner or runner)
    # MED-3: top-up evidence is derived from the logged battery record (completed charge
    # within 1800 s, or continuous float since it); a hand-entered time is not admissible.
    from joulewise.align.apple import v4_topup
    now_s = (now or time.time)()
    as_list = lambda value: [] if value is None else [value] if isinstance(value, (str, Path)) else list(value)
    logs, journals = as_list(battery_log), as_list(window_battery_journal)
    evidence = v4_topup.derive_from_sources(logs, journals, now_s) if logs or journals else None
    topup = ({'completed_at_epoch_s': evidence['completed_at_epoch_s'], 'source': evidence['source']}
             if evidence and evidence['admissible'] else None)
    battery = battery_arm(observed, obc_off_attested_by, topup, now_epoch_s=now_s)
    battery['topup_evidence'] = evidence
    battery['raw_ioreg'] = raw.decode('ascii', errors='backslashreplace')
    # Preserve optional reason fields verbatim without changing the frozen parser.
    battery['charging_reason_lines'] = [line for line in battery['raw_ioreg'].splitlines()
                                       if '"NotChargingReason"' in line or '"ChargerInhibitReason"' in line]
    try:
        batt = (runner or subprocess.run)(['pmset', '-g', 'batt']) if runner else subprocess.run(
            ['pmset', '-g', 'batt'], capture_output=True, text=True, timeout=10, check=False)
        # L8: pmset -g batt is retained evidence only; the ioreg predicate decides.
        battery['pmset_batt'] = {'exit_code': batt.returncode, 'stdout': batt.stdout, 'stderr': batt.stderr,
                                 'evidence_only': True}
    except (OSError, subprocess.SubprocessError) as exc:
        battery['pmset_batt'] = {'exit_code': None, 'error': str(exc), 'evidence_only': True}
    reasons += battery['reasons']
    # R12 B2: the frozen next-arm triage list gates every arm. The supplied packet is a POINTER, never
    # trusted data (lead ruling 2026-11-08, Opus packet review HIGH-1/2): the arm rebuilds the packet
    # itself from the identities the supplied one names, with its own clock and artifact-set digest,
    # judges its own build, and refuses a supplied packet that differs from it. Powermode, volume,
    # battery and the live meter are computed here from current hardware, never entered.
    from joulewise.align.apple import v4_cadence, v4_registration
    supplied, packet_file_sha256 = next_arm_triage, None
    if isinstance(supplied, (str, Path)):
        try:
            raw_packet = Path(supplied).read_bytes()
            supplied, packet_file_sha256 = json.loads(raw_packet), _sha256(raw_packet)
        except (OSError, ValueError):
            supplied = None
    current_digest = v4_registration.artifact_set_digest(measurement_root)
    built, matches, rebuild_error = None, False, None
    with timing_receipts.span("arm", "v4_packet_rebuild"):
        try:
            if packet_builder is not None:
                built, matches = packet_builder(measurement_root, supplied, now_epoch_s=now_s,
                                                current_artifact_set_sha256=current_digest)
            else:
                from scripts import align_v4_next_arm_packet as builder
                built, matches = builder.rebuild_and_compare(measurement_root, supplied, now_epoch_s=now_s,
                                                             current_artifact_set_sha256=current_digest)
        except (ValueError, KeyError, TypeError, AttributeError, OSError) as exc:
            rebuild_error = f'{type(exc).__name__}: {exc}'
        # R17 review F7: the Git subprocesses and the series binding finish here, before the probe and dwell.
        identity = None
        if built is not None:
            commit = built.get('record_commit')
            identity = {'artifact_set_sha256': current_digest,
                        'record_commit_exists': (commit_check or _commit_exists)(measurement_root, commit),
                        'record_bound': bool((record_check or _record_bound)(measurement_root, built))}
        series_binding = list(series_bind(built)) if series_bind is not None else None
    watchdog = (watchdog_check or watchdog_acceptance)(phase='pre_install', runner=runner,
        plist_path=watchdog_plist, plan=watchdog_plan, plan_path=watchdog_plan_path, now=now)
    if not watchdog['ok']:
        reasons.append(_watchdog_refusal('pre_install', watchdog))
    # The 3 s monitor launch is USB and process activity: it runs BEFORE the quiet/display dwell
    # starts, never during it (lead ruling 2026-11-08). The arm stamps the probe's end and the dwell
    # start on one monotonic clock and refuses unless the probe ended strictly earlier.
    with timing_receipts.span("arm", "v4_meter_probe"):
        probe_started_ns = time.monotonic_ns()
        try:
            meter = dict((meter_probe or _probe_meter_live)(measurement_root))
        except Exception as exc:  # noqa: BLE001 - an unverifiable meter refuses; it never raises out of the arm
            meter = {'live': False, 'reason': f'{type(exc).__name__}: {exc}'}
    meter.setdefault('probe_started_ns', probe_started_ns)
    meter.setdefault('probe_ended_ns', time.monotonic_ns())
    meter.setdefault('probe_ended_epoch_s', now_s)
    internal = {'series_powermode': bool(power['admitted']),
                'external_volume': volumes['verdict'] == external_volume.PASS,
                'charging_battery': bool(battery['admitted']),
                'meter_reader_live': meter.get('live') is True}
    if built is None:
        triage = v4_cadence.next_arm_triage(None, internal, None, now_epoch_s=now_s)
        triage['reasons'].append(f'packet could not be rebuilt from its named sources: {rebuild_error}')
        triage['admitted'] = False
    else:
        triage = v4_cadence.next_arm_triage(built, internal, identity, now_epoch_s=now_s)
        if not matches:
            triage['admitted'] = False
            triage['reasons'].append('packet does not match its committed sources (the supplied packet '
                                     'differs from the arm\'s own build)')
    triage.update(packet_file_sha256=packet_file_sha256, supplied_packet_matches_rebuild=matches,
                  rebuilt_packet=built, rebuilt_packet_sha256=(v4_cadence._canonical_sha256(built) if built else None),
                  meter_live_evidence=meter, rebuild_error=rebuild_error)
    reasons += ['next_arm_triage: ' + reason for reason in triage['reasons']
                if not reason.startswith(('triage series_powermode', 'triage external_volume',
                                          'triage charging_battery', 'triage meter_reader_live'))]
    reasons += ([] if internal['meter_reader_live'] else
                ['next_arm_triage: triage meter_reader_live failed'])
    record = {'schema': ARM_RECORD_SCHEMA, 'admitted': not reasons, 'reasons': reasons,
            'watchdog_acceptance': watchdog,
            'next_arm_triage': triage,
            'ac_powermode': power, 'external_volumes': volumes, 'battery': battery,
            # Lead ruling R7-10: the host state directory this arm used.
            'host_state_dir': powermode.host_state_dir()}
    if series_binding is not None:
        record['series_binding'] = series_binding
    if pre_dwell is not None:
        pre_dwell(record)        # every remaining check, read, disk_usage and write (lead ruling, item 5)
    # The quiet dwell starts HERE, after every subprocess, file write and disk_usage of the arm.
    dwell_start_ns = (dwell_start or time.monotonic_ns)()
    # In memory only from here on: the one value that depends on the stamp.
    dwell_ordered = (type(meter['probe_ended_ns']) is int and type(dwell_start_ns) is int
                     and meter['probe_ended_ns'] < dwell_start_ns)
    record['quiet_dwell'] = {'start_ns': dwell_start_ns, 'start_epoch_s': now_s,
                             'meter_probe_ended_ns': meter['probe_ended_ns'], 'meter_probe_before_dwell': dwell_ordered,
                             'git_and_series_binding_before_dwell': True,
                             'record_checks_and_writes_before_dwell': pre_dwell is not None}
    if not dwell_ordered:
        record['reasons'].append('quiet_dwell: the meter probe did not end before the quiet dwell started '
                                 '(it must run before the dwell, never during it)')
        record['admitted'] = False
    return record


def _disk_config_digest(config):
    import hashlib
    return hashlib.sha256(json.dumps(config, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def validate_offload_freshness(policy):
    import math
    if (not isinstance(policy, dict) or type(policy.get('max_age_s')) not in (int, float)
            or not math.isfinite(policy['max_age_s']) or policy['max_age_s'] <= 0
            or not kit.valid_lead_signature(policy.get('lead_signature'))):
        raise ValueError('offload freshness requires a prospective lead-signed max_age_s; no default duration (R11/R11)')


def daytime_offload_receipt(config, *, now=None, gate=None, freshness_policy=None):
    """By-day only: hash configured offloads while the SSD is available.

    The caller validates the R0 config first. No arm/capture is started here.
    """
    validate_offload_freshness(freshness_policy)
    from joulewise.align.r0_host import w1_disk_gate
    result = (gate or w1_disk_gate)(config)
    rows = result.get('offloads', [])
    if (result.get('status') != 'pass' or not rows or len(rows) != len(config.get('offloads', []))
            or any(r.get('pass') is not True or not r.get('observed') for r in rows)):
        raise ValueError('daytime offloads not verified')
    return {'schema': 'joulewise.align_v4.daytime_offloads.v1', 'epoch_s': (now or time.time)(),
            'config_sha256': _disk_config_digest(config), 'offloads': rows, 'freshness_policy': freshness_policy}


def w1_disk_check(config_path, *, gate=None, now=None):
    """Require current free disk plus a fresh bound daytime offload receipt.

    The arm never remounts or re-hashes an SSD. The by-day writer uses the
    original R0 inventory verifier. Empty offloads require an explicit waiver
    that none are owed. ``gate`` is the synthetic command-boundary seam.
    """
    if config_path is None:
        raise ValueError('W1 arm requires --w1-disk-config: the validated R0 desk config whose '
                         'disk_path and offloads the W1 disk gate checks')
    from joulewise.align.r0_host import w1_disk_gate
    from joulewise.align.r0_runner import validate_config
    raw_config = json.loads(Path(config_path).read_text())
    offloads_owed = raw_config.pop('offloads_owed', None)
    daytime_path = raw_config.pop('daytime_offload_receipt', None)
    freshness = raw_config.pop('daytime_offload_freshness', None)
    config = validate_config(raw_config)
    if not config.get('offloads') and offloads_owed != 'none':
        raise ValueError('W1 offloads: [] requires explicit offloads_owed: none; empty receipts do not pass')
    if daytime_path is not None:
        import shutil
        import math
        validate_offload_freshness(freshness)
        saved = json.loads(Path(daytime_path).read_bytes())
        if (saved.get('schema') != 'joulewise.align_v4.daytime_offloads.v1'
                or saved.get('config_sha256') != _disk_config_digest(config)
                or saved.get('freshness_policy') != freshness):
            raise ValueError('daytime offload receipt binding mismatch')
        epoch = saved.get('epoch_s')
        age = (now or time.time)()-epoch if type(epoch) in (int, float) else None
        if age is None or not math.isfinite(age) or not 0 <= age <= freshness['max_age_s']:
            raise ValueError('daytime offload receipt stale or future-dated')
        rows = saved.get('offloads', [])
        if (not rows or [r.get('label') for r in rows] != [r['label'] for r in config['offloads']]
                or any(r.get('pass') is not True or not r.get('observed') for r in rows)):
            raise ValueError('daytime offload receipt lacks verified offloads')
        free = shutil.disk_usage(config['disk_path']).free
        receipt = {'status': 'pass' if free >= 80_000_000_000 else 'fail',
                   'free_bytes_after_present_weights': free, 'required_free_bytes_after_r0': 80_000_000_000,
                   'offloads': rows, 'daytime_receipt': saved, 'receipt_age_s': age}
    elif gate is not None:
        receipt = gate(config)  # synthetic command-boundary seam
    elif not config.get('offloads') and offloads_owed == 'none':
        receipt = w1_disk_gate(config)
    else:
        raise ValueError('W1 requires daytime_offload_receipt; do not mount/re-hash the SSD at arm')
    if not isinstance(receipt, dict) or receipt.get('status') != 'pass':
        rows = [{k: row.get(k) for k in ('label', 'pass', 'error')} for row in (receipt or {}).get('offloads', [])]
        raise ValueError('W1 disk gate refused the arm: '
                         + json.dumps({'status': (receipt or {}).get('status'),
                                       'free_bytes_after_present_weights': (receipt or {}).get(
                                           'free_bytes_after_present_weights'),
                                       'required_free_bytes_after_r0': (receipt or {}).get(
                                           'required_free_bytes_after_r0'),
                                       'offloads': rows}, sort_keys=True))
    return receipt


def _require_night_job_absent(runner=None, *, label='com.joulewise.night'):
    """Lead ruling R7-6 (round-6 exec MEDIUM-4): the shared installer's launchd
    census (``bytes_h_session.install``: same argv, 10 s budget, only exit
    113 with the exact absent-service line admits), run before any power
    mode change. ``runner`` is the install's command boundary (the test seam)."""
    argv = ['launchctl', 'print', f'gui/{os.getuid()}/{label}']
    try:
        job = (runner(argv) if runner is not None else
               subprocess.run(argv, check=False, capture_output=True, text=True, timeout=10))
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError(f'v4 install refused: launchd job state unavailable: {exc}') from exc
    if job.returncode == 0:
        raise ValueError(f'v4 install refused: launchd already holds the night job ({label})')
    absent = f'Could not find service "{label}" in domain for user gui: {os.getuid()}'
    if job.returncode != 113 or absent not in (job.stderr or '').splitlines():
        raise ValueError(f'v4 install refused: launchd job state unavailable ({label})')


class _InstallReceipts:
    """Buffered install/arm boundary markers (Opus cold review MEDIUM-2: no stdout during the dwell).

    Rows only accumulate in memory while the install runs. ``take()`` hands out the rows not yet persisted:
    the pre-stamp rows go into the arm record that ``pre_dwell`` already writes before the dwell stamp, and
    the post-stamp rows (``v4_arm_checks`` end, ``v4_installer_handoff``) into the ``dwell.json`` writes the
    arm already makes. Nothing is written to stdout or any new file. The envelope's own ``v4_install`` end
    is emitted after the handoff has returned, so it is not persisted (an open envelope: a missing end stays
    missing). If the install fails before any record could carry the rows (no arm record was written), they
    go to stderr, outside any dwell.
    """

    def __init__(self):
        self.rows, self.persisted, self.carried = [], 0, False

    def take(self):
        rows = self.rows[self.persisted:]
        self.persisted = len(self.rows)
        self.carried = True
        return rows


_receipts = ContextVar('v4_install_receipts', default=None)


def _install_timing(operation):
    @wraps(operation)
    def wrapped(*args, **kwargs):
        buffer = _InstallReceipts()
        token = _receipts.set(buffer)
        try:
            with timing_receipts.bind(timing_receipts.Writer(buffer.rows.append, producer="v4_arm")), \
                 timing_receipts.span("arm", "v4_install"):
                return operation(*args, **kwargs)
        finally:
            _receipts.reset(token)
            if not buffer.carried:
                for row in buffer.rows:
                    try:
                        sys.stderr.write(json.dumps(row, sort_keys=True) + "\n")
                    except OSError:
                        pass
    return wrapped


def _take_receipts():
    buffer = _receipts.get()
    return buffer.take() if buffer is not None else []


@_install_timing
def install(session_root, *, runner=None, volume_runner=None, now=None, w1_disk_config=None,
            disk_gate=None, frequency_reader=None, frequency_runner=None, frequency_preflight=None,
            frequency_pre_t0=None, **kwargs):
    session = Path(session_root)
    state = pilot.h.read(session / 'session.json')
    measurement_root = state['measurement_root']
    # Council ruling 7: the frozen series powermode comes from the measurement
    # checkout's r1_slots, and arm refuses on a mismatch with the host.
    source_root = state['source_measurement_root'] if state.get('v4_series') else measurement_root
    kit.generate(source_root, check=True, source_root=source_root)
    plan = (validate_series_state(state) if state.get('v4_series') else
            json.loads((Path(measurement_root) / kit.KIT / 'collection_plan.json').read_bytes()))
    from joulewise.align.apple import powermode
    high = None
    # Lead ruling R6-7: the High Power marker is host-level, so every later
    # session, night and the watchdog see it; it names this session as owner.
    marker = Path(powermode.host_marker_path())
    custody_root = (state.get('inputs') or {}).get('custody_root')
    if custody_root and (Path(custody_root) / 'night/result.json').is_file():
        # A terminal session has no night left to restore Automatic (Sol
        # critique of R5-6): never change the power mode for it.
        raise ValueError('v4 install refused: the session is terminal (night/result.json exists)')
    owner = {'custody_root': custody_root, 'plan_path': state.get('plan_path')}
    # R6-7: the install holds the host night lock throughout, so no restore by
    # a late launchd fire interleaves with it and it never changes the mode
    # under a measuring night.
    lock = powermode.HostLock(role='v4-install')
    # Lead ruling R7-4: TERM and HUP unwind the install like INT, so its normal
    # close runs (the Automatic restore below included).
    closing, restore_signals = _termination_handlers()
    try:
        if not lock.acquire():
            raise ValueError('v4 install refused: a measuring night holds the host night lock '
                             f'({powermode.night_lock_path()})')
    except BaseException:
        restore_signals()
        raise
    try:
        already = (state.get('install') or {}).get('exit_code') == 0
        entering = (plan.get('runtime_requirements') or {}).get('ac_powermode') == 2 and not already
        if entering:
            # Lead ruling R7-6: plan-0 nights do not hold this lock. Refuse a
            # loaded (or unknown) night job before any pmset command, the
            # session-start restore included.
            _require_night_job_absent(runner)
        # R6-7 session start: any marker this session does not own is a
        # restore owed (an R1 crash, an abandoned or killed W1 night).
        start = session_start_restore(measurement_root, runner=runner, lock=lock,
                                      keep_owner={'custody_root': custody_root})
        if start['action'] != 'none':
            pilot.h.write(session / f'staging/v4-session-start-restore-{time.time_ns()}.json', start)
        try:
            frequency = (frequency_preflight or frequency_word_preflight)(
                state, reader=frequency_reader, runner=frequency_runner or runner)
            if entering and frequency['ok']:
                # Lead ruling R5-6: W1 under an adopted High Power. The marker
                # comes first (powermode.enter_high_power), so any later crash
                # leaves the restore owed. Inside the try (round-5 executing
                # review): a signal during the entry itself, after pmset
                # applied 2, still restores Automatic below.
                high = powermode.enter_high_power(marker, runner=runner, owner=owner)
            result = _arm_and_install(session, state, measurement_root, plan, high, runner=runner,
                                      volume_runner=volume_runner, now=now, w1_disk_config=w1_disk_config,
                                      disk_gate=disk_gate, lock=lock,
                                      owner=owner if any(owner.values()) else None,
                                      watchdog_undo_closing=closing,
                                      frequency_preflight_record=frequency,
                                      frequency_pre_t0_check=lambda: (frequency_pre_t0 or frequency_word_pre_t0)(
                                          state, reader=frequency_reader), **kwargs)
            if entering and not (isinstance(result, dict) and result.get('exit_code') == 0):
                # Round-5 cold pass MEDIUM-1 (R6-7): the shared installer
                # returned without installing (launchd already holds a night
                # job). No night of this session will close the High Power
                # span, so it is not an arm: restore below and refuse.
                raise ValueError('v4 install did not install the night job (installer not called); '
                                 'Automatic restored')
            return result
        except BaseException as exc:
            closing()
            if entering:
                # The arm did not hand off: leave the host Automatic (R5-6), on
                # every failure from the mode change on.
                restore = powermode.restore_automatic(marker, runner=runner)
                try:
                    pilot.h.write(session / f'staging/v4-arm-restore-{time.time_ns()}.json', restore)
                except Exception:  # noqa: BLE001 - the restore itself is what matters
                    pass
                if (isinstance(exc, ValueError) and str(exc).startswith('watchdog_acceptance: post_install:')
                        and not restore.get('ok')):
                    raise ValueError(f'{exc}; install_undo_failed: host Automatic restore failed: {restore}') from exc
            raise
    finally:
        closing()
        lock.release()
        restore_signals()


TERMINATION_SIGNALS = (signal.SIGTERM, signal.SIGHUP)


def _termination_handlers():
    """Lead ruling R7-4: until the close begins (``closing()``), SIGTERM and
    SIGHUP raise KeyboardInterrupt, as SIGINT does, so the install's normal
    close runs; once it has begun they are swallowed so they cannot
    interrupt the restore. Python handlers reset on exec, so children keep
    default dispositions. Main thread only. Returns ``(closing, restore)``."""
    if threading.current_thread() is not threading.main_thread():
        return (lambda: None), (lambda: None)
    state = {'closing': False}

    def handler(signum, _frame):
        if not state['closing']:
            raise KeyboardInterrupt(f'signal {signum}')

    previous = {sig: signal.signal(sig, handler) for sig in TERMINATION_SIGNALS}

    def closing():
        state['closing'] = True

    def restore():
        for sig, old in previous.items():
            signal.signal(sig, old)
    return closing, restore


def _watchdog_post_install(state, dwell, *, runner=None, plist_path=None, check=None, closing=None, now=None):
    """Isolated W-1 post-install step (one call site); refusal removes this arm's jobs.

    The enclosing install's existing exception path restores any High Power
    it entered, under its still-held host lock and termination shield.
    """
    from joulewise.night_agent_install import LABELS
    quiet = dwell['quiet_dwell']
    quiet['watchdog_post_install_start_ns'] = time.monotonic_ns()
    result = {'ok': False, 'state': 'UNAVAILABLE', 'reason': None, 'plan_read_proven': False}
    try:
        plan = pilot.h.read(state['plan_path'])
        deadline = quiet['watchdog_post_install_start_ns'] + WATCHDOG_TIMEOUT_S * 1_000_000_000
        result = (check or watchdog_acceptance)(phase='post_install', runner=runner, plist_path=plist_path,
                                               plan=plan, now=now, deadline_ns=deadline)
        result['stopped'] = result['state'] == 'STOPPED'
        if result['ok']:
            if time.monotonic_ns() > deadline:
                raise TimeoutError('watchdog acceptance timeout')
            t0 = plan.get('t0_epoch_s')
            if not pilot.h.finite(t0):
                raise ValueError('installed plan t0_epoch_s unavailable')
            remaining = t0 - WATCHDOG_PLAN_LEAD_S - (now or time.time)()
            if result['state'] == 'FENCED' or result['state'].startswith('STANDDOWN_'):
                result['evidence_class'] = 'fence_observed'
            elif remaining <= 0:
                result.update(ok=False, reason='inside plan span without a fence')
            else:
                result.update(evidence_class='installed_plan_parsed_no_fence_yet',
                              seconds_until_span_begins=remaining)
    except BaseException as exc:  # a signal after install must undo the jobs too
        result.update(ok=False, state='UNAVAILABLE', reason=f'{type(exc).__name__}: {exc}')
    finally:
        quiet['watchdog_post_install_end_ns'] = time.monotonic_ns()
        quiet['watchdog_post_install'] = result
    if result['ok']:
        return
    if closing is not None:
        closing()  # existing termination shield protects uninstall and the enclosing host restore
    undo = result['install_undo'] = {'errors': [], 'remaining_labels': []}
    argv = [str(Path(state['measurement_root']) / 'scripts/install_night_agent.sh'),
            '--plan', state['plan_path'], '--uninstall']
    undo['argv'] = argv
    try:
        done = (runner or subprocess.run)(argv, check=False, capture_output=True, text=True, timeout=180)
        undo.update(exit_code=done.returncode, stdout=done.stdout, stderr=done.stderr)
        if done.returncode != 0:
            undo['errors'].append(f'uninstaller exited {done.returncode}; plists may remain for {", ".join(LABELS)}')
    except (OSError, subprocess.SubprocessError) as exc:
        undo['errors'].append(f'uninstaller: {type(exc).__name__}: {exc}')
    for label in LABELS:
        try:
            _require_night_job_absent(runner, label=label)
        except ValueError as exc:
            undo['remaining_labels'].append(label)
            undo['errors'].append(f'{label}: {exc}')
    detail = ('install_undo_failed: ' + '; '.join(undo['errors']) if undo['errors'] else 'install undone')
    raise ValueError(_watchdog_refusal('post_install', result) + '; ' + detail)


def _arm_and_install(session, state, measurement_root, plan, high, *, runner, volume_runner, now,
                     w1_disk_config, disk_gate, lock=None, owner=None,
                     obc_off_attested_by=None, battery_runner=None, battery_log=None,
                     window_battery_journal=None, next_arm_triage=None, commit_check=None, record_check=None,
                     packet_builder=None, meter_probe=None, dwell_start=None,
                     frequency_preflight_record=None, frequency_pre_t0_check=None,
                     watchdog_plist=None, watchdog_check=None, watchdog_undo_closing=None,
                     weight_digests_attested=None, **kwargs):
    # RUN_STATE 226 R15: every arm, W1 included, binds the frozen series. W1 binds an empty history after
    # R1; a C/T window the next frozen window. The packet bound is the arm's OWN rebuild (a supplied
    # packet is only a pointer), whose history is derived from the hash-chained, authenticated records.
    # R17 review F7: arm_checks runs this binding before the meter probe and the recorded dwell start.
    from scripts import align_v4_series as series
    window_id = (state.get('v4_series') or {}).get('window_id', 'W1')
    binding_root = state.get('source_measurement_root') or measurement_root

    def series_bind(built):
        try:
            if not isinstance(built, dict):
                raise ValueError('the arm could not rebuild the packet')
            series.bind_packet(binding_root, window_id, built, authenticated_by_rebuild=True)
            return []
        except (OSError, ValueError, KeyError, TypeError) as exc:
            return [f'series_binding: {window_id}: {exc}']

    # Every arm records what it saw, admitted or not (ruling 7: "every arm and every bundle records
    # it"), before the shared installer can run. Lead ruling (R17 review open item 5): that record
    # write, the powermode check and the W1 disk gate run BEFORE the dwell stamp (``pre_dwell``).
    attempt = 1
    while (session / f'staging/v4-arm-{attempt:03d}.json').exists():
        attempt += 1
    path = session / f'staging/v4-arm-{attempt:03d}.json'
    dwell_path = session / f'staging/v4-arm-{attempt:03d}.dwell.json'

    def refuse(record, reason):
        record['admitted'] = False
        record['reasons'] = [reason] + record['reasons']

    def pre_dwell(record):
        # No arm-time rehash: carry prepare's time and digest evidence verbatim.
        weights = (_attested_weight_digests(state, plan['members'], weight_digests_attested)
                   if weight_digests_attested is not None else
                   state.get('weight_digest_preflight', {'source': 'not_recorded_by_prepare'}))
        record['weight_digests'] = weights
        if weights.get('ok') is False:
            for reason in weights['reasons']:
                refuse(record, reason)
        built = (record.get('next_arm_triage') or {}).get('rebuilt_packet')
        binding = record.pop('series_binding', None)
        if binding is None:            # an arm_checks stand-in that did not run the hook
            binding = series_bind(built)
        record['series_window'] = window_id
        record['series_binding'] = binding
        record['series_packet'] = built
        if binding:
            record['admitted'] = False
            record['reasons'] = binding + record['reasons']
        if high is not None:
            record['high_power_enter'] = high
            if not high['ok']:
                refuse(record, 'high_power_enter: ' + str(high['reason']))
        record['epoch_s'] = (now or time.time)()
        receipt = None
        if frequency_preflight_record is not None:
            record['clock_frequency_preflight'] = frequency_preflight_record
            if not frequency_preflight_record['ok']:
                refuse(record, f"{frequency_preflight_record['cause']}: {frequency_preflight_record['reason']}")
        if record['admitted']:
            try:
                kit.arm_powermode_check(plan, record['ac_powermode'].get('observed'))
            except ValueError as exc:
                refuse(record, f'ac_powermode: {exc}')
        if record['admitted']:
            try:
                with timing_receipts.span("arm", "v4_disk_gate"):
                    receipt = w1_disk_check(w1_disk_config, gate=disk_gate)
                record['w1_disk_gate'] = receipt
            except (OSError, ValueError) as exc:
                refuse(record, f'w1_disk_gate: {exc}')
        record['clock_frequency_pre_t0'] = None
        if record['admitted'] and frequency_pre_t0_check is not None:
            final_frequency = record['clock_frequency_pre_t0'] = frequency_pre_t0_check()
            if not final_frequency['ok']:
                refuse(record, f"{final_frequency['cause']}: {final_frequency['reason']}")
        # The dwell stamp is the one value that depends on the dwell: it is held in memory and written
        # alone, to the dwell record, after the stamp (``quiet_dwell`` here only names that file).
        record['timing_receipts'] = _take_receipts()      # pre-stamp boundary markers (MEDIUM-2)
        record['quiet_dwell'] = {'start_ns': None, 'stamped_after_this_record': True, 'dwell_record': str(dwell_path)}
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x') as handle:
            handle.write(json.dumps(record, indent=2, sort_keys=True) + '\n')
        state.setdefault('v4_arm_records', []).append({'path': str(path), 'admitted': record['admitted'],
                                                        'ac_powermode': record['ac_powermode'].get('observed'),
                                                        'reasons': record['reasons'],
                                                        'dwell_record': str(dwell_path)})
        pilot.h.write(session / 'session.json', state)
        if receipt is not None:
            pilot.h.write(session / 'staging/w1_disk_gate.json', receipt)

    record = arm_checks(measurement_root, plan, runner=runner, volume_runner=volume_runner, lock=lock,
                        owner=owner, obc_off_attested_by=obc_off_attested_by, battery_runner=battery_runner,
                        battery_log=battery_log, window_battery_journal=window_battery_journal, now=now,
                        next_arm_triage=next_arm_triage, commit_check=commit_check,
                        record_check=record_check, packet_builder=packet_builder, meter_probe=meter_probe,
                        dwell_start=dwell_start, series_bind=series_bind, pre_dwell=pre_dwell,
                        watchdog_plist=watchdog_plist, watchdog_check=watchdog_check,
                        watchdog_plan=pilot.h.read(state['plan_path']), watchdog_plan_path=state['plan_path'])
    # After the stamp: the single in-memory dwell value, written once, then the handoff (or refusal).
    dwell = {'schema': ARM_DWELL_SCHEMA, 'arm_record': str(path), 'admitted': record['admitted'],
             'quiet_dwell': record['quiet_dwell'], 'timing_receipts': _take_receipts()}
    with dwell_path.open('x') as handle:
        handle.write(json.dumps(dwell, indent=2, sort_keys=True) + '\n')
    if not record['admitted']:
        raise ValueError('v4 arm refused: ' + '; '.join(record['reasons']))
    # R17: the powermode and W1 disk checks and their receipt write ran BEFORE the dwell (pre_dwell).
    # Lead ruling: also record when the installer's launchctl calls returned, on the dwell's monotonic
    # clock, so analysis can disclose the post-stamp installer interval (a later rule may trim it).
    outcome = 'raised'
    try:
        with timing_receipts.span("arm", "v4_installer_handoff"):
            installed = pilot.install(session, now=now or time.time, **kwargs)
        outcome = 'returned'
        dwell['quiet_dwell']['installer_end_ns'] = time.monotonic_ns()
        if isinstance(installed, dict) and installed.get('exit_code') == 0:
            _watchdog_post_install(state, dwell, runner=runner, plist_path=watchdog_plist, check=watchdog_check,
                                   closing=watchdog_undo_closing, now=now)
        return installed
    finally:
        dwell['quiet_dwell'].setdefault('installer_end_ns', time.monotonic_ns())
        dwell['quiet_dwell']['installer_outcome'] = outcome
        dwell['timing_receipts'] = dwell['timing_receipts'] + _take_receipts()   # the installer-handoff markers
        temporary = dwell_path.with_name(dwell_path.name + '.tmp')
        with temporary.open('x') as handle:
            handle.write(json.dumps(dwell, indent=2, sort_keys=True) + '\n')
        os.replace(temporary, dwell_path)


def main(argv=None):
    return pilot.main(argv, kit=kit.KIT, pack_id=kit.PACK_ID, desk_schema=kit.DESK_SCHEMA,
                      session_prefix='align-v4-', prepare_fn=prepare, install_fn=install,
                      desk_fn=desk,
                      prepare_options=(('--window-id', dict(help='frozen series window or D alias; requires series admission')),
                                       ('--extra-sentinels', dict(type=int, default=0, choices=(0, 2),
                                           help='R20: two supplemental escalation sentinels (ordinals 23, 24) '
                                                'after a U4-inconclusive window; ceiling 62,400 s'))),
                      desk_extra_checks=powermode_desk_check,
                      install_options=(('--w1-disk-config', dict(
                          type=Path, required=True,
                          help='validated R0 desk config (disk_path, W1 offloads) for the W1 disk gate')),
                                       ('--obc-off-attested-by', dict(required=True,
                          help='operator attesting Optimized Battery Charging is off')),
                                       ('--battery-log', dict(type=Path, required=True, action='append',
                          help='JSONL between-window battery log (scripts/align_v4_battery_log.py sample --loop, '
                               'run only between windows); repeatable; the arm derives top-up evidence from it')),
                                       ('--window-battery-journal', dict(type=Path, action='append',
                          help='a window hazard battery journal (the 1 Hz SMC B0AC lines and ioreg lines) merged '
                               'in time order with the between-window log; repeatable')),
                                       ('--weight-digests-attested', dict(type=Path,
                          help='RL-62 JSON: attested_by, optional attested_at_epoch_s, roots mapping to '
                               'registered_folded_sha256 and observed_folded_sha256 pairs')),
                                       ('--next-arm-triage', dict(type=Path, required=True,
                          help='R12 B2 next-arm triage packet (JSON) built off the MBP from the committed record'))))


if __name__ == '__main__':
    from joulewise.align.apple import powermode as _powermode
    _powermode.mark_production_entry('align_v4_session')   # lead ruling R7-10
    raise SystemExit(main())
