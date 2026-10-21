#!/usr/bin/env python3
"""Reproduce planning allowances from committed pilots and read-only B6 receipts."""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from joulewise.b5 import chain, plan as window_plan
from joulewise.desk_compress import read_bytes

KIT = Path('configs/campaigns/bytes_mac_check')


def read(path):
    return json.loads(read_bytes(Path(path)))


def rows(path):
    return [json.loads(line) for line in read_bytes(Path(path)).splitlines() if line.strip()]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def request_s(events):
    begin = next((r['timestamp_s'] for r in events if r.get('event_type') == 'sampling_started'), None)
    end = next((r['timestamp_s'] for r in reversed(events) if r.get('event_type') == 'sampling_stopped'), None)
    return None if begin is None or end is None or end <= begin else end - begin


def derive(root, session_roots):
    root = Path(root)
    reg = root / KIT / 'registration'
    pins = read(reg / 'identity_pins.json')['units']
    inventory = read(reg / 'model_artifact_inventory.json')['artifacts']
    weights = {k: sum(f['size_bytes'] for f in v['inventory']) for k, v in inventory.items()}
    roster = read(root / 'configs/campaigns/bytes_v1/roster.json')['models']
    models, sources = {}, []
    for m in roster:
        if not m['pilot']:
            continue
        path = root / 'docs/design/bytes_pilot' / m['pilot']
        pilot = read(path)
        times = [r['total_s'] for r in pilot['runs']]
        models[m['model_id']] = {'request_s': times, 'load_s': pilot['load_s'],
            'source': {'path': path.relative_to(root).as_posix(), 'sha256': sha(path)}, 'weight_bytes': weights[m['model_id']]}
    # F2 (lead, 2026-10-21): interpolate, never fit. Dense Qwen3 only.
    ladder = sorted((weights[k], k) for k in ('qwen3-4b', 'qwen3-8b', 'qwen3-14b', 'qwen3-32b'))
    target = weights['qwen3-8b-8bit']
    lower = max((w, k) for w, k in ladder if w < target)
    upper = min((w, k) for w, k in ladder if w > target)
    fraction = (target - lower[0]) / (upper[0] - lower[0])
    lo, hi = models[lower[1]], models[upper[1]]
    interpolate = lambda a, b: a + fraction * (b - a)
    models['qwen3-8b-8bit'] = {
        'request_s': [interpolate(a, b) for a, b in zip(lo['request_s'], hi['request_s'], strict=True)],
        'load_s': interpolate(lo['load_s'], hi['load_s']), 'weight_bytes': target,
        'flag': 'sizing.planning_bound_interpolated',
        'interpolation': {'lower_model': lower[1], 'upper_model': upper[1],
            'lower_weight_bytes': lower[0], 'upper_weight_bytes': upper[0], 'fraction': fraction,
            'sources': [lo['source'], hi['source']],
            'formula': 'q = (W_target-W_low)/(W_high-W_low); each repeat total_s and load_s = low+q*(high-low)',
            'authority': 'F2, activation 283e9802, 2026-10-21; memory-bandwidth-bound decode; planning only'}}
    observations, fixed, overheads, rates, original_sizes, fixed_sizes = [], [], [], [], [], []
    reference_times = []
    for session in map(Path, session_roots):
        clock_path = session / 'custody/collection/run_clock.jsonl'
        journal_path = session / 'custody/night/chain-stages.jsonl'
        compressed_path = session / 'archive.desk/compression.jsonl'
        sources.extend({'path': str(p), 'sha256': sha(p)} for p in (clock_path, journal_path, compressed_path))
        original = {r['path']: r['size'] for r in rows(compressed_path) if r.get('event') == 'compress'}
        pairs = defaultdict(dict)
        for row in rows(clock_path):
            pairs[row['run_id']][row['event']] = row
        by_stage = defaultdict(float)
        stage_rows = rows(journal_path)
        # Shell stage stamps are integer epoch seconds (date +%s), so
        # their endpoint represents [stamp, stamp+1). Include every member,
        # including failed rows, before deriving disjoint stage overhead.
        for pair in pairs.values():
            if not {'start', 'end'} <= pair.keys():
                continue
            a, b = pair['start']['clock']['wall_s'], pair['end']['clock']['wall_s']
            for stage in stage_rows:
                if (stage.get('kind') == 'campaign_collection'
                    and stage['started_epoch_s'] <= a <= b < stage['ended_epoch_s'] + 1):
                    by_stage[stage['stage_id']] += b - a
                    break
        observed_bytes = 0
        for rid, pair in pairs.items():
            if not {'start', 'end'} <= pair.keys():
                continue
            bundle = next((session / 'archive/sources' / kind / rid for kind in ('claim-runs', 'bound-runs')
                           if (session / 'archive/sources' / kind / rid / 'events.jsonl').is_file()), None)
            if bundle is None or read(bundle / 'summary_metrics.json').get('status') != 'succeeded':
                continue
            events = rows(bundle / 'events.jsonl')
            request = request_s(events)
            if request is None:
                continue
            wall = pair['end']['clock']['wall_s'] - pair['start']['clock']['wall_s']
            meta = read(bundle / 'metadata.json')
            stamps = meta['uncertainty_evidence']['clock_anchor']['clock_stamps']
            stream = stamps['post_parse']['monotonic_after_s'] - stamps['pre_spawn']['monotonic_before_s']
            # Compression journal preserves original byte counts. Round every
            # original file UP to the volume allocation quantum (statvfs.f_frsize),
            # and retain at least today's allocated size. No compression saving
            # is assumed during the window. Two live copies: raw + archive.
            size = 0
            quantum = os.statvfs(bundle).f_frsize
            for f in bundle.rglob('*'):
                if not f.is_file():
                    continue
                info = f.stat()
                raw_name = str(f).removesuffix('.zst') if f.suffix == '.zst' else str(f)
                raw_size = original.get(raw_name, info.st_size)
                size += max(info.st_blocks * 512, math.ceil(raw_size / quantum) * quantum)
            observed_bytes += size
            rates.append(size / wall)
            original_sizes.append(size)
            cfg = read(bundle / 'config.json')
            source = cfg.get('model', {}).get('source')
            if source == pins['neg8_reference']['model_source']:
                reference_times.append(request)
            obs = {'session': session.name, 'run_id': rid, 'member_wall_s': wall, 'request_s': request,
                'stream_s': stream, 'non_request_s': wall - request, 'stream_non_request_s': stream - request,
                'original_allocated_upper_bytes': size, 'allocation_quantum_bytes': quantum,
                'event_sha256': sha(bundle / 'events.jsonl'), 'metadata_sha256': sha(bundle / 'metadata.json')}
            observations.append(obs)
        # Fixed session files (calibrations, meter/monitor, reduction products),
        # at original uncompressed allocation, excluding every run bundle.
        bundle_roots = [p.parent for p in (session / 'archive/sources').glob('*-runs/*/config.json')]
        bundle_roots += [p.parent for p in (session / 'runs-parent').glob('*/*/config.json')]
        fixed_bytes = 0
        excluded = set(bundle_roots)
        for directory, children, filenames in os.walk(session):
            directory = Path(directory)
            children[:] = [n for n in children if directory / n not in excluded]
            for name in filenames:
                f = directory / name
                info = f.stat()
                raw_name = str(f).removesuffix('.zst') if f.suffix == '.zst' else str(f)
                size = original.get(raw_name, info.st_size)
                quantum = os.statvfs(f).f_frsize
                fixed_bytes += max(info.st_blocks * 512, math.ceil(size / quantum) * quantum)
        fixed_sizes.append(fixed_bytes)
        stages = rows(journal_path)
        collections = [s for s in stages if s.get('kind') == 'campaign_collection']
        overheads.extend(max(0, s['ended_epoch_s'] - s['started_epoch_s'] - by_stage[s['stage_id']])
                         for s in collections)
        # These chain records are disjoint in real B6 custody. Their union
        # avoids double-counting any nested record and excludes collection.
        intervals = [(s['started_epoch_s'], s['ended_epoch_s']) for s in stages
                     if s.get('kind') != 'campaign_collection' and 'started_epoch_s' in s]
        merged = []
        for a, b in sorted(intervals):
            if merged and a <= merged[-1][1]: merged[-1][1] = max(merged[-1][1], b)
            else: merged.append([a, b])
        fixed.append(sum(b - a for a, b in merged))
    if not observations or not reference_times:
        raise ValueError('successful B6 member/reference receipts are required')
    # Apply exactly one shared observed-spread rule to all models, including
    # the F2 row and the measured reference. No fixed percentage padding.
    margin = max(max(v['request_s']) / min(v['request_s']) - 1 for v in models.values())
    margin = max(margin, max(reference_times) / min(reference_times) - 1)
    non_request = max(o['non_request_s'] for o in observations)
    stream_extra = max(o['stream_non_request_s'] for o in observations)
    for k, v in models.items():
        mean = sum(v['request_s']) / len(v['request_s'])
        # The archive residual includes the old model load. Add the new
        # pilot load without subtracting it: disclosed conservative envelope.
        v['member_allowance_s'] = (mean + v['load_s'] + non_request) * (1 + margin)
        v['stream_allowance_s'] = (mean + stream_extra) * (1 + margin)
    reference = (sum(reference_times) / len(reference_times) + non_request) * (1 + margin)
    tree = read(root / KIT / 'plan_tree.json')
    count = {s['stage_id']: s['expected_count'] for s in tree['stage_graph'] if s['kind'] == 'campaign_collection'}
    counts = {k: v['config_count'] for k, v in pins.items()}
    member_s = sum(counts[k] * v['member_allowance_s'] for k, v in models.items()) + counts['neg8_reference'] * reference
    # Registered chain settle: one before pre-calibration, one per collection.
    settles = (len(count) + 1) * chain.SETTLE_S
    stage_overhead = max(overheads)
    fixed_s = max(fixed)
    span = member_s + settles + len(count) * stage_overhead + fixed_s
    # Largest observed original bundle AND observed bytes/s scaled to the
    # longest planned member. Two raw/archive copies; two backups may coexist
    # on S's volume. Claim/bound backups partition the roster, so their
    # combined payload is one more copy: three copies at peak. Fixed custody uses
    # the observed uncompressed non-bundle session footprint, scaled for
    # growth from the archived session's member-time sum to this planned window.
    per_copy = math.ceil(max(max(original_sizes), max(rates) * max(reference, *(v['member_allowance_s'] for v in models.values()))))
    peak_copies = 3  # raw + archive + disjoint claim/bound backups
    per_member = per_copy
    # Fixed journals grow with duration; apply the same observed byte-rate
    # envelope over the maximum window (including T0/pause/WAIT), not a fixed factor.
    window_max = 60 * math.ceil((math.ceil(span) + window_plan.T0_STAGE_CAP_S
                                + window_plan.PAUSE_LIMIT_S + window_plan.SESSION_WAIT_BUDGET_S) / 60)
    fixed_bytes = math.ceil(max(fixed_sizes) * max(1, window_max / sum(o['member_wall_s'] for o in observations)))
    # WAIT occurs with a live member sampler. Its session-wide budget can
    # add samples beyond the normal observed member envelope. Agent pauses
    # are between members; continuous meter/monitor growth is in fixed_bytes.
    extra_wait_raw_bytes = math.ceil(max(rates) * window_plan.SESSION_WAIT_BUDGET_S)
    extra_wait_peak_bytes = peak_copies * extra_wait_raw_bytes
    sized = {'pack_id': 'bytes-mac-check', 'programmed_span_s': span,
        'T_stream_max_s': max(reference, *(v['stream_allowance_s'] for v in models.values())),
        'bytes_per_member': per_member, 'member_count': sum(counts.values()), 'fixed_retained_bytes': fixed_bytes,
        'estimated_footprint_bytes': peak_copies * per_member * sum(counts.values()) + fixed_bytes + extra_wait_peak_bytes,
        'extra_wait_peak_bytes': extra_wait_peak_bytes,
        'measured_margin': margin, 'models': models, 'reference_member_allowance_s': reference,
        'counts_by_model': counts, 'collection_stages': len(count),
        'breakdown': {'members_s': member_s, 'settles_s': settles, 'fixed_s': fixed_s,
            'collection_stage_overhead_s': stage_overhead, 'collection_overheads_s': len(count) * stage_overhead},
        'disk_derivation': {'peak_copies': peak_copies, 'window_max_s': window_max,
            'session_wait_budget_s': window_plan.SESSION_WAIT_BUDGET_S, 'extra_wait_raw_bytes': extra_wait_raw_bytes,
            'extra_wait_peak_bytes': extra_wait_peak_bytes,
            'time_budget_source': 'joulewise.b5.plan: T0_STAGE_CAP_S, PAUSE_LIMIT_S, SESSION_WAIT_BUDGET_S; same minute-rounded window formula', 'max_observed_fixed_session_bytes': max(fixed_sizes), 'observed_member_wall_sum_s': sum(o['member_wall_s'] for o in observations), 'max_observed_original_bundle_bytes': max(original_sizes),
            'max_observed_bundle_bytes_per_wall_s': max(rates), 'estimated_per_copy_bytes': per_copy,
            'formula': 'ceil(max(max_original_allocated_bundle, max_original_bytes/member_wall_s * longest_planned_member_s)); peak 3 copies (raw + archive + disjoint claim/bound backups); fixed = observed original non-bundle session bytes * max(1, window_max/sum observed member wall seconds); WAIT extra = ceil(max original bytes/wall_s * registered session WAIT budget) * 3 copies',
            'reserve_bytes': 150 * 1024**3, 'reserve_authority': 'BYTES R6 / block-6 design section 15'}}
    derivation = {'schema_version': 'joulewise.bytes_h_sizing_evidence.v1', 'non_claim': True,
        'sources': sources, 'observations': observations, 'max_non_request_s': non_request,
        'max_stream_non_request_s': stream_extra,
        'reference_request_s': reference_times,
        'formula': 'member=(mean pilot request + pilot load + max B6(member_wall-request))*(1+margin); stream=(mean request+max B6(stream-request))*(1+margin); span=sum(count*member)+(collections+1)*SETTLE_S+collections*max observed stage overhead+max observed fixed work',
        'margin_derivation': 'max(max/min-1) over each measured pilot request group and archived reference requests; same margin for every model and reference',
        'limits': ['Planning allowances only; H measures real timing, bytes and floors.',
            'Prior model load retained in residual as a conservative allowance; no quiet-machine validation claimed.',
            'Observed first-attempt workload envelope; registered WAIT/pause/T0 budgets remain separately in window_max_s.']}
    return {'schema_version': 'joulewise.b5_sizing.v1', 'non_claim': True, 'packs': {sized['pack_id']: sized},
            'derivation': derivation['formula']}, derivation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session-root', type=Path, action='append', required=True)
    args = parser.parse_args()
    sized, evidence = derive(ROOT, args.session_root)
    reg = ROOT / KIT / 'registration'
    for name, value in (('sizing_b5.json', sized), ('sizing_evidence.json', evidence)):
        (reg / name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps(sized['packs']['bytes-mac-check'], indent=2))


if __name__ == '__main__':
    main()
