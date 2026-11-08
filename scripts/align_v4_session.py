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
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import align_pilot_session as pilot, align_v4_kit as kit


def series_ac_powermode(measurement_root):
    """The R1-frozen series AC powermode the generated collection plan carries."""
    plan = json.loads((Path(measurement_root) / kit.KIT / 'collection_plan.json').read_bytes())
    value = (plan.get('runtime_requirements') or {}).get('ac_powermode')
    if type(value) is not int or value not in (0, 2):
        raise ValueError(f'v4 collection plan freezes no series AC powermode (got {value!r})')
    return value


def prepare(measurement_root, session_root, *, power_runner=None, **kwargs):
    # Lead ruling R6-7: at every session start a host-level High Power marker
    # means an Automatic restore is owed. Restore it first (never under a
    # measuring night, which holds the host night lock and restores at its own
    # close) and refuse the session if the restore fails its read-back.
    start = session_start_restore(measurement_root, runner=power_runner)
    kit.generate(measurement_root, check=True, source_root=measurement_root)
    # Lead ruling R5-6: the night plan declares the frozen series powermode, so
    # run_night admits a High Power host only for a W1 that adopted it.
    kwargs.setdefault('ac_powermode', series_ac_powermode(measurement_root))
    kwargs.setdefault('kit', kit.KIT)
    kwargs.setdefault('pack_id', kit.PACK_ID)
    kwargs.setdefault('session_prefix', 'align-v4-')
    state = pilot.prepare(measurement_root, session_root, **kwargs)
    if start['action'] != 'none':
        try:
            pilot.h.write(Path(session_root) / f'staging/v4-session-start-restore-{time.time_ns()}.json', start)
        except Exception:  # noqa: BLE001 - the restore itself is what matters
            pass
    return state


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


def powermode_desk_check(*, state, members, runs_root, kit_path):
    """Council ruling 7: any member whose bundle-recorded AC powermode differs
    from the frozen series value sets ``instrument_ok`` false. The report also
    carries the D members' X2 count and rate (print-only, LEAD-RULINGS-2 R10)."""
    plan = {'members': pilot._member_rows(state, kit=kit_path)}
    observed = {m['run_id']: bundle_ac_powermode(Path(runs_root) / m['run_id']) for m in plan['members']}
    verdict = kit.validate_powermode_members(plan, observed)
    checks = {'ac_powermode_members': verdict['instrument_ok']}
    report = {**verdict, 'd_member_x2': d_member_x2_report(plan['members'], runs_root)}
    from joulewise.align.apple import km003c
    try:
        custody = (state.get('inputs') or {}).get('custody_root')
        if custody is None and state.get('plan_path'):
            custody = pilot.h.read(state['plan_path'])['custody_root']
        dc = km003c.session_report(custody, plan['members'], runs_root, members)
    except Exception as exc:  # secondary diagnostics must never become a rails admission gate
        dc = km003c.unavailable_report(plan['members'], 'meter.desk_failed:' + type(exc).__name__,
                                       detail=str(exc))
    for rid, row in dc['members'].items():
        print(f'{rid} {km003c.LABEL}: ' + json.dumps({k: row[k] for k in
              ('status', 'dc_in_energy_j', 'dc_in_delta_j', 'dc_in_residual_j', 'flags')}, sort_keys=True))
    report['km003c'] = dc
    # Keep the common v3 desk unchanged. V4 adds its registered thermal desk.
    from scripts.align_v4_thermal_desk import registration_evidence, enrich_record, r1_soak_c, contrast_predeclaration
    from joulewise.align.apple.thermal_desk import read_bundle_record, window_report
    from joulewise.align.apple import v4_registration
    registration_dir = Path(state.get('registration_dir', Path(state['measurement_root'])/kit.KIT/'registration'))
    try:
        bar, wp19 = registration_evidence(registration_dir)
    except (OSError, ValueError) as exc:
        checks['v4_registration_evidence'] = False
        report['registration_error'] = str(exc)
        return checks, report
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
        r.update({k: row[k] for k in ('ordinal', 'role') if k in row},
                 window='W1', stage=row.get('stage_id'))
        if row.get('replay_of'):
            r['identical_work_group'] = row['replay_of']
        elif row.get('ordinal') == 5 or row.get('role', '').startswith(('X-', 'Y-')):
            r['identical_work_group'] = row['run_id']
        if row.get('role', '').startswith(('X-', 'Y-')):
            r.update(template=row['role'][0], arm=row['role'][-1])
            fixture = json.loads((Path(state['measurement_root'])/kit.WP18_FIXTURES[r['template']]).read_bytes())
            expected = [{k: t[k] for k in ('prompt_token_ids', 'output_token_ids')} for t in fixture['turns']]
            r['pilot7_token_identical'] = r.get('tokens') == expected
        p = pilot_members.get(row['run_id'], {})
        codes = p.get('exclusion_codes', [])
        if any(str(c).startswith('battery.member_span') for c in codes):
            r['flags'].append('battery.member_span')
        r['excluded'] = bool(codes) or bool(r.get('calibration_exclusions'))
        records.append(r)
    policy = (kit.read_inputs(state['measurement_root']).get('R1') or {}).get('thermal_policy') or {}
    report['thermal'] = window_report(records, v4=True, u3_bar=bar,
        delta_slow_c=policy.get('delta_slow_c'), contrast_predeclared=contrast_predeclaration(wp19, policy))
    report['registration_diagnostics'] = v4_registration.desk_diagnostics(records,
        r1_soak=r1_soak_c(registration_dir))
    for model, result in report['thermal']['model_windows'].items():
        for n in (1, 2, 3):
            checks[f'v4_{model}_U{n}'] = result[f'U{n}']['status'] == 'pass'
    checks['v4_B_bar'] = all(w['bar_pass'] for w in report['registration_diagnostics']['battery_windows'].values())
    checks['v4_D_cohort'] = report['registration_diagnostics']['d_cohort']['instrument_ok']
    return checks, report


