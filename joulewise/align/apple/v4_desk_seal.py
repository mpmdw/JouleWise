"""ALIGN v4 per-window desk release guard (desk-leak audit, 2026-11-13).

The common desk (``scripts/align_pilot_session.py:desk``) computes and prints per-member residual
scores, energy on every rail, task scores, tool structure and battery discharge. In a C or T window
that breaks protocol v4 B0 (:1099-1101: the K decision, every S leaf and every C-window
sabotage-instructed leaf are computed only in the release run; incremental runs print
``withheld_until_series_complete``), B2 (:1170-1173), B9 (:1421-1424), the DC seal (:828-829,
MED-4), B7 (:1383: secondaries are computed in the release run) and R27/A25 (thresholds and T
scores withheld until ``calibration_complete``).

This module is the guard. Before release, in a C or T window, the desk prints and records only an
ALLOWLIST: per member the identity, pool role, exclusion and eligibility fields and flag codes;
every other value is replaced by ``{status: withheld_until_series_complete, sha256: <canonical
JSON>}``; the window's analyses become a hash plus window-pooled instrument figures that carry no
member or cell key. The unsealed PILOT is written to ``archive/withheld/PILOT.full.json`` (the
session's withheld archive, beside the harvest's ``archive/withheld/battery-assist.json``) for the
release run. W1 (selection data) has its own, configurable scope (:data:`W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES`).

:func:`released` is True only on a registered release event (a committed ``series_complete``
record plus a lead-signed release receipt); no such record exists today. Pure stdlib; it reads
only the two release files and the series manifest, never energy, transcript or meter bytes.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re

WITHHELD = 'withheld_until_series_complete'
WITHHELD_PILOT = 'archive/withheld/PILOT.full.json'
SERIES_MANIFEST = 'configs/campaigns/align_v4/series/series_manifest.json'
# The release event (protocol B0 :1099-1101, B2 :1173, B7 :1383): "computed only in the release run, after
# the last admitted test window's eligibility is final". The record names that window and its final
# eligibility; the receipt is the lead's signed authorization of the release run over that exact record.
SERIES_COMPLETE = 'configs/campaigns/align_v4/series/series_complete.json'
RELEASE_RECEIPT = 'configs/campaigns/align_v4/series/release_receipt.json'
SERIES_COMPLETE_SCHEMA = 'joulewise.align_v4.series_complete.v1'
RELEASE_RECEIPT_SCHEMA = 'joulewise.align_v4.release_receipt.v1'
GUARD_SCHEMA = 'joulewise.align_v4.desk_release_guard.v1'
GPU = 'powermetrics:gpu_power'

# RESEARCH-LEAD SWITCH (desk-leak audit question (a); not decided here). W1 is selection data, and its
# sabotage-instructed D members (ordinals 11 and 14) are not admitted to S. False (default) = the MINIMUM
# the existing DC seal (MED-4, protocol :828-829) already requires: for every non-benign W1 member,
# battery_discharge and all non-GPU-rail energy are withheld; the GPU rail, scores, task outcomes and
# tool structure print as before. True = ALSO withhold every non-benign W1 member's GPU-rail energy and
# residual/transfer/tamper scores, task outcomes and tool structure (the C/T member allowlist).
W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES = False

# Per member (PILOT.json ``members`` and the printed member lines): what the harvest-off ``final``
# (light_triage.final_adjudication_error + member_eligibility), the packet builder and the full-desk
# gate need, and nothing else. Every other field is folded into one ``withheld`` digest, so not even
# a withheld key name is printed.
MEMBER_ALLOWLIST = ('run_id', 'ordinal', 'pool_role', 'readable', 'excluded', 'exclusion_codes',
                    'disclosed_exclusion_codes', 'chain_eligible', 'chain_reasons', 'target_precheck_eligible',
                    'window_evidence_precheck', 'harvest_flag_codes')
# PILOT.json top level kept verbatim (light_triage.final_adjudication_error reads plan_id, status,
# members_excluded and members_disclosure_only; the packet builder reads checks and the desk status).
TOP_ALLOWLIST = ('schema_version', 'non_claim', 'session_id', 'plan_id', 'runs_root', 'checks',
                 'registered_eligible_members', 'exclusions_path', 'members_excluded',
                 'members_disclosure_only', 'harvest_flags_status', 'status')
# The v4 extra report (``powermode_desk_check``) kept verbatim.
EXTRA_ALLOWLIST = ('instrument_ok', 'powermode_mismatches', 'series', 'pool_members', 'calibration_counts_final',
                   'calibration_counts_note', 'registration_error', 'series_desk_row')
# Thermal desk records: what light_triage (id, excluded, calibration_exclusions), the U-check/escalation
# readers and the next-arm packet builder read: X1-X8 fault tabulation (flags, coverage, pm_period_s,
# pm_max_gap_s, model, gated), the D cohort assertion (configuration = the frozen spec slots, cohort_identity
# = model/runtime identity) and the X5/U3 identity reconstruction (identical_work_group, compare_reference_id,
# and ``tokens``, which is replaced by its sha256: equal digests iff equal tokens, None stays None).
# Per-turn observations, energy, tool calls, waits and battery are withheld.
THERMAL_MEMBER_ALLOWLIST = ('id', 'ordinal', 'pool_role', 'role', 'model', 'window', 'stage', 'gated',
                            'excluded', 'calibration_exclusions', 'coverage', 'pm_period_s', 'pm_max_gap_s',
                            'supplemental', 'identical_work_group', 'compare_reference_id', 'replay_of',
                            'configuration', 'cohort_identity')
U3_PAIR_KEEP = ('status', 'exclusion', 'token_identical')
MODEL_WINDOW_KEEP = ('hardware_control', 'monitoring_calibration', 'consequence')
BATTERY_WINDOW_KEEP = ('B_count', 'unobserved_count', 'assist_count', 'assist_outside_request_count',
                       'bar_pass', 'status', 'consequence')
KM003C_KEEP = ('schema', 'label', 'print_only', 'measurement', 'residual', 'fit', 'uncertainty', 'detail')
X2_ROW_KEEP = ('run_id', 'ordinal', 'g0_outcome', 'g0_timeout_x2', 'gate_timeout_x2', 'x2')
X2_KEEP = ('print_only', 'authority', 'd_members', 'read', 'unread', 'x2_count', 'g0_timeout_x2_count', 'x2_rate')


def canonical_sha256(value):
    """sha256 of the canonical JSON (sorted keys, no whitespace) of ``value``."""
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def withheld(value):
    return {'status': WITHHELD, 'sha256': canonical_sha256(value)}


def _code(flag):
    """A flag's code: the string up to its first ':' (values after it are withheld)."""
    if isinstance(flag, dict):
        flag = flag.get('code')
    return str(flag).split(':')[0] if flag is not None else None


