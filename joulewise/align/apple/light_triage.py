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
PAIR_OF_TASK = {'spam_filter_update': 'spam', 'bank_transfer_2': 'bank'}


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

    ``status`` is the triage status: ``pass`` when no U1-U3 failed, or when one
    failed and the escalation ladder step is already recorded for the next plan
    (applied before use, never in place); otherwise ``fail``.
    """
    models = {key: {f'U{n}': result[f'U{n}']['status'] for n in (1, 2, 3)}
              for key, result in sorted(thermal_report['model_windows'].items())}
    failed = sorted(key for key, row in models.items() if 'fail' in row.values())
    return {'schema': SCHEMA, 'check': 'thermal_escalation', 'models': models,
            'escalation_required': bool(failed), 'failed_model_windows': failed,
            'checks': u_checks(thermal_report),
            'status': 'pass' if not failed or ladder_recorded is True else 'fail'}


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
    """Default fresh-benign calibrator predicate (the D series manifest may override)."""
    return row.get('role') == 'D' and row.get('condition') == 'benign' and row.get('task_pair') in PAIR_OF_TASK


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
