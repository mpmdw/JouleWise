"""Light next-arm triage for ``thermal_escalation`` and ``member_eligibility`` (HARVEST-OFF-opus).

The full v4 desk (``scripts/align_v4_session.py:powermode_desk_check``) builds one
thermal record per plan member from the bundle bytes, then applies the harvest's
member exclusion codes (:func:`apply_harvest_codes`), then runs
``thermal_desk.window_report``. The light triage runs the SAME record builder and
the SAME ``window_report`` without waiting for the harvest.

* ``thermal_escalation`` (U1-U3) is identical: ``window_report`` reads the harvest
  only through ``excluded`` (used by the contrast, never by U1-U3) and the
  ``battery.member_span`` flag (used by the B printout, never by U1-U3).
  ``tests/align/test_harvest_off.py`` proves the invariance on synthetic records.
* ``member_eligibility`` is PROVISIONAL: the harvest can only remove members
  (final eligible is a subset of provisional eligible), and the captured-member
  count, which is all the fixed-8 predicate reads before 8 counted windows, is
  identical. Counts become final only from the full desk on the verified copy;
  ``v4_cadence.calibration_stop`` already refuses with
  ``pending_final_eligibility`` at 8 counted windows while any row is provisional.

No score, alarm, residual or outcome-bearing energy is read for any decision here:
U1-U3 are the registered thermal-protocol checks, and eligibility uses exclusion
codes and capture presence only.
"""
from __future__ import annotations

SCHEMA = 'joulewise.align_v4.light_triage.v1'
PAIR_OF_TASK = {'spam_filter_update': 'spam', 'bank_transfer_2': 'bank', 'spam': 'spam', 'bank': 'bank'}


def apply_harvest_codes(record, codes):
    """The full desk's harvest step for one thermal record (moved here verbatim).

    ``codes`` are the harvest's member exclusion codes (``exclusions.json``).
    """
    if any(str(c).startswith('battery.member_span') for c in codes):
        record['flags'].append('battery.member_span')
    record['excluded'] = bool(codes) or bool(record.get('calibration_exclusions'))
    return record


def u_checks(thermal_report):
    """The desk's per-model U1-U3 instrument checks from a ``window_report``."""
    checks = {}
    for model, result in thermal_report['model_windows'].items():
        for n in (1, 2, 3):
            checks[f'v4_{model}_U{n}'] = result[f'U{n}']['status'] == 'pass'
    return checks


def thermal_escalation(thermal_report, *, ladder_recorded=False):
    """U1-U3 verdict per model/window and whether the registered ladder is owed.

    ``status`` is the triage status: ``pass`` when every U1-U3 passed, or when one did
    not and the escalation ladder step is already recorded for the next plan (applied
    before use, never in place); otherwise ``fail``. A status that is not ``pass``
    (``fail`` or ``inconclusive``) owes the registered consequence, exactly as the
    packet builder's ``thermal_escalation`` check reads it (R17 review F6).
    """
    models = {key: {f'U{n}': result[f'U{n}']['status'] for n in (1, 2, 3)}
              for key, result in sorted(thermal_report['model_windows'].items())}
    failed = sorted(key for key, row in models.items() if 'fail' in row.values())
    non_pass = sorted(key for key, row in models.items() if any(v != 'pass' for v in row.values()))
    return {'schema': SCHEMA, 'check': 'thermal_escalation', 'models': models,
            'escalation_required': bool(non_pass), 'failed_model_windows': failed,
            'non_pass_model_windows': non_pass, 'checks': u_checks(thermal_report),
            'status': 'pass' if not non_pass or ladder_recorded is True else 'fail'}


def _eligible(record):
    # Full desk: ``excluded`` = harvest codes or calibration exclusions.
    # Light: the harvest step has not run, so only calibration exclusions.
    return not record.get('excluded', bool(record.get('calibration_exclusions')))