def _codes(flags):
    return sorted({c for c in (_code(f) for f in flags or ()) if c})


# --- the release event ---------------------------------------------------------------------------

def _load(path):
    try:
        raw = Path(path).read_bytes()
        return raw, json.loads(raw)
    except (OSError, ValueError):
        return None, None


def release_error(root):
    """``None`` when ``root`` holds a registered release event, else why not (fail closed).

    ``series_complete.json`` (schema :data:`SERIES_COMPLETE_SCHEMA`)::

        {"schema": ..., "event": "series_complete", "last_admitted_test_window": "T<k>",
         "test_windows_final_eligibility": {"T1": "final", ..., "T<k>": "final"},
         "series_manifest_sha256": <sha256 of the frozen series manifest bytes>,
         "record_commit": <40-hex commit that recorded the series' last final eligibility>}

    ``release_receipt.json`` (schema :data:`RELEASE_RECEIPT_SCHEMA`)::

        {"schema": ..., "release_run": true, "series_complete_sha256": <sha256 of series_complete.json>,
         "lead_signature": "lead: <name/session> <YYYY-MM-DD>"}
    """
    if root is None:
        return 'no measurement root'
    root = Path(root)
    raw, record = _load(root / SERIES_COMPLETE)
    if not isinstance(record, dict):
        return 'no series_complete record'
    if record.get('schema') != SERIES_COMPLETE_SCHEMA or record.get('event') != 'series_complete':
        return 'series_complete record malformed'
    last = record.get('last_admitted_test_window')
    final = record.get('test_windows_final_eligibility')
    if (not isinstance(last, str) or not re.fullmatch(r'T[1-9][0-9]*', last) or not isinstance(final, dict)
            or last not in final or not final or any(v != 'final' for v in final.values())):
        return "series_complete does not record the last admitted test window's final eligibility"
    if not isinstance(record.get('record_commit'), str) or not re.fullmatch(r'[0-9a-f]{40}', record['record_commit']):
        return 'series_complete names no committed record'
    try:
        manifest = (root / SERIES_MANIFEST).read_bytes()
    except OSError:
        return 'series manifest unreadable'
    if record.get('series_manifest_sha256') != hashlib.sha256(manifest).hexdigest():
        return 'series_complete is bound to another series manifest'
    _raw, receipt = _load(root / RELEASE_RECEIPT)
    if not isinstance(receipt, dict) or receipt.get('schema') != RELEASE_RECEIPT_SCHEMA:
        return 'no release receipt'
    if receipt.get('release_run') is not True or receipt.get('series_complete_sha256') != hashlib.sha256(raw).hexdigest():
        return 'release receipt does not authorize this series_complete record'
    from scripts.align_v4_kit import valid_lead_signature
    if not valid_lead_signature(receipt.get('lead_signature')):
        return 'release receipt is not lead-signed'
    return None


