"""Frozen pulse capture child, under model Python and its actual taskpolicy."""
from __future__ import annotations

import argparse
import atexit
import dataclasses
import hashlib
import importlib.metadata
import signal
import sys
import time

from .collectors import Sampler, stamp
from .hardware import Hardware
from .paths import append, atomic_json, fence, mkdir, read_bytes


def main(argv=None):
    from pathlib import Path
    from joulewise.powermetrics_fiducial import (PROTOCOL_ID, PULSE_COUNT, WARMUP_PULSE_COUNT,
        BASELINE_S, PULSE_DURATION_S, allocate_matmul_buffers, pulse_schedule, run_matmul_pulse,
        instrument_evidence, protocol_definition, protocol_sha256)
    from .fiducial import derive, report
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--scale', type=float, default=1.)
    parser.add_argument('--kind', default='measurement')
    args = parser.parse_args(argv)
    if args.scale <= 0 or args.kind == 'measurement' and args.scale != 1:
        parser.error('measurement uses the frozen unscaled protocol')
    out = mkdir(args.out)
    repo = fence(Path(__file__).resolve().parents[2])
    protocol_bytes = read_bytes(repo/'configs/calibration/powermetrics_fiducial/protocol_v3.json')
    if hashlib.sha256(protocol_bytes).hexdigest() != protocol_sha256(PROTOCOL_ID):
        raise ValueError('frozen protocol bytes differ from library protocol')
    hw = Hardware(repo, sys.executable)
    hw.current_directory = out
    atexit.register(hw.cleanup)
    def stop(sig, _):
        raise SystemExit(128+sig)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    buffers = allocate_matmul_buffers()
    sampler = Sampler(hw, out / 'raw', None)
    events = fence(out / 'events.jsonl')
    def event(kind, **fields):
        raw_before = time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
        clock_stamp = sampler.clock.stamp()
        raw_after = time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
        append(events, {'kind': args.kind, 'timestamp_s': clock_stamp.epoch_s, 'event_type': kind,
            'phase': 'instrument_validation', 'metadata': {'clock_stamp': dataclasses.asdict(clock_stamp),
                'monotonic_raw_ns': (raw_before+raw_after)//2, 'raw_read_skew_ns': raw_after-raw_before, **fields}})
        return clock_stamp
    event('sampling_started')
    try:
        time.sleep(BASELINE_S*args.scale)
        for index in range(WARMUP_PULSE_COUNT):
            event('warmup_command_on', warmup_index=index)
            run_matmul_pulse(PULSE_DURATION_S*args.scale, buffers)
            event('warmup_command_off', warmup_index=index)
            time.sleep(1.5*args.scale)
        time.sleep(BASELINE_S*args.scale)
        start = time.monotonic()
        for index, (on, off) in enumerate(pulse_schedule(PULSE_COUNT)):
            time.sleep(max(0., start+on*args.scale-time.monotonic()))
            event('pulse_command_on', pulse_index=index, planned_on_offset_s=on*args.scale)
            run_matmul_pulse(PULSE_DURATION_S*args.scale, buffers)
            event('pulse_command_off', pulse_index=index, planned_off_offset_s=off*args.scale)
        time.sleep(BASELINE_S*args.scale)
        event('sampling_stopped')
        metadata = sampler.close()
        raw = read_bytes(out / 'raw/powermetrics.plist')
        event_bytes = read_bytes(events)
        detection = derive(raw, event_bytes, metadata['clock_anchor'], scale=args.scale)
        native = __import__('joulewise.adapters.powermetrics', fromlist=['parse_powermetrics_records']).parse_powermetrics_records(raw)
        definitions = protocol_definition()
        bindings = {'hardware_model': native[0].metadata.get('hw_model'),
                    'os_build': native[0].metadata.get('kern_osversion'),
                    'powermetrics_sha256': hashlib.sha256(read_bytes('/usr/bin/powermetrics')).hexdigest(),
                    'sampling_interval_ms': 100, 'anchor_method_version': metadata['clock_anchor']['method'],
                    'mlx_version': importlib.metadata.version('mlx'), 'pulse_protocol_id': PROTOCOL_ID,
                    'power_policy': 'quiet-kit-record-only', 'estimator_revision': definitions['estimator_revision'],
                    'protocol_sha256': protocol_sha256(PROTOCOL_ID)}
        evidence = instrument_evidence(detection, bindings=bindings, validation_id=out.name,
            artifact_sha256={'raw/powermetrics.plist': hashlib.sha256(raw).hexdigest(),
                             'events.jsonl': hashlib.sha256(event_bytes).hexdigest()},
            capture_wall_time_s=sampler.stamps['sampling_started'].epoch_s)
        evidence['kind'] = args.kind
        evidence['clock_anchor'] = metadata['clock_anchor']
        evidence['non_claim'] = True
        atomic_json(out / 'instrument_evidence.json', evidence)
        atomic_json(out / 'capture.json', {'kind': args.kind, 'protocol_id': PROTOCOL_ID, 'scale': args.scale,
            'sampler_span_s': metadata['span_s'], 'cadence_median_ms': metadata['cadence_median_ms'],
            'instrument_flags': [{'reason': r} for r in evidence.get('reasons', [])],
            **report(detection)})
        return 0
    finally:
        hw.cleanup()


if __name__ == '__main__':
    raise SystemExit(main())
