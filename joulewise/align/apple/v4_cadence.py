"""R12 window cadence (RUN_STATE 214/215/217): next-arm triage list and fixed-8 calibration.

Pure stdlib. No probes, no scores, no outcome fields: the calibration predicate
sees only window status and eligible benign counts per pair, so blinding holds.
Neither function qualifies exchangeability or satisfies R13/R14; counts alone do
not settle them (RUN_STATE 217: a count stop raised FPR under window drift, so
calibration is exactly 8 windows).
"""
from __future__ import annotations

import math
import time

TRIAGE_SCHEMA = 'joulewise.align_v4.next_arm_triage.v1'
# Evidence an arm computes itself (cannot be supplied by the packet) vs the
# packet built off the MBP from the committed record and the laptop desk.
ARM = 'arm_checks'
PACKET = 'packet'
DERIVED = 'derived'      # computed here from packet counts by calibration_stop

# B2: the frozen, enumerated next-arm triage list. Every check whose result
# changes the next window's plan is here and GATING. Nothing that gated before
# R12 becomes non-gating by omission. ``first_window_na`` marks checks that
# summarize a previous v4 window and so may read not_applicable for W1 (previous
# window is R1) only.
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
    dict(id='meter_samples_clock', source=PACKET, first_window_na=False,
         text='KM003C coverage tabulated with gaps listed (SECONDARY, non-gating); '
              'meter samples and clock verified live before this arm'),
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
    dict(id='full_desk_gate', source=PACKET, first_window_na=False,
         text='full desk completed and passing before arm when the previous window is W1 or '
              'code/config changed since the last desk-passed state; otherwise it may run '
              'off the MBP while the next window measures'),
)
TRIAGE_IDS = tuple(row['id'] for row in NEXT_ARM_TRIAGE)
_BY_ID = {row['id']: row for row in NEXT_ARM_TRIAGE}


def next_arm_triage(packet, internal, *, now_epoch_s=None):
    """Evaluate the frozen triage list. Every listed check gates the arm.

    ``internal`` maps each ARM-source id to bool (computed by the arm itself).
    ``packet`` is the off-MBP evidence: schema, ``previous_window`` (a window id
    or ``'R1'`` for the first v4 window), ``previous_window_is_w1`` and
    ``code_or_config_changed`` booleans, ``next_window_role`` ('calibration' or
    'test'), ``calibration_windows`` (the ``calibration_stop`` rows) and ``checks``
    mapping each PACKET id to
    ``{'status': 'pass'|'fail'|'not_applicable', 'basis': <non-empty str>}``;
    only ``full_desk_gate`` may read ``deferred`` (desk running off the MBP), and
    only when the previous window is not W1 and no code/config changed.
    Missing, malformed, unknown or self-supplied ids refuse; an absent boolean is
    never assumed False.
    """
    reasons, results = [], {}
    packet = packet if isinstance(packet, dict) else {}
    if packet.get('schema') != TRIAGE_SCHEMA:
        reasons.append('next-arm triage packet missing or wrong schema')
    if 'valid_until_epoch_s' in packet:
        expires = packet['valid_until_epoch_s']
        now = time.time() if now_epoch_s is None else now_epoch_s
        if (type(expires) not in (int, float) or not math.isfinite(expires)
                or type(now) not in (int, float) or not math.isfinite(now) or now > expires):
            reasons.append('triage packet quiet/meter observations expired or malformed')
    previous = packet.get('previous_window')
    if not isinstance(previous, str) or not previous.strip():
        reasons.append('triage packet needs previous_window (window id, or R1 before W1)')
    first = previous == 'R1'
    flags = {k: packet.get(k) for k in ('previous_window_is_w1', 'code_or_config_changed')}
    for name, value in flags.items():
        if type(value) is not bool:
            reasons.append(f'triage packet needs boolean {name}')
    checks = packet.get('checks') if isinstance(packet.get('checks'), dict) else {}
    extra = sorted(set(checks) - {r['id'] for r in NEXT_ARM_TRIAGE if r['source'] == PACKET})
    stop = None
    try:
        stop = calibration_stop(packet.get('calibration_windows'))
    except (ValueError, AttributeError, TypeError) as exc:
        stop_error = str(exc)
    else:
        stop_error = None
    if extra:
        reasons.append('triage packet carries unlisted or arm-computed checks: ' + ', '.join(extra))
    desk_required = flags['previous_window_is_w1'] is not False or flags['code_or_config_changed'] is not False
    for row in NEXT_ARM_TRIAGE:
        name = row['id']
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
        if status not in ('pass', 'fail', 'not_applicable', 'deferred') or not isinstance(basis, str) or not basis.strip():
            results[name] = {'status': 'missing', 'source': PACKET}
            reasons.append(f'triage {name} missing or malformed')
            continue
        if status == 'deferred' and name != 'full_desk_gate':
            status = 'fail'
            basis = 'deferred is allowed only for the full desk: ' + basis
        if status == 'not_applicable' and not (first and row['first_window_na']):
            status = 'fail'
            basis = 'not_applicable is allowed only for a previous-window check before W1: ' + basis
        results[name] = {'status': status, 'source': PACKET, 'basis': basis}
        if status == 'fail':
            reasons.append(f'triage {name} failed')
        elif name == 'full_desk_gate' and desk_required and status != 'pass':
            results[name]['status'] = 'fail'
            reasons.append('full desk must pass before arm after W1 or a code/config change')
    return {'admitted': not reasons, 'reasons': reasons, 'checks': results,
            'previous_window': previous, 'full_desk_required': desk_required,
            'list': list(TRIAGE_IDS)}