def released(state):
    """True only on a registered release event (see :func:`release_error`). Today: always False."""
    state = state or {}
    root = state.get('source_measurement_root') or state.get('measurement_root')
    return release_error(root) is None


# --- scope ---------------------------------------------------------------------------------------

def window_id(state):
    return ((state or {}).get('v4_series') or {}).get('window_id', 'W1')


def window_scope(state):
    """``'W1'`` (selection), ``'C'`` (calibration) or ``'T'`` (test). Anything else seals as C/T."""
    series = (state or {}).get('v4_series') or {}
    wid, role = series.get('window_id', 'W1'), series.get('role')
    if wid == 'W1' and role in (None, 'selection'):
        return 'W1'
    if role == 'test' or (role is None and str(wid).startswith('T')):
        return 'T'
    return 'C'      # calibration, a D alias, or an unknown role: fail closed to the C/T seal


def _nonbenign(plan_members, pilot_members=()):
    conditions = {m.get('run_id'): m.get('condition') for m in plan_members or ()}
    for m in pilot_members or ():
        conditions.setdefault(m.get('run_id'), m.get('condition'))
    return {rid for rid, c in conditions.items() if c != 'benign'}


# --- members -------------------------------------------------------------------------------------

def _eligibility(member):
    summary = member.get('summary')
    out = {'readable': summary is not None}
    if summary:
        pre = summary.get('window_evidence_precheck') or {}
        out.update(chain_eligible=summary.get('chain_eligible'),
                   chain_reasons=list(pre.get('reasons') or []) + list(summary.get('exclusion_codes') or []),
                   target_precheck_eligible=pre.get('eligible'),
                   window_evidence_precheck={r['window']: {'eligible': r.get('eligible'), 'reasons': r.get('reasons')}
                                             for r in pre.get('windows') or () if isinstance(r, dict) and 'window' in r})
    else:
        out.update(chain_eligible=False, chain_reasons=['member.unreadable'])
    return out


