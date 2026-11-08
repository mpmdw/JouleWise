"""R12 window cadence (RUN_STATE 214/215/217): next-arm triage list and fixed-8 calibration.

Pure stdlib. No probes, no scores, no outcome fields: the calibration predicate
sees only window status and eligible benign counts per pair, so blinding holds.
Neither function qualifies exchangeability or satisfies R13/R14; counts alone do
not settle them (RUN_STATE 217: a count stop raised FPR under window drift, so
calibration is exactly 8 windows).
"""
from __future__ import annotations

import hashlib
import json
import re

TRIAGE_SCHEMA = 'joulewise.align_v4.next_arm_triage.v1'
# Evidence an arm computes itself (cannot be supplied by the packet) vs the
# packet built off the MBP from the committed record and the laptop desk.
ARM = 'arm_checks'
PACKET = 'packet'
DERIVED = 'derived'      # computed here from packet counts by calibration_stop

# B2: the frozen, enumerated next-arm triage list. Every check whose result
# changes the next window's plan is here and GATING, except ``gating=False`` rows,
# which are tabulations recorded in the arm record. Nothing that gated before R12
# becomes non-gating by omission. ``first_window_na`` marks checks that summarize a
# previous v4 window and so may read not_applicable for W1 (previous window is R1) only.
NEXT_ARM_TRIAGE = (
    dict(id='record_committed', source=PACKET, first_window_na=False,
         text='previous window record finalized, hashed, committed and pushed'),
    dict(id='terminal_completion', source=PACKET, first_window_na=False,
         text='authenticated terminal completion: terminal result, chain closure, courier '
              'delivery and the watchdog empty-process latch (B1; not a direct-child exit)'),
    dict(id='quiet_start_state', source=PACKET, first_window_na=False,
         text='machine back in the quiet start state: cool-down and display/quiet dwell, '
              'no desk, hashing or evidence traffic on the MBP'),
    dict(id='series_powermode', source=ARM, first_window_na=False,
         text='AC powermode equals the plan-frozen series value (High Power if adopted), '
              'stale R1 marker restored first; not an Automatic-only check'),
    dict(id='external_volume', source=ARM, first_window_na=False,
         text='no external volume, network mount or FUSE volume mounted (ruling 20)'),
    dict(id='charging_battery', source=ARM, first_window_na=False,
         text='charging/battery: AC, >=99%, not charging, |InstantAmperage|<=200 mA, '
              'completed top-up within 30 min, OBC off attested (R02)'),
    dict(id='meter_reader_live', source=PACKET, first_window_na=False,
         text='the KM003C meter reader is verified live (enabled, answering) before this arm; '
              'the meter is a SECONDARY channel and nothing else about it gates'),
    dict(id='meter_coverage', source=PACKET, first_window_na=False, gating=False,
         text='RECORDED, NON-GATING: the previous window\'s per-member meter sample/clock '
              'coverage tabulated with gaps listed; a gap never blocks v4'),
    dict(id='capture_faults', source=PACKET, first_window_na=False,
         text='sidecar/powermetrics coverage, collector faults, OOM/Metal, deadman and '
              'unobserved-state faults (X1-X8) tabulated for the previous window'),
    dict(id='thermal_escalation', source=PACKET, first_window_na=True,
         text='U1-U3 result: if failed, the registered escalation ladder (idle 300->450 s, '
              'delta_slow steps <=2.0 C, then one quantization step down) is applied and '
              'recorded before use, never in place'),
    dict(id='cohort_pool_rules', source=PACKET, first_window_na=True,
         text='cohort and pool rules: U1-U3 failure bars pool entry; one frozen four-slot '
              'cohort; no pooling across a changed configuration'),
    dict(id='sentinel_roster', source=PACKET, first_window_na=True,
         text='U4/U5 inconclusive adds two sentinels to remaining windows; roster for the '
              'next window recorded'),
    dict(id='member_eligibility', source=PACKET, first_window_na=True,
         text='final eligibility adjudication of the previous window (identity X5, U3 pairs, '
              'exclusions); counts are provisional until this check passes'),
    dict(id='calibration_stop', source=DERIVED, first_window_na=True,
         text='B3 fixed-8 predicate over the packet counts: continue for a calibration arm '
              'until 8 counted windows, '
              'calibration_complete for a test arm; pending_final_eligibility, '
              'insufficient_calibration and escalate_to_lead refuse'),
    dict(id='battery_window', source=PACKET, first_window_na=True,
         text='previous window B bar (rule zero_B_auto_resume_v1, lead ruling 9): pass; or the '
              'first non-passing window in a row resumes automatically (B members excluded, '
              'others kept; fresh admissible top-up + OBC attestation are charging_battery); '
              'a second consecutive non-passing window needs a signed battery_rulings row'),
    dict(id='full_desk_gate', source=PACKET, first_window_na=False,
         text='full desk completed and passing before arm when the previous window is W1 or '
              'code/config changed since the last desk-passed state; otherwise it may run '
              'off the MBP while the next window measures. A false v4_B_bar alone does not '
              'fail this gate: battery_window governs it (align_v4_session.full_desk_gate_pass)'),
)
TRIAGE_IDS = tuple(row['id'] for row in NEXT_ARM_TRIAGE)
GATING_IDS = tuple(row['id'] for row in NEXT_ARM_TRIAGE if row.get('gating', True))
_BY_ID = {row['id']: row for row in NEXT_ARM_TRIAGE}
WINDOW_ID = re.compile(r'^(?:R1|W1|[CTD][1-9][0-9]*)$')
COMMIT = re.compile(r'^[0-9a-f]{40}$')
RULING_RESETS = ('zero_capture_escalation',)


