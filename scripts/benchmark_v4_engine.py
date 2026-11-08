#!/usr/bin/env python3
"""Profile synthetic 11 x 22 full-size desk exports and prove byte identity.

No inference, live probes, weights, study data or network. At most two workers
by default, to coexist with Ed's separate blinded analysis. Timing is separate
from the fill and includes input parsing/verification and output serialization.
"""
import argparse
import cProfile
import json
from pathlib import Path
import pstats
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.align.v4_analysis import analyze, canonical
from joulewise.align.v4_analysis.io import digest, input_path, load
from joulewise.align.v4_analysis.synthetic import series


def write_fixture(root, *, full_ids=True):
    root.mkdir(parents=True, exist_ok=False)
    payload = series(identity_tokens='full' if full_ids else 8)
    for w in payload['windows']:
        records = []
        slots = []
        for m in w.pop('members'):
            slots.append(m['slot'])
            records.append({**m['thermal'], 'run_id': m['slot']['run_id'],
                'summary': m['summary'], 'captured': m['captured'], 'dc_secondary': m['dc']})
        raw = canonical(dict(members=records))
        filename = w['window']+'.json'
        (root/filename).write_bytes(raw)
        source = dict(path=filename, sha256=digest(raw))
        w.update(thermal_source=source, residual_source=source, roster=slots)
    (root/'input.json').write_bytes(canonical(payload))
    return root/'input.json'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='new synthetic artifact directory')
    parser.add_argument('--workers', type=int, choices=range(2, 5), default=2)
    parser.add_argument('--small-ids', action='store_true')
    parser.add_argument('--profile', action='store_true')
    args = parser.parse_args(argv)
    root = input_path(args.output)
    root.mkdir(parents=True, exist_ok=False)
    path = write_fixture(root/'fixture', full_ids=not args.small_ids)
    receipts = []
    expected = None
    for workers in (1, args.workers):
        started = time.perf_counter()
        payload = load(path)
        loaded = time.perf_counter()
        profile = cProfile.Profile() if args.profile and workers == 1 else None
        if profile:
            profile.enable()
        fill, verdict = analyze(payload, workers=workers)
        if profile:
            profile.disable()
            profile.dump_stats(root/'serial.pstats')
            with (root/'profile.txt').open('w') as out:
                pstats.Stats(profile, stream=out).sort_stats('cumulative').print_stats(35)
        analyzed = time.perf_counter()
        result = canonical(fill), canonical(verdict)
        ended = time.perf_counter()
        (root/f'fill-w{workers}.json').write_bytes(result[0])
        (root/f'verdict-w{workers}.json').write_bytes(result[1])
        if expected is not None and result != expected:
            raise AssertionError('serial/parallel output bytes differ')
        expected = result
        receipts.append(dict(workers=workers, load_s=loaded-started,
            analysis_s=analyzed-loaded, serialization_s=ended-analyzed, total_s=ended-started,
            fill_sha256=digest(result[0]), verdict_sha256=digest(result[1]),
            source_files_read=len(payload['input_census'])))
        del payload, fill
    report = dict(schema='joulewise.align_v4.synthetic_benchmark.v1', synthetic=True,
        windows=11, members=242, turns_per_member=12, identity_tokens='small' if args.small_ids else 'full',
        fixture_bytes=sum(p.stat().st_size for p in (root/'fixture').iterdir()),
        byte_identical=True, timings=receipts,
        timing_note='Profiled timings include profiler overhead' if args.profile else 'Wall clock; no profiler overhead',
        speedup=receipts[0]['total_s']/receipts[1]['total_s'])
    (root/'timings.json').write_bytes(canonical(report))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