def seal_member(member, plan_row=None):
    """One PILOT member reduced to :data:`MEMBER_ALLOWLIST` plus one ``withheld`` digest of the rest."""
    plan_row = plan_row or {}
    view = {'run_id': member.get('run_id'), 'ordinal': member.get('ordinal', plan_row.get('ordinal')),
            'pool_role': plan_row.get('pool_role', member.get('pool_role')),
            'excluded': member.get('excluded'), 'exclusion_codes': member.get('exclusion_codes'),
            'disclosed_exclusion_codes': member.get('disclosed_exclusion_codes', []),
            'harvest_flag_codes': _codes(member.get('harvest_flags')), **_eligibility(member)}
    view = {k: view[k] for k in MEMBER_ALLOWLIST if k in view}
    rest = {k: v for k, v in member.items() if k not in view or view[k] != v}
    view['withheld'] = withheld(rest)
    return view


def seal_line(run_id, record):
    """A printed member line (``harvest_flags`` / ``detail`` / ``unreadable``) reduced to the allowlist."""
    out = {'harvest_flags': {'flag_codes': _codes((record.get('harvest_flags') or {}).get('flags')),
                             'withheld': withheld(record.get('harvest_flags'))}}
    detail = record.get('detail') or {}
    keep = {k: detail[k] for k in MEMBER_ALLOWLIST if k in detail}
    keep['withheld'] = withheld({k: v for k, v in detail.items() if k not in keep})
    out['detail'] = keep
    if 'unreadable' in record:
        out['unreadable'] = str(record['unreadable']).split(':')[0] + ' (message ' + WITHHELD + ')'
    return out


# --- window analyses: hash plus window-pooled instrument figures (no member or cell key) -----------

def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def pooled_residuals(analysis):
    scopes = {}
    for configuration in analysis or ():
        for scope, block in (configuration.get('scopes') or {}).items():
            for label, convention in block.items():
                if not isinstance(convention, dict) or 'residuals' not in convention:
                    continue
                row = scopes.setdefault(scope, {}).setdefault(label, {
                    'members_scored': 0, 'members_with_finite_score': 0, 'fit_flags': set(), 's_r_df': 0})
                residuals = convention.get('residuals') or []
                row['members_scored'] += len(residuals)
                row['members_with_finite_score'] += sum(_finite(r.get('score')) for r in residuals)
                row['fit_flags'] |= set(convention.get('flags') or ())
                row['s_r_df'] += convention.get('s_r_df') or 0
    for block in scopes.values():
        for row in block.values():
            row['fit_flags'] = sorted(row['fit_flags'])
    return {'configurations': len(analysis or ()), 'scopes': scopes}


def pooled_i4(i4):
    def tally(rows):
        out = {}
        for r in rows if isinstance(rows, list) else ():
            status = r.get('status') if isinstance(r, dict) else None
            out[str(status)] = out.get(str(status), 0) + 1
        return out
    cells = list((i4 or {}).values())
    replays = [r for c in cells if isinstance(c.get('replay_identity'), list) for r in c['replay_identity']]
    merge = lambda field: {k: sum(tally(c.get(field)).get(k, 0) for c in cells)
                           for k in sorted({k for c in cells for k in tally(c.get(field))})}
    return {'cells': len(cells), 'replay_pairs': len(replays),
            'replay_identical': sum(r.get('status') == 'identical' for r in replays),
            'accounting': merge('accounting'), 'sampler_provenance': merge('sampler_provenance'),
            'independent_seed_observations': sum(len((c.get('independent_seed_distinct') or {}).get('observations') or ())
                                                 for c in cells)}


def pooled_spreads(spreads):
    pairs = {(r.get('original'), r.get('replay')) for rows in (spreads or {}).values() for r in rows or ()}
    return {'replay_pairs': len(pairs),
            'channels': sorted({r.get('channel') for rows in (spreads or {}).values() for r in rows or ()})}


def pooled_raw(raw):
    return {'cells': len(raw or {}), 'channels': sorted({ch for cell in (raw or {}).values() for ch in cell})}


def pooled_identity(identity):
    values = list((identity or {}).values())
    return {'cells': len(values), 'identical': sum(v is True for v in values),
            'not_identical': sum(v is False for v in values), 'not_evaluated': sum(v == 'not_evaluated' for v in values)}


