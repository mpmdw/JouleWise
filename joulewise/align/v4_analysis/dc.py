"""Fresh benign DC observations and independent five-term LOTO diagnostic.

Uses the production KM003C clock/coverage rules and the production ownership
partition. No DC leaf is an input to GPU selection, fits or thresholds.
"""
from dataclasses import asdict
import math

from joulewise.align.attribution import _segments
from joulewise.external import km003c_parse as kp
from . import residual
from .io import canonical, digest


def capture(streams, episode, member_span):
    flags = []
    for name, stream in streams:
        offset = kp.raw_offset_ns(stream, allow_unclosed=True)
        if not stream.present or not stream.aligned or offset is None:
            flags.append('meter.clock_or_samples_unavailable')
            continue
        a, b = (v+offset for v in member_span)
        if not stream.host_ns[0] <= a < b <= stream.host_ns[-1] or kp.span_has_drops(stream, a, b):
            flags.append('meter.member_uncovered_or_gap')
            continue
        if any(e.get('rx') is None or a <= e['rx'] < b for e in stream.errors):
            flags.append('meter.member_error')
            continue
        disclosures = kp.flags(stream, windows=[(a,b)])
        if any(f['code'] == 'meter.clock_fit_residual' for f in disclosures):
            flags.append('meter.clock_fit_residual')
            continue
        owned = {t.index: [] for t in episode.logged_turns()}
        segments = _segments(episode, [])
        def integral(start, end):
            return kp.integrate(stream.host_ns, stream.watts, start+offset, end+offset)[0]
        for turn, kind, start, end in segments:
            if turn in owned:
                owned[turn].append(integral(start,end))
        whole = integral(*member_span)
        if whole is None or any(v is None for parts in owned.values() for v in parts):
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


def analyze_windows(windows, *, calibration_complete):
    output = []
    for window in windows:
        benign = []
        for m in window['members']:
            slot = m['slot']
            identity = dict(window=window['window'], run_id=slot['run_id'])
            if slot['condition'] != 'benign':
                # Never open raw DC for sabotage. A presence seal is enough for
                # comparison; a pre-existing desk hash may also be supplied.
                output.append(dict(**identity, status='sealed', sealed=True,
                    sha256=digest(canonical(m.get('dc')))))
                continue
            evidence = m.get('dc_evidence')
            row = capture(evidence['streams'], evidence['episode'], evidence['member_span_ns']) if evidence else dict(
                status='missing', flags=['meter.raw_evidence_unavailable'], turn_rows=[],
                whole_member_j=None, turn_owned_j=None, battery_assist=dict(status='unavailable', joules=None))
            result = dict(**identity, status='print_only', value=row, residual_status='dc_unavailable')
            output.append(result)
            benign.append((m, row, result))
        for m, row, result in benign:
            if row['status'] != 'available':
                continue
            if not window.get('pool_entry', True) or not m['eligible']:
                result['residual_status'] = 'ineligible'
                continue
            if window['window'].startswith('T') and not calibration_complete:
                result['residual_status'] = 'calibration_incomplete'
                continue
            slot = m['slot']
            train = [(n, r) for n, r, _ in benign if n['eligible'] and
                     n['slot']['model_id'] == slot['model_id'] and n['slot']['task_pair'] == slot['task_pair']
                     and n['slot']['run_id'] != slot['run_id'] and r['status'] == 'available'
                     and n['slot']['held_out'] == slot['held_out']]
            model = residual.fit([v for _, r in train for v in r['turn_rows']])
            point = residual.predict(model, row['turn_rows'], measured_j=row['turn_owned_j'],
                                     measured_half_width_j=0., uncertainty_kind='standard_uncertainty')
            result.update(residual_status='available' if math.isfinite(point['predicted_j']) else 'dc_fit_unavailable',
                model=model, training_run_ids=[n['slot']['run_id'] for n, _ in train],
                prediction_j=point['predicted_j'], residual_j=point['residual_j'], method='leave_one_trajectory_out')
    return output