def _canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def triage_template(previous_window, *, next_window_role='calibration'):
    """A fill-in packet (L7): every field the arm reads, statuses 'fail' until the producer decides."""
    return {'schema': TRIAGE_SCHEMA, 'previous_window': previous_window,
            'next_window_role': next_window_role, 'record_commit': '0' * 40,
            'last_desk_passed_artifact_set_sha256': '0' * 64,
            'calibration_windows': [], 'lead_rulings': [],
            'checks': {row['id']: {'status': 'recorded' if row.get('gating', True) is False else 'fail',
                                   'basis': 'FILL IN'}
                       for row in NEXT_ARM_TRIAGE if row['source'] == PACKET}}


def _is_digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def next_arm_triage(packet, internal, identity=None):
    """Evaluate the frozen triage list. Every gating check gates the arm.

    ``internal`` maps each ARM-source id to bool (computed by the arm itself).
    ``identity`` is what the arm derives itself, never from the packet:
    ``{'artifact_set_sha256': <current bound-artifact digest>, 'record_commit_exists': bool}``.
    ``packet`` is the off-MBP evidence: schema, ``previous_window`` (a window id
    or ``'R1'`` for the first v4 window), ``record_commit`` (the previous record's
    commit), ``last_desk_passed_artifact_set_sha256``, ``next_window_role``
    ('calibration' or 'test'), ``calibration_windows`` (the ``calibration_stop``
    rows), optional ``lead_rulings`` and ``calibration_totals``, and ``checks``
    mapping each PACKET id to
    ``{'status': 'pass'|'fail'|'not_applicable', 'basis': <non-empty str>}``.
    Whether the previous window was W1 and whether code/config changed are DERIVED
    (window id; artifact-set digest vs the last desk-passed one); the optional
    packet flags ``previous_window_is_w1`` / ``code_or_config_changed`` must agree
    or the packet is refused. Only ``full_desk_gate`` may read ``deferred``, and only
    when neither holds. ``meter_coverage`` is a recorded tabulation and never gates.
    The result retains the packet itself and its digest.
    """
    reasons, results = [], {}
    packet = packet if isinstance(packet, dict) else {}
    identity = identity if isinstance(identity, dict) else {}
    if packet.get('schema') != TRIAGE_SCHEMA:
        reasons.append('next-arm triage packet missing or wrong schema')
    previous = packet.get('previous_window')
    if not isinstance(previous, str) or not WINDOW_ID.match(previous):
        reasons.append('triage packet needs previous_window as a registered window id (R1, W1, Cn, Tn, Dn)')
        previous = previous if isinstance(previous, str) else None
    first = previous == 'R1'
    derived_w1 = previous == 'W1'
    current, passed = identity.get('artifact_set_sha256'), packet.get('last_desk_passed_artifact_set_sha256')
    derived_changed = not (_is_digest(current) and current == passed)
    for flag, derived in (('previous_window_is_w1', derived_w1), ('code_or_config_changed', derived_changed)):
        if flag in packet and (type(packet[flag]) is not bool or packet[flag] != derived):
            reasons.append(f'triage packet {flag}={packet[flag]!r} contradicts the derived value {derived}')
    desk_required = derived_w1 or derived_changed
    checks = packet.get('checks') if isinstance(packet.get('checks'), dict) else {}
    extra = sorted(set(checks) - {r['id'] for r in NEXT_ARM_TRIAGE if r['source'] == PACKET})
    if extra:
        reasons.append('triage packet carries unlisted or arm-computed checks: ' + ', '.join(extra))
    stop = stop_error = None
    try:
        stop = calibration_stop(packet.get('calibration_windows'), packet.get('lead_rulings', ()))
        totals = packet.get('calibration_totals')
        if totals is not None and totals != stop['eligible_by_pair']:
            raise ValueError(f'calibration_totals {totals!r} do not match the window rows {stop["eligible_by_pair"]!r}')
    except (ValueError, AttributeError, TypeError) as exc:
        stop, stop_error = None, str(exc)
        reasons.append(f'calibration evidence contradictory or malformed: {stop_error}')
    commit = packet.get('record_commit')
    record_ok = isinstance(commit, str) and bool(COMMIT.match(commit)) and identity.get('record_commit_exists') is True
    for row in NEXT_ARM_TRIAGE:
        name, gating = row['id'], row.get('gating', True)
        if row['source'] == ARM:
            ok = internal.get(name) is True
            results[name] = {'status': 'pass' if ok else 'fail', 'source': ARM}
            if not ok:
                reasons.append(f'triage {name} failed or unevaluated')
            continue
        if row['source'] == DERIVED:
            role = packet.get('next_window_role')
            if first and role is None and packet.get('calibration_windows') in (None, []):
                results[name] = {'status': 'not_applicable', 'source': DERIVED}
                continue
            allowed = stop is not None and ((stop['decision'] == 'continue' and role == 'calibration')
                                            or (stop['decision'] == 'calibration_complete' and role == 'test'))
            results[name] = {'status': 'pass' if allowed else 'fail', 'source': DERIVED,
                             'decision': stop['decision'] if stop else stop_error, 'next_window_role': role}
            if not allowed:
                reasons.append(f'triage {name}: {results[name]["decision"]} does not allow a {role!r} arm')
            continue
        entry = checks.get(name)
        status = entry.get('status') if isinstance(entry, dict) else None
        basis = entry.get('basis') if isinstance(entry, dict) else None
        valid = ('recorded', 'not_applicable') if not gating else ('pass', 'fail', 'not_applicable', 'deferred')
        if status not in valid or not isinstance(basis, str) or not basis.strip():
            results[name] = {'status': 'missing', 'source': PACKET, 'gating': gating}
            if gating:
                reasons.append(f'triage {name} missing or malformed')
            continue
        if not gating:
            results[name] = {'status': status, 'source': PACKET, 'gating': False, 'basis': basis,
                             **({'gaps': list(entry['gaps'])} if isinstance(entry.get('gaps'), list) else {})}
            continue
        if status == 'deferred' and name != 'full_desk_gate':
            status = 'fail'
            basis = 'deferred is allowed only for the full desk: ' + basis
        if status == 'not_applicable' and not (first and row['first_window_na']):
            status = 'fail'
            basis = 'not_applicable is allowed only for a previous-window check before W1: ' + basis
        if name == 'battery_window' and status == 'fail':
            streak = entry.get('consecutive_non_pass')
            ruled = _battery_ruled(packet.get('battery_rulings'), previous)
            if type(streak) is not int or streak < 1:
                basis = 'a failed B window needs consecutive_non_pass >= 1: ' + basis
            elif streak == 1:
                status, basis = 'automatic_resume', 'first non-passing B window resumes automatically: ' + basis
            elif ruled:
                status, basis = 'resumed_by_lead', f'lead disposition {ruled}: ' + basis
            else:
                basis = f'{streak} consecutive non-passing B windows need a lead disposition: ' + basis
        if name == 'record_committed' and status == 'pass' and not record_ok:
            status = 'fail'
            basis = 'record_commit is missing, malformed or not a commit in the repository: ' + basis
        results[name] = {'status': status, 'source': PACKET, 'basis': basis}
        if status == 'fail':
            reasons.append(f'triage {name} failed')
        elif name == 'full_desk_gate' and desk_required and status != 'pass':
            results[name]['status'] = 'fail'
            reasons.append('full desk must pass before arm after W1 or a code/config change')
    try:
        retained = json.loads(json.dumps(packet, allow_nan=False))
    except (TypeError, ValueError):
        retained = {'unserializable': True}
    return {'admitted': not reasons, 'reasons': reasons, 'checks': results,
            'previous_window': previous, 'full_desk_required': desk_required,
            'derived': {'previous_window_is_w1': derived_w1, 'code_or_config_changed': derived_changed,
                        'artifact_set_sha256': current, 'record_commit_exists': identity.get('record_commit_exists')},
            'list': list(TRIAGE_IDS), 'gating': list(GATING_IDS),
            'calibration': stop, 'lead_rulings': retained.get('lead_rulings', []),
            'packet': retained, 'packet_sha256': _canonical_sha256(retained)}