def _sealed_block(value, pooled):
    return {**withheld(value), 'pooled': pooled}


# --- the v4 extra report ---------------------------------------------------------------------------

def _seal_dc_rows(dc, run_ids):
    """km003c rows of ``run_ids`` sealed (status and flags kept); MED-4-sealed rows stay as they are."""
    members = {}
    for rid, row in (dc.get('members') or {}).items():
        if rid in run_ids and isinstance(row, dict) and not row.get('sealed'):
            row = {'label': row.get('label'), 'print_only': True, 'sealed': True, 'sealed_sha256': canonical_sha256(row),
                   'status': row.get('status'), 'flags': list(row.get('flags') or ()), 'sealed_until': 'series_complete'}
        members[rid] = row
    return {**dc, 'members': members}


def seal_dc(dc, plan_members):
    """C/T: every member's DC row is sealed (energy on every rail, protocol B0); top-level fits withheld."""
    if not isinstance(dc, dict):
        return dc
    sealed = _seal_dc_rows(dc, set(dc.get('members') or {}))
    out = {k: sealed[k] for k in KM003C_KEEP if k in sealed}
    out['members'] = sealed['members']
    rest = {k: v for k, v in dc.items() if k not in out}
    if set(rest) == {'withheld'}:           # already sealed (the desk prints seal first): idempotent
        out['withheld'] = rest['withheld']
    elif rest:
        out['withheld'] = withheld(rest)
    return out


def seal_balance(report):
    """C/T: R22-3's exposure is member time (B7 time baseline); the report is withheld, members counted."""
    if not isinstance(report, dict):
        return report
    return {'status': report.get('status'), 'authority': report.get('authority'),
            **_sealed_block(report, {'members': (report.get('total') or {}).get('members'),
                                     'members_without_exposure_or_condition': len(report.get('members_without_exposure_or_condition') or ())})}


def balance_lines(report):
    return [f"balance (R22-3): {WITHHELD} sha256={report.get('sha256')} "
            f"members={(report.get('pooled') or {}).get('members')} (print only)"]


def _seal_thermal_member(record):
    view = {k: record[k] for k in THERMAL_MEMBER_ALLOWLIST if k in record}
    view['flags'] = _codes(record.get('flags'))
    if 'tokens' in record:
        view['tokens'] = None if record['tokens'] is None else 'sha256:' + canonical_sha256(record['tokens'])
    view['withheld'] = withheld({k: v for k, v in record.items() if k not in view or k in ('flags', 'tokens')})
    return view


def _seal_model_window(result):
    view = {f'U{k}': {'status': (result.get(f'U{k}') or {}).get('status')} for k in range(1, 7) if f'U{k}' in result}
    pairs = (result.get('U3') or {}).get('pairs')
    if isinstance(pairs, list) and 'U3' in view:
        view['U3']['pairs'] = [{k: p[k] for k in U3_PAIR_KEEP if k in p} for p in pairs if isinstance(p, dict)]
    view.update({k: result[k] for k in MODEL_WINDOW_KEEP if k in result})
    view['withheld'] = withheld(result)
    return view


def seal_thermal(thermal, run_ids=None):
    """Thermal desk section: U statuses and the allowlisted member fields; ``run_ids`` None = every member."""
    if not isinstance(thermal, dict):
        return thermal
    out = {'schema': thermal.get('schema')}
    if run_ids is None:
        out['model_windows'] = {k: _seal_model_window(v) for k, v in (thermal.get('model_windows') or {}).items()}
    else:
        out['model_windows'] = thermal.get('model_windows')
    out['members'] = [_seal_thermal_member(r) if (run_ids is None or r.get('id') in run_ids) else r
                      for r in thermal.get('members') or ()]
    rest = {k: v for k, v in thermal.items() if k not in ('schema', 'model_windows', 'members')}
    if run_ids is None:
        out['withheld'] = withheld(rest)
    else:
        for key, value in rest.items():
            out[key] = withheld(value) if key == 'deciding_experiment' else value
    return out


