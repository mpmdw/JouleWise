#!/usr/bin/env python3
"""Offline synthetic-only powermetrics benchmark; never opens campaign configs."""
from __future__ import annotations

import argparse
import cProfile
from dataclasses import asdict, replace
from datetime import datetime, timedelta
import io
import hashlib
import json
from pathlib import Path
import plistlib
import pstats
import platform
import re
import sys
import tempfile
import time
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.adapters.powermetrics import parse_powermetrics_records, decode_rich_telemetry
from joulewise.align.apple import reduce_sol as sol

ENDPOINT = 1767225600.0
OFFSET = -1767225500000000000
EVIDENCE = {'clock_anchor': {'status': 'bounded', 'method': 'synthetic-benchmark',
                           'effective_clock_anchor_bound_s': .031}}


def synthetic_frames(count, seed=0):
    """Preserve the committed M3 Max XML tree, replacing observations with fiction.

    In particular this retains all cluster/core DVFM arrays, rather than padding
    a tiny dictionary with an unrepresentative large string.
    """
    template = (ROOT / 'tests/fixtures/powermetrics_sample.plist').read_bytes().split(b'\0')[0]
    document = plistlib.loads(template)
    document['hw_model'] = 'synthetic-M3-Max'
    document['kern_osversion'] = 'synthetic'
    document['kern_bootargs'] = ''
    document['kern_boottime'] = 0
    document['timestamp'] = datetime(2026, 1, 1)
    # Every numeric observation, including unused per-core counters, is synthetic.
    def reset(value):
        if isinstance(value, dict):
            return {k: reset(v) for k, v in value.items()}
        if isinstance(value, list):
            return [reset(v) for v in value]
        if type(value) is int:
            return 100
        if type(value) is float:
            return 0.5
        return value
    document = reset(document)
    for i in range(count):
        document['timestamp'] = datetime(2026, 1, 1) + timedelta(seconds=seed * 10000 + i // 10)
        document['elapsed_ns'] = 100_000_000 + (i % 7 - 3) * 1000
        document['thermal_pressure'] = ('Nominal', 'Moderate')[i % 17 == 0]
        for j, rail in enumerate(('cpu', 'gpu', 'ane')):
            document['processor'][rail + '_power'] = (j + 1) * 1000.0 + i % 31 / 8 + seed / 64
            document['processor'][rail + '_energy'] = (j + 1) * 100 + i % 3
        for j, state in enumerate(document['gpu']['dvfm_states']):
            state['freq'] = 300 + j * 100
            state['used_ns'] = (i + j) % 11 * 100_000
        # The retained fixture is unindented Apple XML; match that representation.
        yield re.sub(rb'(?m)^\t+', b'', plistlib.dumps(document, sort_keys=False)) + b'\0'


def timed(function, *args, **kwargs):
    wall, cpu = time.perf_counter(), time.process_time()
    result = function(*args, **kwargs)
    return result, {'wall_s': time.perf_counter() - wall, 'cpu_s': time.process_time() - cpu}


def baseline(data):
    records, parsing = timed(parse_powermetrics_records, data, first_record_endpoint_s=1767225600.0)
    rich, rich_parsing = timed(decode_rich_telemetry, data, first_record_endpoint_s=1767225600.0)
    _, mapping = timed(lambda: [round(r.timestamp_s * 1e9) - 1767225500000000000 for r in records])
    _, integration = timed(lambda: [sum(r.rail_power_w[k] * r.elapsed_ns / 1e9 for r in records)
                                   for k in ('cpu_power', 'gpu_power', 'ane_power')])
    def xml_only():
        for frame in data.split(b'\0'):
            if frame.strip():
                ET.fromstring(frame)
    _, xml_time = timed(xml_only)
    return {'bytes': len(data), 'samples': len(records), 'parse_records': parsing,
            'decode_rich': rich_parsing, 'clock_mapping': mapping, 'integration': integration,
            'C_XML_tree_only': xml_time,
            'plistlib_MB_per_cpu_s': len(data) / 1e6 / parsing['cpu_s']}


def synthetic_episode(samples):
    from joulewise.align.apple.sampler import TRACE_DOMAIN
    from joulewise.align.records import ClockMapping, Episode, Turn, ToolCall
    start = round(ENDPOINT * 1e9) + OFFSET - 100_000_000
    # Leave a real right-edge support: this is a simulated episode, not a
    # measurement window, and all turn/phase boundaries are prescribed here.
    end = start + (samples - 2) * 100_000_000
    step = (end - start) // 3
    turns = tuple(Turn(index=i, start_ns=start+i*step+1000, end_ns=start+(i+1)*step-1000,
                       context_tokens=10, prefill_tokens=4, decode_tokens=3,
                       first_token_ns=start+i*step+step//4,
                       tool_calls=(ToolCall('synthetic-tool', start+i*step+step//2,
                                            start+i*step+3*step//4, 0, 0),)) for i in range(3))
    return Episode(episode_id='synthetic', task_pair='synthetic', condition='benign',
                   agent_model='synthetic', endpoint='mock', seed=0, clock_domain='host',
                   start_ns=start, end_ns=end, turns=turns,
                   clock_mappings=(ClockMapping(TRACE_DOMAIN, 'host', OFFSET, 31_000_000, 'synthetic'),))


def raw_analysis(path, episode):
    """Existing desk's raw parser + persisted rich JSON + fresh attribution."""
    from joulewise.adapters.powermetrics import samples_from_records
    from joulewise.align.apple.sampler import power_records
    from joulewise.align.attribution import attribute_episode
    data = path.read_bytes()
    records = parse_powermetrics_records(data, first_record_endpoint_s=ENDPOINT)
    rich = [json.loads(line) for line in path.with_suffix('.rich.jsonl').read_bytes().splitlines() if line.strip()]
    traces, flags = power_records(samples_from_records(records), nominal_interval_ns=100_000_000,
                                  evidence=EVIDENCE)
    joined = replace(episode, power_traces=traces, flags=tuple(dict.fromkeys((*episode.flags, *flags))))
    energy = {}
    for rail in sol.RAILS:
        attributed = attribute_episode(joined, source='powermetrics', channel=rail)
        energy[rail] = {'attribution': asdict(attributed), 'turns': [
            {'turn': turn.index, 'owned_j': sum(s.energy.joules for s in attributed.segments if s.turn == turn.index),
             'owned_half_width_j': sum(s.energy.half_width_j for s in attributed.segments if s.turn == turn.index)}
            for turn in episode.turns]}
    pm = []
    for native, detail in zip(records, rich):
        end = round(detail['timestamp_s'] * 1e9) + OFFSET
        states = (detail.get('gpu') or {}).get('dvfm_states', ())
        active = sum(s.get('used_ns', 0) for s in states)
        clock = sum(s['freq']*s.get('used_ns', 0) for s in states)/active if active else None
        pm.append({'start_ns': end-native.elapsed_ns, 'end_ns': end, 'state': native.thermal_pressure,
                   'active_ns': active, 'clock_mhz': clock})
    return {'native_pm': pm, 'energy': energy}


def reduced_analysis(samples, episode):
    return {'native_pm': samples.native_pm_samples(ENDPOINT, OFFSET),
            'energy': sol.turn_energy_table(samples, episode, first_record_endpoint_s=ENDPOINT,
                                            nominal_interval_ns=100_000_000, evidence=EVIDENCE)}


def aggregate(rows, members_per_window):
    """Small, deterministic illustrative statistics, never a registered verdict."""
    from statistics import fmean, stdev
    values = [sum(t['owned_j'] for t in r['energy']['gpu_power']['turns']) for r in rows]
    windows = [fmean(values[i:i+members_per_window]) for i in range(0, len(values), members_per_window)]
    return {'window_gpu_owned_j_means': windows, 'mean': fmean(windows),
            'sd': stdev(windows) if len(windows) > 1 else None}


def series_benchmark(root, *, samples, windows, members_per_window, workers):
    root.mkdir()
    paths = []
    for i in range(windows * members_per_window):
        path = root / f'member-{i:04}.plist'
        with path.open('wb') as handle:
            handle.writelines(synthetic_frames(samples, seed=i))
        rich = decode_rich_telemetry(path.read_bytes(), first_record_endpoint_s=ENDPOINT)
        path.with_suffix('.rich.jsonl').write_text(''.join(json.dumps(r, sort_keys=True)+'\n' for r in rich))
        paths.append(path)
    episode = synthetic_episode(samples)
    def raw_path():
        rows = [raw_analysis(path, episode) for path in paths]
        return {'members': rows, 'statistics': aggregate(rows, members_per_window)}
    def reduced_path():
        columns = sol.reduce_members(paths, cache_dir=root/'cache', workers=workers)
        rows = [reduced_analysis(s, episode) for s in columns]
        return {'members': rows, 'statistics': aggregate(rows, members_per_window)}
    raw, raw_time = timed(raw_path)
    print('series: raw path complete', file=sys.stderr, flush=True)
    cold, cold_time = timed(reduced_path)
    print('series: cold reduced path complete', file=sys.stderr, flush=True)
    warm, warm_time = timed(reduced_path)
    raw_bytes = json.dumps(raw, sort_keys=True, separators=(',', ':')).encode()
    assert raw_bytes == json.dumps(cold, sort_keys=True, separators=(',', ':')).encode()
    assert raw_bytes == json.dumps(warm, sort_keys=True, separators=(',', ':')).encode()
    return {'windows': windows, 'members_per_window': members_per_window, 'samples_per_member': samples,
            'raw_bytes': sum(p.stat().st_size for p in paths), 'workers': workers,
            'persisted_rich_bytes': sum(p.with_suffix('.rich.jsonl').stat().st_size for p in paths),
            'raw_path': raw_time, 'cold_reduced_path': cold_time, 'warm_reduced_path': warm_time,
            'byte_identical': True, 'output_sha256': hashlib.sha256(raw_bytes).hexdigest(),
            'statistics': raw['statistics'],
            'note': 'Read raw once plus persisted rich JSON, map/attribute/aggregate; illustrative statistics, not the future primary engine. CPU time excludes worker children.'}


def member_benchmark(root, samples, members_per_window):
    path = root/'large-synthetic.plist'
    with path.open('wb') as handle:
        handle.writelines(synthetic_frames(samples))
    size = path.stat().st_size
    def parse(reference):
        with path.open('rb') as handle:
            return sol.reduce_stream(handle, reference=reference)
    full, full_time = timed(parse, True)
    print('large member: plistlib complete', file=sys.stderr, flush=True)
    extracted, extraction_time = timed(parse, False)
    print('large member: extractor complete', file=sys.stderr, flush=True)
    assert sol.encode_columns(full) == sol.encode_columns(extracted)
    _, miss_time = timed(sol.reduce_file, path, cache_dir=root/'large-cache')
    _, hit_time = timed(sol.reduce_file, path, cache_dir=root/'large-cache')
    # A measured member-count-equivalent sequence; no derived cache is used.
    def window():
        for _ in range(members_per_window):
            parse(False)
    _, window_time = timed(window)
    print('large member: window-equivalent passes complete', file=sys.stderr, flush=True)
    return {'samples': samples, 'raw_bytes': size, 'reduced_bytes': len(sol.encode_columns(extracted)),
            'full_plistlib': full_time, 'extractor': extraction_time,
            'plistlib_MB_per_cpu_s': size/1e6/full_time['cpu_s'],
            'extractor_MB_per_cpu_s': size/1e6/extraction_time['cpu_s'],
            'cold_cache': miss_time, 'warm_cache': hit_time,
            'serial_window_reduction': window_time, 'window_members': members_per_window,
            'window_note': 'Repeated extraction passes over one synthetic file; warm OS page cache; no derived cache.',
            'byte_identical': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--samples', type=int, default=300)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--member-samples', type=int, default=0,
                        help='Also time a large synthetic member (9300 ~= 507 MB).')
    parser.add_argument('--series-samples', type=int, default=0,
                        help='Also benchmark a complete short-member synthetic 11-window series.')
    parser.add_argument('--windows', type=int, default=11)
    parser.add_argument('--members-per-window', type=int, default=22)
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--window-passes', type=int, default=1,
                        help='Extraction passes at large-member size; report count explicitly.')
    args = parser.parse_args()
    data = b''.join(synthetic_frames(args.samples))
    profiler = cProfile.Profile()
    profiler.enable()
    profile_result = baseline(data)
    profiler.disable()
    report = {'synthetic_only': True, 'python': sys.version, 'architecture': platform.machine(),
              'producer_sha256': sol.producer_sha256(), 'unprofiled': baseline(data),
              'profiled': profile_result}
    output = io.StringIO()
    pstats.Stats(profiler, stream=output).strip_dirs().sort_stats('cumulative').print_stats(25)
    report['profile'] = output.getvalue()
    with tempfile.TemporaryDirectory(prefix='reduce-sol-bench-') as directory:
        root = Path(directory)
        if args.member_samples:
            report['member'] = member_benchmark(root, args.member_samples, args.window_passes)
        if args.series_samples:
            report['series'] = series_benchmark(root/'series', samples=args.series_samples, windows=args.windows,
                                                members_per_window=args.members_per_window, workers=args.workers)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
