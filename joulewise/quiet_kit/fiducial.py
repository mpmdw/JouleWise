"""Capture physics composition, with no ledger or registered acceptance input."""
from __future__ import annotations

import dataclasses
import functools
import json


def derive(raw: bytes, events: bytes, anchor: dict, *, protocol_id=None, scale=1.):
    return _derive(raw, events, json.dumps(anchor, sort_keys=True), protocol_id, scale)


@functools.lru_cache(maxsize=8)
def _derive(raw, events, anchor_json, protocol_id, scale):
    anchor = json.loads(anchor_json)
    from joulewise.adapters.powermetrics import parse_powermetrics_records, anchor_records_from_powermetrics
    from joulewise.clock import ClockStamp
    from joulewise.uncertainty_evidence import resolve_anchor_deriver
    from joulewise.powermetrics_fiducial import (PROTOCOL_ID, CommandedPulse, TraceInterval,
        WARMUP_PULSE_COUNT, authenticate_protocol_schedule, clock_stamp_half_width_s, detect_pulses,
        trim_trace_after_pulses, protocol_pulse_count, capture_wall_time_from_events)
    protocol_id = protocol_id or PROTOCOL_ID
    capture_wall_time_from_events(events)
    # The anchor's primary inputs are paired clock stamps and native plist
    # records. Recompute it, rather than trusting a stored derived bound.
    anchor = resolve_anchor_deriver(anchor['method'])(
        stamps={k: ClockStamp(**v) for k, v in anchor['clock_stamps'].items()},
        records=anchor_records_from_powermetrics(parse_powermetrics_records(raw)))
    endpoint = anchor.get('first_sample_end_point_epoch_s')
    if endpoint is None or anchor.get('status') != 'bounded':
        raise ValueError('capture trace anchor unresolved')
    pairs = {'pulse': [], 'warmup': []}
    pending = {}
    for line in events.splitlines():
        row = json.loads(line)
        event = row.get('event_type', '')
        if event not in ('pulse_command_on', 'pulse_command_off', 'warmup_command_on', 'warmup_command_off'):
            continue
        kind, edge = event.split('_command_')
        stamp = ClockStamp(**row['metadata']['clock_stamp'])
        if edge == 'on':
            if kind in pending:
                raise ValueError('unpaired pulse on')
            pending[kind] = stamp
        else:
            on = pending.pop(kind, None)
            if on is None or stamp.epoch_s <= on.epoch_s:
                raise ValueError('unpaired pulse off')
            pairs[kind].append(CommandedPulse(on.epoch_s, stamp.epoch_s,
                clock_stamp_half_width_s(on), clock_stamp_half_width_s(stamp)))
    if pending:
        raise ValueError('unfinished pulse event')
    if len(pairs['warmup']) != WARMUP_PULSE_COUNT or len(pairs['pulse']) != protocol_pulse_count(protocol_id):
        raise ValueError('capture pulse count disagrees with frozen protocol')
    records = parse_powermetrics_records(raw, first_record_endpoint_s=endpoint)
    intervals = [TraceInterval(r.timestamp_s-r.elapsed_ns/1e9, r.timestamp_s, r.rail_power_w['gpu_power']) for r in records]
    intervals = trim_trace_after_pulses(intervals, pairs['warmup'])
    if scale == 1.:
        authenticate_protocol_schedule(pairs['pulse'], intervals)
    detection = detect_pulses(intervals, pairs['pulse'], trace_anchor_bound_s=anchor['effective_clock_anchor_bound_s'])
    detection = dataclasses.replace(detection, anchor_method=anchor['method'], derivation_role='prospective')
    return detection


def report(detection):
    """The bound belongs only to these calibration bytes, never to a claim."""
    return {'bound_s': detection.b_fiducial_s, 'detector': dataclasses.asdict(detection),
            'flags': [{'reason': r} for r in detection.reasons]}