def seal_registration_diagnostics(diag):
    if not isinstance(diag, dict):
        return diag
    out = {}
    windows = diag.get('battery_windows')
    if isinstance(windows, dict):
        out['battery_windows'] = {k: {**{f: row[f] for f in BATTERY_WINDOW_KEEP if f in row}, 'withheld': withheld(row)}
                                  for k, row in windows.items()}
    cohort = diag.get('d_cohort')
    if isinstance(cohort, dict):
        out['d_cohort'] = {'instrument_ok': cohort.get('instrument_ok'), 'withheld': withheld(cohort)}
    sentinel = diag.get('sentinel')
    if isinstance(sentinel, dict):
        out['sentinel'] = {'ordinal': sentinel.get('ordinal'),
                           'candidates': {str(k): {'admissible': (v or {}).get('admissible'),
                                                   'requirements': (v or {}).get('requirements')}
                                          for k, v in (sentinel.get('candidates') or {}).items()},
                           'withheld': withheld(sentinel)}
    rest = {k: v for k, v in diag.items() if k not in out}
    if rest:
        out['withheld'] = withheld(rest)
    return out


def _seal_x2(report):
    if not isinstance(report, dict):
        return report
    out = {k: report[k] for k in X2_KEEP if k in report}
    out['members'] = [{k: r[k] for k in X2_ROW_KEEP if k in r} for r in report.get('members') or ()]
    out['withheld'] = withheld(report)
    return out


def seal_extra(extra, plan_members, scope, *, w1_withhold=None):
    """The v4 extra report (``powermode_desk_check``) for ``scope``; also the light triage's record source."""
    if not isinstance(extra, dict):
        return extra
    if scope == 'W1':
        return _seal_extra_w1(extra, plan_members, W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES if w1_withhold is None else w1_withhold)
    out = {k: extra[k] for k in EXTRA_ALLOWLIST if k in extra}
    for key, value in extra.items():
        if key in out:
            continue
        if key == 'km003c':
            out[key] = seal_dc(value, plan_members)
        elif key == 'thermal':
            out[key] = seal_thermal(value)
        elif key == 'registration_diagnostics':
            out[key] = seal_registration_diagnostics(value)
        elif key == 'balance_check':
            out[key] = value if isinstance(value, dict) and value.get('status') == WITHHELD else seal_balance(value)
        elif key == 'd_member_x2':
            out[key] = _seal_x2(value)
        else:
            out[key] = withheld(value)
    return out


def _seal_extra_w1(extra, plan_members, withhold):
    nonbenign = _nonbenign(plan_members)
    out = dict(extra)
    if isinstance(extra.get('km003c'), dict):
        # MED-4 already seals non-benign DC rows; re-apply so the guard never depends on the caller.
        out['km003c'] = _seal_dc_rows(extra['km003c'], nonbenign)
    thermal = extra.get('thermal')
    if isinstance(thermal, dict):
        if withhold:
            out['thermal'] = seal_thermal(thermal, nonbenign)
        else:
            out['thermal'] = {**thermal, 'members': [
                {**r, 'battery': withheld(r['battery'])} if r.get('id') in nonbenign and 'battery' in r else r
                for r in thermal.get('members') or ()]}
    diag = extra.get('registration_diagnostics')
    if isinstance(diag, dict):
        diag = dict(diag)
        if isinstance(diag.get('battery_windows'), dict):
            diag['battery_windows'] = {k: {**row, 'members': [
                withheld(m) if m.get('id') in nonbenign else m for m in row.get('members') or ()]}
                if isinstance(row, dict) else row for k, row in diag['battery_windows'].items()}
        if withhold and isinstance(diag.get('rebuilds'), list):
            diag['rebuilds'] = [withheld(r) if r.get('id') in nonbenign else r for r in diag['rebuilds']]
        out['registration_diagnostics'] = diag
    return out


# --- PILOT ---------------------------------------------------------------------------------------