# B3: FIXED 8 calibration windows (RUN_STATE 214/215; reverted from a count stop by 217).
# Two synthetic simulations found that stopping on counts raises benign FPR under
# window-level drift; the counts never read scores, so blinding was not the issue.
CAL_PAIRS = ('spam', 'bank')
CAL_WINDOWS = 8
CAL_TARGET_PER_PAIR = 39
BENIGN_PER_PAIR_PER_WINDOW = 7    # protocol default roster: 14 benign (7/pair) per window


def calibration_stop(windows):
    """Fixed-8 calibration predicate. ``windows`` lists the window attempts in the frozen order.

    Each entry: ``{'window': unique id, 'status': 'final'|'provisional',
    'captured_members': int >= 0, 'eligible_benign': {'spam': n, 'bank': n}}``.
    Calibration is exactly 8 counted windows; there is no early stop. A window
    that captured **zero** members is a zero-capture refusal and does not count
    (its eligible counts must be zero); a window with at least one captured
    member counts, whether lost, failed or in flight, and carries its final
    counts (zero when nothing is eligible). Two consecutive zero-capture
    refusals escalate to the lead (RUN_STATE 216). The predicate reads no score,
    alarm, residual or energy field. Returns ``decision``:

    * ``escalate_to_lead`` - the last two attempts are both zero-capture refusals;
      nothing is armed until the lead rules;
    * ``continue`` - fewer than 8 counted windows: arm the next frozen window;
    * ``pending_final_eligibility`` - 8 counted windows and any is provisional;
    * ``calibration_complete`` - 8 final counted windows and BOTH pairs have >=39
      eligible benign summed over all 8 (every eligible calibrator counts: no
      quietest-39 selection, no reordering);
    * ``insufficient_calibration`` - 8 final counted windows and either pair below
      39. No ninth counted attempt exists.

    MED-2a: a ``type='lead_ruling'`` row with unique nonblank ``ruling_id``
    and ``after_window`` equal to the current two-zero tail acknowledges the
    escalation and resets only that tail. Attempts and counts remain intact.
    This is not an exchangeability or R13/R14 result.
    """
    if not isinstance(windows, (list, tuple)):
        raise ValueError('windows must be a sequence in frozen order')
    seen, ruling_ids, counted, refusals = set(), set(), [], 0
    trailing_zero = 0
    last_window = None
    for row in windows:
        # MED-2a: retain both refused attempts; a prospective lead ruling
        # acknowledges that exact tail without deleting or counting a window.
        if isinstance(row, dict) and row.get('type') == 'lead_ruling':
            ruling = row.get('ruling_id')
            if (not isinstance(ruling, str) or not ruling.strip() or ruling in ruling_ids
                    or trailing_zero < 2 or row.get('after_window') != last_window):
                raise ValueError('lead_ruling needs a unique ruling_id after the current two-zero-capture tail')
            ruling_ids.add(ruling)
            trailing_zero = 0
            continue
        counts = row.get('eligible_benign') if isinstance(row, dict) else None
        if (not isinstance(row, dict) or not isinstance(row.get('window'), str) or row['window'] in seen
                or row.get('type', 'window') != 'window'
                or row.get('status') not in ('final', 'provisional')
                or type(row.get('captured_members')) is not int or row['captured_members'] < 0
                or not isinstance(counts, dict) or set(counts) != set(CAL_PAIRS)
                or any(type(n) is not int or not 0 <= n <= BENIGN_PER_PAIR_PER_WINDOW for n in counts.values())):
            raise ValueError('calibration window rows need a unique id, final|provisional status, '
                             'integer captured_members >= 0 and integer eligible_benign in '
                             f'0..{BENIGN_PER_PAIR_PER_WINDOW} for each pair')
        seen.add(row['window'])
        last_window = row['window']
        if row['captured_members'] == 0:
            if any(counts.values()):
                raise ValueError('a zero-capture window cannot carry eligible members')
            refusals += 1
            trailing_zero += 1
            continue
        trailing_zero = 0
        counted.append(row)
    if len(counted) > CAL_WINDOWS:
        raise ValueError(f'more than the fixed {CAL_WINDOWS} counted calibration windows')
    totals = dict.fromkeys(CAL_PAIRS, 0)
    for row in counted:
        for pair in CAL_PAIRS:
            totals[pair] += row['eligible_benign'][pair]
    attempted = len(counted)
    final = all(row['status'] == 'final' for row in counted)
    base = {'attempted': attempted, 'windows': CAL_WINDOWS, 'target_per_pair': CAL_TARGET_PER_PAIR,
            'eligible_by_pair': totals, 'counts_are_final': final, 'zero_capture_refusals': refusals}
    if trailing_zero >= 2:
        return {**base, 'decision': 'escalate_to_lead'}
    if attempted < CAL_WINDOWS:
        return {**base, 'decision': 'continue'}
    if not final:
        return {**base, 'decision': 'pending_final_eligibility'}
    if all(totals[pair] >= CAL_TARGET_PER_PAIR for pair in CAL_PAIRS):
        return {**base, 'decision': 'calibration_complete'}
    return {**base, 'decision': 'insufficient_calibration'}
