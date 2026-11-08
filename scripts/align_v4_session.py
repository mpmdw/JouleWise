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
from functools import wraps
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
from joulewise import timing_receipts
from scripts import align_pilot_session as pilot, align_v4_kit as kit


def series_ac_powermode(measurement_root, kit_path=kit.KIT):
    """The R1-frozen series AC powermode the generated collection plan carries."""
    plan = json.loads((Path(measurement_root) / kit_path / 'collection_plan.json').read_bytes())
    value = (plan.get('runtime_requirements') or {}).get('ac_powermode')
    if type(value) is not int or value not in (0, 2):
        raise ValueError(f'v4 collection plan freezes no series AC powermode (got {value!r})')
    return value


def prepare(measurement_root, session_root, *, power_runner=None, window_id=None, extra_sentinels=0, **kwargs):
    # Lead ruling R6-7: at every session start a host-level High Power marker
    # means an Automatic restore is owed. Restore it first (never under a
    # measuring night, which holds the host night lock and restores at its own
    # close) and refuse the session if the restore fails its read-back.
    start = session_start_restore(measurement_root, runner=power_runner)
    kit.generate(measurement_root, check=True, source_root=measurement_root)
    series_state = None
    if extra_sentinels not in (0, 2) or (extra_sentinels and window_id in (None, 'W1')):
        raise ValueError('escalation sentinels (R20) apply to a C/T window after a U4/U5-inconclusive window only')
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
    state = pilot.prepare(measurement_root, session_root, **kwargs)
    if series_state is not None:
        if state.get('preparation_status') != 'STAGED':
            raise ValueError('series prepare produced no armable plan; inspect session flags')
        state['v4_series'] = series_state
        pilot.h.write(Path(session_root) / 'session.json', state)
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
        neutral = [{**m, 'excluded': False} if charging_only_exclusion(m) else m for m in members]
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
    from joulewise.align.apple import v4_registration
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
        if any(str(c).startswith('battery.member_span') for c in codes):
            r['flags'].append('battery.member_span')
        r['excluded'] = bool(codes) or bool(r.get('calibration_exclusions'))
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
    for model, result in report['thermal']['model_windows'].items():
        for n in (1, 2, 3):
            checks[f'v4_{model}_U{n}'] = result[f'U{n}']['status'] == 'pass'
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
    status = pilot.desk(session_root, **kwargs)
    # Evidence-aware full-desk verdict (ruling 9) beside the common desk status.
    try:
        members = pilot.h.read(status['pilot']).get('members', [])
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        members = None
    removed = [m.get('run_id') for m in members or () if charging_only_exclusion(m)]
    status['full_desk_gate'] = {'pass': members is not None and full_desk_gate_pass(status.get('checks'), members),
                                'charging_only_members_removed': removed,
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


def _probe_meter_live(root, *, runner=subprocess.run, seconds=3):
    """Verify the KM003C reader live at arm time (never lead-entered): run the monitor briefly.

    Live means: a stream with status streaming, samples, a clock fit, a closing line and a
    consistent raw offset. Secondary channel: the result gates nothing but this check itself.
    """
    import tempfile
    from joulewise.external import km003c_parse as kp
    with tempfile.TemporaryDirectory(prefix='v4-meter-probe-') as tmp:
        out = Path(tmp) / 'probe.jsonl'
        done = runner([sys.executable, '-B', str(Path(root) / 'scripts/km003c_monitor.py'), '--out', str(out),
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
               packet_builder=None, meter_probe=None, dwell_start=None):
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
    dwell_start_ns = (dwell_start or time.monotonic_ns)()
    dwell_ordered = (type(meter['probe_ended_ns']) is int and type(dwell_start_ns) is int
                     and meter['probe_ended_ns'] < dwell_start_ns)
    quiet_dwell = {'start_ns': dwell_start_ns, 'start_epoch_s': now_s, 'meter_probe_ended_ns': meter['probe_ended_ns'],
                   'meter_probe_before_dwell': dwell_ordered}
    if not dwell_ordered:
        reasons.append('quiet_dwell: the meter probe did not end before the quiet dwell started '
                       '(it must run before the dwell, never during it)')
    internal = {'series_powermode': bool(power['admitted']),
                'external_volume': volumes['verdict'] == external_volume.PASS,
                'charging_battery': bool(battery['admitted']),
                'meter_reader_live': meter.get('live') is True}
    if built is None:
        triage = v4_cadence.next_arm_triage(None, internal, None, now_epoch_s=now_s)
        triage['reasons'].append(f'packet could not be rebuilt from its named sources: {rebuild_error}')
        triage['admitted'] = False
    else:
        commit = built.get('record_commit')
        identity = {'artifact_set_sha256': current_digest,
                    'record_commit_exists': (commit_check or _commit_exists)(measurement_root, commit),
                    'record_bound': bool((record_check or _record_bound)(measurement_root, built))}
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
    return {'schema': ARM_RECORD_SCHEMA, 'admitted': not reasons, 'reasons': reasons,
            'next_arm_triage': triage, 'quiet_dwell': quiet_dwell,
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


def _install_timing(operation):
    @wraps(operation)
    def wrapped(*args, **kwargs):
        # The session CLI already owns stdout. Buffer throughout arm/install,
        # then append there after the unmeasured operation. No sidecar, file
        # open, or marker write can enter the quiet start-state preparation.
        rows = []
        try:
            with timing_receipts.bind(timing_receipts.Writer(rows.append, producer="v4_arm")), \
                 timing_receipts.span("arm", "v4_install"):
                return operation(*args, **kwargs)
        finally:
            for row in rows:
                try:
                    sys.stdout.write(json.dumps(row, sort_keys=True) + "\n")
                except OSError as error:
                    sys.stderr.write(f"timing receipt missing: {error}\n")
    return wrapped


@_install_timing
def install(session_root, *, runner=None, volume_runner=None, now=None, w1_disk_config=None,
            disk_gate=None, **kwargs):
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
                     obc_off_attested_by=None, battery_runner=None, battery_log=None,
                     window_battery_journal=None, next_arm_triage=None, commit_check=None, record_check=None,
                     packet_builder=None, meter_probe=None, dwell_start=None, **kwargs):
    record = arm_checks(measurement_root, plan, runner=runner, volume_runner=volume_runner, lock=lock,
                        owner=owner, obc_off_attested_by=obc_off_attested_by, battery_runner=battery_runner,
                        battery_log=battery_log, window_battery_journal=window_battery_journal, now=now,
                        next_arm_triage=next_arm_triage, commit_check=commit_check,
                        record_check=record_check, packet_builder=packet_builder, meter_probe=meter_probe,
                        dwell_start=dwell_start)
    # RUN_STATE 226 R15: every arm, W1 included, binds the frozen series. W1 binds an empty history after
    # R1; a C/T window the next frozen window. The packet bound is the arm's OWN rebuild (a supplied
    # packet is only a pointer), whose history is derived from the hash-chained, authenticated records.
    from scripts import align_v4_series as series
    built = (record.get('next_arm_triage') or {}).get('rebuilt_packet')
    window_id = (state.get('v4_series') or {}).get('window_id', 'W1')
    binding_root = state.get('source_measurement_root') or measurement_root
    try:
        if not isinstance(built, dict):
            raise ValueError('the arm could not rebuild the packet')
        series.bind_packet(binding_root, window_id, built, authenticated_by_rebuild=True)
        binding = []
    except (OSError, ValueError, KeyError, TypeError) as exc:
        binding = [f'series_binding: {window_id}: {exc}']
    record['series_window'] = window_id
    record['series_binding'] = binding
    record['series_packet'] = built
    if binding:
        record['admitted'] = False
        record['reasons'] = binding + record['reasons']
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
    with timing_receipts.span("arm", "v4_disk_gate"):
        receipt = w1_disk_check(w1_disk_config, gate=disk_gate)
    pilot.h.write(session / 'staging/w1_disk_gate.json', receipt)
    with timing_receipts.span("arm", "v4_installer_handoff"):
        return pilot.install(session, now=now or time.time, **kwargs)


def main(argv=None):
    return pilot.main(argv, kit=kit.KIT, pack_id=kit.PACK_ID, desk_schema=kit.DESK_SCHEMA,
                      session_prefix='align-v4-', prepare_fn=prepare, install_fn=install,
                      desk_fn=desk,
                      prepare_options=(('--window-id', dict(help='frozen series window or D alias; requires series admission')),
                                       ('--extra-sentinels', dict(type=int, default=0, choices=(0, 2),
                                           help='R20: two supplemental escalation sentinels (ordinals 23, 24) '
                                                'after a U4/U5-inconclusive window; ceiling 62,400 s'))),
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
                                       ('--next-arm-triage', dict(type=Path, required=True,
                          help='R12 B2 next-arm triage packet (JSON) built off the MBP from the committed record'))))


if __name__ == '__main__':
    from joulewise.align.apple import powermode as _powermode
    _powermode.mark_production_entry('align_v4_session')   # lead ruling R7-10
    raise SystemExit(main())