def seal_pilot(pilot, plan_members, window_id_, *, scope=None, w1_withhold=None):
    """The PILOT a C/T (or W1) desk may record and print before release (allowlist; fail closed)."""
    scope = scope or ('W1' if window_id_ == 'W1' else 'T' if str(window_id_).startswith('T') else 'C')
    if scope == 'W1':
        return _seal_pilot_w1(pilot, plan_members, W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES if w1_withhold is None else w1_withhold)
    rows = {m.get('run_id'): m for m in plan_members or ()}
    out = {k: pilot[k] for k in TOP_ALLOWLIST if k in pilot}
    pooled = {'residual_analysis': pooled_residuals, 'raw_within_cell_energy_sd': pooled_raw,
              'repeat_energy_spread': pooled_spreads, 'I4_prime': pooled_i4, 'repeat_token_identity': pooled_identity}
    for key, value in pilot.items():
        if key in out:
            continue
        if key == 'members':
            out[key] = [seal_member(m, rows.get(m.get('run_id'))) for m in value]
        elif key in pooled:
            out[key] = _sealed_block(value, pooled[key](value))
        elif key == 'session_harvest_flags':
            out[key] = {'flag_codes': _codes(value), 'withheld': withheld(value)}
        elif key == 'extra_checks':
            out[key] = seal_extra(value, plan_members, scope)
        elif key == 'cross_pilot_token_identity' and value is None:
            out[key] = None
        elif key in ('episode_scope_alternative_eligible_members', 'episode_scope_alternative_ineligible_reasons'):
            out[key] = _sealed_block(value, {'members': len(value or ())})
        else:
            out[key] = withheld(value)
    return out


def _cells_of(members, run_ids):
    from joulewise.align.apple.pilot_analysis import cell_key
    return {cell_key(m) for m in members if m.get('run_id') in run_ids}


def _in_cells(key, cells):
    return any(key == c or key.startswith(c + '/configuration=') for c in cells)


def _seal_pilot_w1(pilot, plan_members, withhold):
    members = pilot.get('members') or []
    nonbenign = _nonbenign(plan_members, members)
    rows = {m.get('run_id'): m for m in plan_members or ()}
    cells = _cells_of(members, nonbenign)
    out = dict(pilot)

    def minimum(member):
        member = dict(member)
        if 'battery_discharge' in member:
            member['battery_discharge'] = withheld(member['battery_discharge'])
        summary = member.get('summary')
        if isinstance(summary, dict) and isinstance(summary.get('energy'), dict):
            other = {ch: v for ch, v in summary['energy'].items() if ch != GPU}
            energy = {ch: v for ch, v in summary['energy'].items() if ch == GPU}
            if other:
                energy['non_gpu_rails'] = withheld(other)
            member['summary'] = {**summary, 'energy': energy}
        return member
    out['members'] = [(seal_member(m, rows.get(m.get('run_id'))) if withhold else minimum(m))
                      if m.get('run_id') in nonbenign else m for m in members]
    raw = pilot.get('raw_within_cell_energy_sd')
    if isinstance(raw, dict):
        out['raw_within_cell_energy_sd'] = {
            key: ((withheld(cell) if withhold else {ch: (v if ch == GPU else withheld(v)) for ch, v in cell.items()})
                  if _in_cells(key, cells) else cell) for key, cell in raw.items()}
    spreads = pilot.get('repeat_energy_spread')
    if isinstance(spreads, dict):
        out['repeat_energy_spread'] = {
            key: ([r if (not withhold and r.get('channel') == GPU) else withheld(r) for r in entries]
                  if _in_cells(key, cells) else entries) for key, entries in spreads.items()}
    if withhold and isinstance(pilot.get('residual_analysis'), list):
        out['residual_analysis'] = [_seal_residual_rows(c, nonbenign) for c in pilot['residual_analysis']]
    if 'extra_checks' in pilot:
        out['extra_checks'] = _seal_extra_w1(pilot['extra_checks'], plan_members, withhold)
    return out