# B3: FIXED 8 calibration windows (RUN_STATE 214/215; reverted from a count stop by 217).
# Two synthetic simulations found that stopping on counts raises benign FPR under
# window-level drift; the counts never read scores, so blinding was not the issue.
CAL_PAIRS = ('spam', 'bank')
CAL_WINDOWS = 8
CAL_TARGET_PER_PAIR = 39
BENIGN_PER_PAIR_PER_WINDOW = 7    # protocol default roster: 14 benign (7/pair) per window
WINDOW_MEMBERS = 22               # 4 anchors + 2 sentinels + 14 benign + 2 sabotage


def _battery_ruled(rulings, previous):
    """The ruling_id of a signed battery disposition after ``previous``, else None."""
    from scripts.align_v4_kit import valid_lead_signature
    for row in rulings if isinstance(rulings, (list, tuple)) else ():
        if (isinstance(row, dict) and set(row) == {'ruling_id', 'text_sha256', 'after_window', 'lead_signature'}
                and isinstance(row['ruling_id'], str) and row['ruling_id'].strip()
                and _is_digest(row['text_sha256']) and row['after_window'] == previous
                and valid_lead_signature(row['lead_signature'])):
            return row['ruling_id']
    return None


def _validated_rulings(rulings, window_ids):
    from scripts.align_v4_kit import valid_lead_signature
    if not isinstance(rulings, (list, tuple)):
        raise ValueError('lead_rulings must be a list')
    out = []
    for row in rulings:
        if (not isinstance(row, dict) or set(row) != {'ruling_id', 'text_sha256', 'resets', 'after_window', 'lead_signature'}
                or not isinstance(row['ruling_id'], str) or not row['ruling_id'].strip()
                or not _is_digest(row['text_sha256']) or row['resets'] not in RULING_RESETS
                or row['after_window'] not in window_ids or not valid_lead_signature(row['lead_signature'])):
            raise ValueError('lead_ruling row malformed (ruling_id, text_sha256, resets, after_window, lead_signature)')
        out.append(row)
    return out


