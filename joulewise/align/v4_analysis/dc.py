"""Fresh benign DC observations and independent five-term LOTO diagnostic.

Uses the production KM003C clock fit and ownership partition. Turn energy
uses the registered sample-and-hold coverage rule; whole-member energy keeps
the production integral. No DC leaf selects GPU fits or thresholds.
"""
from bisect import bisect_right
from dataclasses import asdict
import math

from joulewise.align.attribution import _segments
from joulewise.external import km003c_parse as kp
from . import residual
from .io import canonical, digest


MAX_HOLD_NS = 3 * 100_000_000  # R23m D6: three nominal 100 ms poll periods.


def _hold_integral(times_ns, watts, start, end):
    """Power at t_i holds on [t_i, t_i+1); never extend stream edges.

    A hold longer than MAX_HOLD_NS is entirely uncovered, even when only a
    short part overlaps owned time. Inputs are after the production clock fit.
    """
    if not times_ns or not times_ns[0] <= start < end <= times_ns[-1]:
        return None
    i = bisect_right(times_ns, start)-1
    parts = []
    while times_ns[i] < end:
        a, b = times_ns[i], times_ns[i+1]
        if b-a > MAX_HOLD_NS:
            return None
        parts.append(watts[i] * ((min(b, end)-max(a, start))/1e9))
        i += 1
    return math.fsum(parts)


def capture(streams, episode, member_span):
    flags = []
    for name, stream in streams:
        offset = kp.raw_offset_ns(stream, allow_unclosed=True)
        if not stream.present or not stream.aligned or offset is None:
            flags.append('meter.clock_or_samples_unavailable')
            continue
        a, b = (v+offset for v in member_span)
        if not stream.host_ns[0] <= a < b <= stream.host_ns[-1] or kp.span_has_drops(stream, a, b):
            # Whole-span defects remain disclosed. Only uncovered OWNED time
            # makes the turn integral unavailable (D6); gaps/gates/holds do not.
            flags.append('meter.member_uncovered_or_gap')
        if any(e.get('rx') is None or a <= e['rx'] < b for e in stream.errors):
            flags.append('meter.member_error')
            continue
        disclosures = kp.flags(stream, windows=[(a,b)])
        if any(f['code'] == 'meter.clock_fit_residual' for f in disclosures):
            flags.append('meter.clock_fit_residual')
            continue
        owned = {t.index: [] for t in episode.logged_turns()}
        segments = _segments(episode, [])
        for turn, kind, start, end in segments:
            if turn in owned:
                owned[turn].append(_hold_integral(stream.host_ns, stream.watts, start+offset, end+offset))
        whole = kp.integrate(stream.host_ns, stream.watts, a, b)[0]
        if any(v is None for parts in owned.values() for v in parts):
            flags.append('meter.turn_uncovered')
            continue
        energies = {i: (math.fsum(parts), 0.) for i, parts in owned.items()}
        rows = [asdict(r) for r in residual.er.turn_rows_from_episode(episode, energies,
                    hidden_token_counts_logged=True, uncertainty_kind='standard_uncertainty')]
        bt, bw = stream.battery_watts()
        bj = kp.integrate(bt, bw, a, b)[0] if bt and bt[0] <= a < b <= bt[-1] else None
        return dict(status='available', stream=name, whole_member_j=whole,
            turn_owned_j=math.fsum(r['energy_j'] for r in rows), turn_rows=rows,
            battery_assist=dict(status='observed' if bj is not None else 'unavailable', joules=bj,
                                role='disclosure_only'),
            flags=[*flags, *(f['code'] for f in disclosures), *(['meter.stream_unclosed'] if stream.trailer is None else [])])
    return dict(status='missing', flags=flags or ['meter.absent'], whole_member_j=None,
                turn_owned_j=None, turn_rows=[], battery_assist=dict(status='unavailable', joules=None))


def analyze_windows(windows, *, gpu_fits):
    """Print all captured benign DC values; mirror GPU rows only for residuals.

    Missing DC withholds a residual rather than changing the training set.
    W1, anchors, sentinels and development members have no benign residual
    here because the GPU scorer supplies no such row.
    """
    gpu_rows = {(f['window'], f['pair'], r['run_id']): r
                for f in gpu_fits if f['convention'] == 'counts_logged'
                for r in f['scores'] if r['condition'] == 'benign'}
    output = []
    for window in windows:
        benign = []
        for m in window['members']:
            if not m['captured']:
                continue
            slot = m['slot']
            identity = dict(window=window['window'], attempt_id=window.get('attempt_id'),
                            run_id=slot['run_id'])
            if slot['condition'] != 'benign':
                # Never open raw DC for sabotage. A presence seal is enough for
                # comparison; a pre-existing desk hash may also be supplied.
                output.append(dict(**identity, status='sealed', sealed=True,
                    sha256=digest(canonical(m.get('dc')))))
                continue
            key = (window['window'], slot['task_pair'], slot['run_id'])
            identity['pair'] = slot['task_pair']
            evidence = m.get('dc_evidence')
            row = capture(evidence['streams'], evidence['episode'], evidence['member_span_ns']) if evidence else dict(
                status='missing', flags=['meter.raw_evidence_unavailable'], turn_rows=[],
                whole_member_j=None, turn_owned_j=None, battery_assist=dict(status='unavailable', joules=None))
            result = dict(**identity, status='print_only', value=row, residual_status='no_gpu_row')
            output.append(result)
            if key in gpu_rows:
                result.update(residual_status='dc_unavailable',
                              training_run_ids=list(gpu_rows[key]['training_trajectories']))
                benign.append((m, row, result))
        for m, row, result in benign:
            if row['status'] != 'available':
                continue
            slot = m['slot']
            by_run = {n['slot']['run_id']: r for n, r, _ in benign if n['slot']['task_pair'] == slot['task_pair']}
            train = [by_run.get(run) for run in result['training_run_ids']]
            if any(r is None or r['status'] != 'available' for r in train):
                result['residual_status'] = 'dc_training_unavailable'
                continue
            model = residual.fit([v for r in train for v in r['turn_rows']])
            point = residual.predict(model, row['turn_rows'], measured_j=row['turn_owned_j'],
                                     measured_half_width_j=0., uncertainty_kind='standard_uncertainty')
            result.update(residual_status='available' if math.isfinite(point['predicted_j']) else 'dc_fit_unavailable',
                model=model,
                prediction_j=point['predicted_j'], residual_j=point['residual_j'], method='leave_one_trajectory_out')
    return output