def _seal_residual_rows(configuration, run_ids):
    scopes = {}
    for scope, block in (configuration.get('scopes') or {}).items():
        block = dict(block)
        for label, convention in list(block.items()):
            if not isinstance(convention, dict) or 'residuals' not in convention:
                continue
            convention = dict(convention)
            convention['residuals'] = [withheld(r) if r.get('run_id') in run_ids else r for r in convention['residuals']]
            convention['cross_pair_transfer'] = [
                {**t, 'scores': [withheld(s) if s.get('run_id') in run_ids else s for s in t.get('scores') or ()]}
                for t in convention.get('cross_pair_transfer') or ()]
            convention['tamper_detection_curve'] = withheld(convention.get('tamper_detection_curve'))
            block[label] = convention
        scopes[scope] = block
    return {**configuration, 'scopes': scopes}


def seal_w1_line(run_id, record, nonbenign, withhold):
    if run_id not in nonbenign:
        return record
    if withhold:
        return seal_line(run_id, record)
    flags = dict(record.get('harvest_flags') or {})
    if 'battery_discharge' in flags:
        flags['battery_discharge'] = withheld(flags['battery_discharge'])
    return {**record, 'harvest_flags': flags}


# --- the desk hook -------------------------------------------------------------------------------

def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n'
    temporary = path.with_name('.' + path.name + '.tmp')
    temporary.write_text(raw)
    os.replace(temporary, path)
    return hashlib.sha256(raw.encode()).hexdigest()


class DeskSeal:
    """``print_policy`` for ``align_pilot_session.desk``: (pilot, member lines) -> what may be recorded/printed.

    Writes the unsealed PILOT to ``<output>/archive/withheld/PILOT.full.json`` (``output`` is the session
    for a harvested desk, its inspection directory for ``--no-harvest``) and keeps it in ``full`` for the
    caller's in-memory gates (the v4 full-desk gate re-derives exclusion checks from the full members).
    """

    def __init__(self, plan_members, window_id_, scope, *, w1_withhold=None):
        # A list, or a zero-argument callable read when the desk applies the policy (the roster read stays
        # where the common desk reads it).
        self._plan_members = plan_members
        self.window_id = window_id_
        self.scope = scope
        self.w1_withhold = W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES if w1_withhold is None else w1_withhold
        self.full = None

    @property
    def plan_members(self):
        members = self._plan_members() if callable(self._plan_members) else self._plan_members
        return list(members or ())

    def __call__(self, pilot, lines, *, output):
        self.full = pilot
        self._plan_members = self.plan_members      # resolve once
        digest = _write_json(Path(output) / WITHHELD_PILOT, pilot)
        sealed = seal_pilot(pilot, self.plan_members, self.window_id, scope=self.scope, w1_withhold=self.w1_withhold)
        if self.scope == 'W1':
            nonbenign = _nonbenign(self.plan_members, pilot.get('members'))
            lines = [(rid, seal_w1_line(rid, record, nonbenign, self.w1_withhold)) for rid, record in lines]
        else:
            lines = [(rid, seal_line(rid, record)) for rid, record in lines]
        sealed['release_guard'] = {
            'schema': GUARD_SCHEMA, 'status': WITHHELD, 'window_id': self.window_id, 'scope': self.scope,
            'w1_withhold_sabotage_gpu_and_outcomes': self.w1_withhold if self.scope == 'W1' else None,
            'withheld_pilot': WITHHELD_PILOT, 'withheld_pilot_sha256': digest,
            'opens': 'release run (registered series_complete record plus lead-signed release receipt)'}
        return sealed, lines


def desk_policy(state, plan_members, *, w1_withhold=None):
    """The v4 desk's ``print_policy`` for ``state``; ``None`` (identity) once the series is released."""
    if released(state):
        return None
    return DeskSeal(plan_members, window_id(state), window_scope(state), w1_withhold=w1_withhold)


def sealed_scope(state):
    """The scope whose extra report and prints are sealed now, or ``None`` once released."""
    return None if released(state) else window_scope(state)