def member_eligibility(records, plan_rows, *, captured, final):
    """Per-member eligibility for the triage packet.

    ``records`` are thermal records (after :func:`apply_harvest_codes` for the
    full desk, before it for the light triage); ``plan_rows`` the window's plan
    members; ``captured`` the run ids whose bundle exists in the committed
    record; ``final`` True only for the full desk on the verified copy.
    """
    by_id = {r['id']: r for r in records}
    members = {}
    for row in plan_rows:
        rid = row['run_id']
        record = by_id.get(rid)
        is_captured = rid in captured
        eligible = bool(is_captured and record is not None and _eligible(record))
        reasons = sorted(record.get('calibration_exclusions') or []) if record is not None else ['member.no_record']
        if record is not None and record.get('excluded') and not record.get('calibration_exclusions'):
            reasons = ['harvest.excluded']
        members[rid] = {'captured': is_captured, 'eligible': eligible,
                        'reasons': [] if eligible else (reasons or ['member.not_captured'])}
    return {'schema': SCHEMA, 'check': 'member_eligibility',
            'stage': 'final' if final else 'provisional', 'members': members,
            'eligible': sorted(rid for rid, m in members.items() if m['eligible']),
            'captured_members': sum(m['captured'] for m in members.values()),
            # The adjudication is complete when every plan member is classified.
            'status': 'pass' if len(members) == len({r['run_id'] for r in plan_rows}) else 'fail'}


def is_calibrator(row):
    """Fresh-benign calibrator, as the packet builder counts it (delta5): only the frozen calibration
    pool (``pool_role``) when the roster carries pool metadata, never a supplemental sentinel."""
    in_pool = row.get('pool_role') == 'calibration' if 'pool_role' in row else True
    return (in_pool and not row.get('supplemental') and row.get('role') == 'D'
            and row.get('condition') == 'benign' and row.get('task_pair') in PAIR_OF_TASK)


def calibration_row(window_id, plan_rows, eligibility, *, calibrator=is_calibrator):
    """The ``v4_cadence.calibration_stop`` row for one window from an eligibility verdict."""
    counts = dict.fromkeys(PAIR_OF_TASK.values(), 0)
    for row in plan_rows:
        if calibrator(row) and eligibility['members'][row['run_id']]['eligible']:
            counts[PAIR_OF_TASK[row['task_pair']]] += 1
    # A zero-capture window has nothing a harvest could exclude: its row is final at once
    # (v4_cadence treats a provisional zero-capture row as unfinished and holds the gate).
    status = 'final' if eligibility['captured_members'] == 0 else eligibility['stage']
    return {'window': window_id, 'status': status,
            'captured_members': eligibility['captured_members'], 'eligible_benign': counts}


# R17 review F4 and delta D9: ONE finality predicate, used by the runner's ``final`` and by the packet
# builder's ``WindowRecord``. A completed harvest whose exclusions the desk recorded, a completed desk
# adjudication, both bound to this window's plan, and exclusions agreeing with what the desk recorded.
COMPLETED_HARVEST = ('ok', 'members_excluded')
DESK_ADJUDICATIONS = ('instrument_ok', 'instrument_incomplete')


def final_adjudication_error(desk, pilot, exclusions, plan_id, *, captured):
    """``None`` when ``desk``/``pilot``/``exclusions`` are a final adjudication of the plan ``plan_id``.

    ``captured``: whether the window holds ANY capture (supplemental ones included; delta D5). Only a
    window with no capture at all has nothing to harvest, so only it may carry a desk whose harvest
    did not run. A completed desk that did not PASS is still final.
    """
    if not isinstance(desk, dict) or desk.get('status') == 'running_off_mbp':
        return 'the desk recorded no completed harvest (still running off the MBP)'
    if desk.get('harvest_status') not in COMPLETED_HARVEST and captured:
        return 'the desk recorded no completed harvest (harvest_status ' + str(desk.get('harvest_status')) + ')'
    if desk.get('plan_id') != plan_id or not isinstance(pilot, dict) or pilot.get('plan_id') != plan_id:
        return "the desk and PILOT.json are not bound to this window's plan"
    if pilot.get('status') not in DESK_ADJUDICATIONS:
        return 'PILOT.json carries no completed desk adjudication (status ' + str(pilot.get('status')) + ')'
    if not isinstance(exclusions, dict) or not isinstance(exclusions.get('members_excluded'), list):
        return 'final exclusions missing'
    # R22-1: contention is disclosure-only, so each record's exclusions are read together with its
    # ``members_disclosure_only`` map (the same comparison ``effective_desk`` makes) before they are compared
    # with the committed harvest exclusions. A real exclusion must still agree exactly (members and codes).
    from joulewise.align.apple import v4_contention
    if any(record.get('members_excluded') is not None
           and not v4_contention.records_agree_with_harvest(record, exclusions['members_excluded'])
           for record in (desk, pilot)):
        return 'desk, PILOT.json and exclusions disagree'
    return None