def desk(session_root, **kwargs):
    kwargs.setdefault('kit', kit.KIT)
    kwargs.setdefault('desk_schema', kit.DESK_SCHEMA)
    kwargs.setdefault('extra_checks', powermode_desk_check)
    return pilot.desk(session_root, **kwargs)


ARM_RECORD_SCHEMA = 'joulewise.align_v4_arm.v1'


def parse_topup_completed_at(value):
    """Epoch seconds, or ISO-8601 with an explicit UTC offset, to epoch seconds."""
    import datetime
    import math
    if value is None:
        return None
    if type(value) in (int, float):
        return float(value) if math.isfinite(value) else None
    try:
        return float(value) if math.isfinite(float(value)) else None
    except (TypeError, ValueError):
        pass
    try:
        stamp = datetime.datetime.fromisoformat(str(value))
    except ValueError:
        return None
    return stamp.timestamp() if stamp.tzinfo is not None else None


def arm_checks(measurement_root, plan, *, runner=None, volume_runner=None, lock=None, owner=None,
               obc_off_attested_by=None, battery_runner=None, topup_completed_at=None,
               topup_source=None, now=None):
    """W1/D arm evidence: ruling 7 AC powermode and ruling 20 volumes.

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
    topup = {'completed_at_epoch_s': parse_topup_completed_at(topup_completed_at),
             'source': topup_source} if topup_completed_at is not None or topup_source is not None else None
    battery = battery_arm(observed, obc_off_attested_by, topup, now_epoch_s=(now or time.time)())
    battery['raw_ioreg'] = raw.decode('ascii', errors='backslashreplace')
    # Preserve optional reason fields verbatim without changing the frozen parser.
    battery['charging_reason_lines'] = [line for line in battery['raw_ioreg'].splitlines()
                                       if '"NotChargingReason"' in line or '"ChargerInhibitReason"' in line]
    try:
        batt = (runner or subprocess.run)(['pmset', '-g', 'batt']) if runner else subprocess.run(
            ['pmset', '-g', 'batt'], capture_output=True, text=True, timeout=10, check=False)
        battery['pmset_batt'] = {'exit_code': batt.returncode, 'stdout': batt.stdout, 'stderr': batt.stderr}
        if batt.returncode != 0:
            battery['admitted'] = False
            battery['reasons'].append('pmset -g batt unavailable')
    except (OSError, subprocess.SubprocessError) as exc:
        battery['admitted'] = False
        battery['reasons'].append(f'pmset -g batt unavailable: {exc}')
    reasons += battery['reasons']
    return {'schema': ARM_RECORD_SCHEMA, 'admitted': not reasons, 'reasons': reasons,
            'ac_powermode': power, 'external_volumes': volumes, 'battery': battery,
            # Lead ruling R7-10: the host state directory this arm used.
            'host_state_dir': powermode.host_state_dir()}


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


def _require_night_job_absent(runner=None):
    """Lead ruling R7-6 (round-6 exec MEDIUM-4): the shared installer's launchd
    census (``bytes_h_session.install``: same argv, 10 s budget, only exit
    113 with the exact absent-service line admits), run before any power
    mode change. ``runner`` is the install's command boundary (the test seam)."""
    label = 'com.joulewise.night'
    argv = ['launchctl', 'print', f'gui/{os.getuid()}/{label}']
    try:
        job = (runner(argv) if runner is not None else
               subprocess.run(argv, check=False, capture_output=True, text=True, timeout=10))
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError(f'v4 install refused: launchd job state unavailable: {exc}') from exc
    if job.returncode == 0:
        raise ValueError('v4 install refused: launchd already holds the night job')
    absent = f'Could not find service "{label}" in domain for user gui: {os.getuid()}'
    if job.returncode != 113 or absent not in (job.stderr or '').splitlines():
        raise ValueError('v4 install refused: launchd job state unavailable')