def calibration_stop(windows, lead_rulings=()):
    """Fixed-8 calibration predicate. ``windows`` lists the window attempts in the frozen order.

    Each entry: ``{'window': unique id, 'status': 'final'|'provisional',
    'captured_members': int >= 0, 'eligible_benign': {'spam': n, 'bank': n}}``
    (optionally ``eligible_total``, which must equal their sum). Rows must be
    internally consistent: integers (no bool), ``captured_members`` at most the 22-member
    window roster, and the eligible benign members (spam + bank) no more than
    were captured; a contradictory row raises and can never authorize completion.

    Calibration is exactly 8 counted windows; there is no early stop. A **final**
    window that captured zero members is a zero-capture refusal and does not count
    (its eligible counts must be zero); a **provisional** zero-capture window is
    unfinished, not a refusal, and holds the gate pending. A window with at least
    one captured member counts, whether lost, failed or in flight. Two consecutive
    final zero-capture refusals escalate to the lead (RUN_STATE 216) until a valid
    ``lead_rulings`` row (``resets`` ``zero_capture_escalation``, signed, naming the
    last window row it follows) resets the count. The predicate reads no score,
    alarm, residual or energy field. Returns ``decision``:

    * ``escalate_to_lead`` - the last two attempts since any ruling are final
      zero-capture refusals; nothing is armed until the lead rules;
    * ``pending_final_eligibility`` - an unfinished zero-capture window, or 8 counted
      windows of which any is provisional;
    * ``continue`` - fewer than 8 counted windows: arm the next frozen window;
    * ``calibration_complete`` - 8 final counted windows and BOTH pairs have >=39
      eligible benign summed over all 8 (every eligible calibrator counts: no
      quietest-39 selection, no reordering);
    * ``insufficient_calibration`` - 8 final counted windows and either pair below
      39. No ninth counted attempt exists.

    This is not an exchangeability or R13/R14 result.
    """
    if not isinstance(windows, (list, tuple)):
        raise ValueError('windows must be a sequence in frozen order')
    seen, counted, refusals, unfinished_zero = set(), [], 0, 0
    order = []
    for row in windows:
        counts = row.get('eligible_benign') if isinstance(row, dict) else None
        if (not isinstance(row, dict) or not isinstance(row.get('window'), str) or row['window'] in seen
                or row.get('status') not in ('final', 'provisional')
                or type(row.get('captured_members')) is not int or not 0 <= row['captured_members'] <= WINDOW_MEMBERS
                or not isinstance(counts, dict) or set(counts) != set(CAL_PAIRS)
                or any(type(n) is not int or not 0 <= n <= BENIGN_PER_PAIR_PER_WINDOW for n in counts.values())
                or sum(counts.values()) > row['captured_members']
                or ('eligible_total' in row and row['eligible_total'] != sum(counts.values()))):
            raise ValueError('calibration window rows need a unique id, final|provisional status, integer '
                             f'captured_members in 0..{WINDOW_MEMBERS}, integer eligible_benign in '
                             f'0..{BENIGN_PER_PAIR_PER_WINDOW} per pair summing to at most captured_members '
                             '(and to eligible_total when given)')
        seen.add(row['window'])
        order.append(row['window'])
        if row['captured_members'] == 0:
            if row['status'] == 'provisional':
                unfinished_zero += 1
            else:
                refusals += 1
            continue
        counted.append(row)
    rulings = _validated_rulings(lead_rulings, set(order))
    last_reset = max((order.index(r['after_window']) for r in rulings), default=-1)
    trailing_zero = 0
    for row in windows[last_reset+1:]:
        trailing_zero = trailing_zero+1 if (row['captured_members'] == 0 and row['status'] == 'final') else 0
    if len(counted) > CAL_WINDOWS:
        raise ValueError(f'more than the fixed {CAL_WINDOWS} counted calibration windows')
    totals = dict.fromkeys(CAL_PAIRS, 0)
    for row in counted:
        for pair in CAL_PAIRS:
            totals[pair] += row['eligible_benign'][pair]
    attempted = len(counted)
    final = all(row['status'] == 'final' for row in counted) and not unfinished_zero
    base = {'attempted': attempted, 'windows': CAL_WINDOWS, 'target_per_pair': CAL_TARGET_PER_PAIR,
            'eligible_by_pair': totals, 'counts_are_final': final, 'zero_capture_refusals': refusals,
            'unfinished_zero_capture_windows': unfinished_zero,
            'lead_rulings_applied': [r['ruling_id'] for r in rulings]}
    if trailing_zero >= 2:
        return {**base, 'decision': 'escalate_to_lead'}
    if unfinished_zero:
        return {**base, 'decision': 'pending_final_eligibility'}
    if attempted < CAL_WINDOWS:
        return {**base, 'decision': 'continue'}
    if not final:
        return {**base, 'decision': 'pending_final_eligibility'}
    if all(totals[pair] >= CAL_TARGET_PER_PAIR for pair in CAL_PAIRS):
        return {**base, 'decision': 'calibration_complete'}
    return {**base, 'decision': 'insufficient_calibration'}


if __name__ == '__main__':
    # L7: python3 -m joulewise.align.apple.v4_cadence --emit-triage-template C2 [--role test]
    import argparse
    parser = argparse.ArgumentParser(description='Emit a fill-in next-arm triage packet (checks fail until filled).')
    parser.add_argument('--emit-triage-template', metavar='PREVIOUS_WINDOW', required=True)
    parser.add_argument('--role', choices=('calibration', 'test'), default='calibration')
    arguments = parser.parse_args()
    print(json.dumps(triage_template(arguments.emit_triage_template, next_window_role=arguments.role),
                     indent=2, sort_keys=True))