def install(session_root, *, runner=None, volume_runner=None, now=None, w1_disk_config=None,
            disk_gate=None, **kwargs):
    session = Path(session_root)
    state = pilot.h.read(session / 'session.json')
    measurement_root = state['measurement_root']
    # Council ruling 7: the frozen series powermode comes from the measurement
    # checkout's r1_slots, and arm refuses on a mismatch with the host.
    kit.generate(measurement_root, check=True, source_root=measurement_root)
    plan = json.loads((Path(measurement_root) / kit.KIT / 'collection_plan.json').read_bytes())
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
            if entering:
                # Lead ruling R5-6: W1 under an adopted High Power. The marker
                # comes first (powermode.enter_high_power), so any later crash
                # leaves the restore owed. Inside the try (round-5 executing
                # review): a signal during the entry itself, after pmset
                # applied 2, still restores Automatic below.
                high = powermode.enter_high_power(marker, runner=runner, owner=owner)
            result = _arm_and_install(session, state, measurement_root, plan, high, runner=runner,
                                      volume_runner=volume_runner, now=now, w1_disk_config=w1_disk_config,
                                      disk_gate=disk_gate, lock=lock,
                                      owner=owner if any(owner.values()) else None, **kwargs)
            if entering and not (isinstance(result, dict) and result.get('exit_code') == 0):
                # Round-5 cold pass MEDIUM-1 (R6-7): the shared installer
                # returned without installing (launchd already holds a night
                # job). No night of this session will close the High Power
                # span, so it is not an arm: restore below and refuse.
                raise ValueError('v4 install did not install the night job (installer not called); '
                                 'Automatic restored')
            return result
        except BaseException:
            closing()
            if entering:
                # The arm did not hand off: leave the host Automatic (R5-6), on
                # every failure from the mode change on.
                restore = powermode.restore_automatic(marker, runner=runner)
                try:
                    pilot.h.write(session / f'staging/v4-arm-restore-{time.time_ns()}.json', restore)
                except Exception:  # noqa: BLE001 - the restore itself is what matters
                    pass
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


def _arm_and_install(session, state, measurement_root, plan, high, *, runner, volume_runner, now,
                     w1_disk_config, disk_gate, lock=None, owner=None,
                     obc_off_attested_by=None, battery_runner=None, topup_completed_at=None,
                     topup_source=None, **kwargs):
    record = arm_checks(measurement_root, plan, runner=runner, volume_runner=volume_runner, lock=lock,
                        owner=owner, obc_off_attested_by=obc_off_attested_by, battery_runner=battery_runner,
                        topup_completed_at=topup_completed_at, topup_source=topup_source, now=now)
    if high is not None:
        record['high_power_enter'] = high
        if not high['ok']:
            record['admitted'] = False
            record['reasons'] = ['high_power_enter: ' + str(high['reason'])] + record['reasons']
    record['epoch_s'] = (now or time.time)()
    # Every arm records what it saw, admitted or not (ruling 7: "every arm and
    # every bundle records it"), before the shared installer can run.
    attempt = 1
    while (session / f'staging/v4-arm-{attempt:03d}.json').exists():
        attempt += 1
    path = session / f'staging/v4-arm-{attempt:03d}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as handle:
        handle.write(json.dumps(record, indent=2, sort_keys=True) + '\n')
    state.setdefault('v4_arm_records', []).append({'path': str(path), 'admitted': record['admitted'],
                                                    'ac_powermode': record['ac_powermode'].get('observed'),
                                                    'reasons': record['reasons']})
    pilot.h.write(session / 'session.json', state)
    if not record['admitted']:
        raise ValueError('v4 arm refused: ' + '; '.join(record['reasons']))
    kit.arm_powermode_check(plan, record['ac_powermode']['observed'])
    receipt = w1_disk_check(w1_disk_config, gate=disk_gate)
    pilot.h.write(session / 'staging/w1_disk_gate.json', receipt)
    return pilot.install(session, **kwargs)


def main(argv=None):
    return pilot.main(argv, kit=kit.KIT, pack_id=kit.PACK_ID, desk_schema=kit.DESK_SCHEMA,
                      session_prefix='align-v4-', prepare_fn=prepare, install_fn=install,
                      desk_extra_checks=powermode_desk_check,
                      install_options=(('--w1-disk-config', dict(
                          type=Path, required=True,
                          help='validated R0 desk config (disk_path, W1 offloads) for the W1 disk gate')),
                                       ('--obc-off-attested-by', dict(required=True,
                          help='operator attesting Optimized Battery Charging is off')),
                                       ('--topup-completed-at', dict(required=True,
                          help='when the battery top-up completed: epoch seconds or ISO-8601 with UTC offset; '
                               'arm refuses if it is future-dated or more than 30 min old')),
                                       ('--topup-source', dict(required=True,
                          help='who/what attests that completion time (operator name or log)'))))


if __name__ == '__main__':
    from joulewise.align.apple import powermode as _powermode
    _powermode.mark_production_entry('align_v4_session')   # lead ruling R7-10
    raise SystemExit(main())
