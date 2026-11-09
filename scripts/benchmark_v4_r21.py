#!/usr/bin/env python3
"""Synthetic full-shape raw series: serial/parallel, cold/cache, fresh decisions.

No study discovery, native inference, weights or network. Two workers maximum
by default, to coexist with the separate blinded analysis on this machine.
"""
import argparse
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.bench_reduce_sol import synthetic_frames
from joulewise.align.records import Episode, Turn, to_json
from joulewise.align.v4_analysis import analyze, canonical
from joulewise.align.v4_analysis.io import digest, input_path, load
from joulewise.align.v4_analysis.synthetic import series
from joulewise.align.apple import reduce_sol as sol

ENDPOINT = 1767225600.


def fixture(root, samples, *, windows=11):
    root.mkdir()
    payload = series(turns=4)
    payload['windows'] = payload['windows'][:windows]
    byte_count = 0
    for wi, w in enumerate(payload['windows']):
        records, slots = [], []
        for m in w.pop('members'):
            slot, thermal = m['slot'], m['thermal']
            ordinal = slot['ordinal']
            start = (1000+wi*10000+ordinal*10)*10**9
            turns = tuple(Turn(index=i, start_ns=start+i*10**9+10_000_000,
                first_token_ns=start+i*10**9+200_000_000, end_ns=start+(i+1)*10**9-10_000_000,
                context_tokens=r['context_tokens'], prefill_tokens=r['prefill_tokens'],
                decode_tokens=r['decode_tokens'], hidden_tokens=r['decode_tokens']-h['decode_tokens'])
                for i, (r,h) in enumerate(zip(m['summary']['residual_rows']['True'],m['summary']['residual_rows']['False'])))
            def gate(kind,a,b,turn=0):
                stamp = dict(epoch_ns=a, monotonic_before_ns=a, monotonic_after_ns=a)
                return dict(kind=kind, start_ns=a, end_ns=b, turn=turn, outcome='released',
                    entry_stamp=stamp, exit_stamp=stamp, exit_sample_ns=b,
                    release=dict(fast_c=40.,slow_c=40.), reference=dict(fast_c=40.,slow_c=40.))
            intervals = [gate('G0',start-2*10**9,start-500_000_000)]
            intervals += [gate('G1',turns[i-1].end_ns, turns[i].start_ns, i) for i in range(1,4)]
            episode = Episode(episode_id=slot['run_id'], task_pair=slot['task_pair'], condition=slot['condition'],
                agent_model=slot['model_id'], endpoint='mock', seed=slot['seed_index'], clock_domain='host',
                start_ns=start, end_ns=start+4*10**9, turns=turns,
                hardware={'thermal': dict(intervals=intervals, policy=dict(sensors=dict(s_fast='F',s_slow='S',fan_keys=[]),
                                            delta_fast_c=1.,delta_slow_c=1.))})
            times = sorted({start+i*500_000_000 for i in range(-6,13)} | {g['end_ns'] for g in intervals})
            journal = [dict(kind='sample',monotonic_ns=t,finished=dict(monotonic_after_ns=t),
                            sensors=dict(F=40.,S=40.),errors={}) for t in times]
            def write(name, data):
                nonlocal byte_count
                (root/name).write_bytes(data); byte_count += len(data)
                return dict(path=name,sha256=digest(data))
            seed = 0 if slot['series_role']=='sentinel' else wi*22+ordinal
            raw = b''.join(synthetic_frames(samples,seed=seed)).replace(b'<string>Moderate</string>',b'<string>Nominal</string>')
            record = dict(run_id=slot['run_id'],captured=True,
                config=write(f'{wi}-{ordinal}.config.json', canonical(m['config'])),
                episode=write(f'{wi}-{ordinal}.episode.json',to_json(episode).encode()),
                powermetrics=write(f'{wi}-{ordinal}.plist',raw),
                first_record_endpoint_s=ENDPOINT, nominal_interval_ns=100_000_000,
                stamps=[dict(epoch_s=ENDPOINT,monotonic_before_s=start/1e9-1.9,
                    monotonic_after_s=start/1e9-1.9,wall_resolution_s=0.,monotonic_resolution_s=0.)],
                clock_evidence=dict(clock_anchor=dict(status='bounded',method='synthetic',
                    wall_minus_monotonic_lower_s=ENDPOINT-(start/1e9-1.9),
                    wall_minus_monotonic_upper_s=ENDPOINT-(start/1e9-1.9),effective_clock_anchor_bound_s=1e-6)),
                journal=journal, turn_rows=[dict(generation=t) for t in thermal['tokens']],
                os_readings=[[t,0] for t in times],registered_os_readings=[[t,0] for t in times],
                registered_span_ns=[times[0],times[-1]], identity_sha256=thermal['identity_sha256'],
                identical_work_group=thermal.get('identical_work_group'), battery=thermal['battery'],
                cohort_identity=payload['cohort']['identity'],configuration=payload['cohort']['configuration'],
                cache_statistics=dict(rebuilds=0))
            records.append(record); slots.append(slot)
        ref = write(w['window']+'.json',canonical(dict(members=records)))
        w.update(raw_source=ref,roster=slots)
    path = root/'input.json'; path.write_bytes(canonical(payload))
    return path, byte_count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=input_path, required=True)
    parser.add_argument('--samples', type=int, default=64)
    parser.add_argument('--workers', type=int, choices=(2,3,4), default=2)
    args = parser.parse_args(argv)
    if args.samples < 60:
        parser.error('at least 60 samples cover the synthetic thermal/episode spans')
    with tempfile.TemporaryDirectory(prefix='v4-r21-') as tmp:
        root = Path(tmp)
        path, byte_count = fixture(root/'raw', args.samples)
        receipts, expected = [], None
        for label, workers, cache in [('serial_cold',1,root/'serial-cache'),
                ('parallel_cold',args.workers,root/'parallel-cache'),('serial_cache',1,root/'serial-cache'),
                ('parallel_cache',args.workers,root/'parallel-cache')]:
            started = time.perf_counter()
            payload = load(path,cache_dir=cache,workers=workers)
            loaded = time.perf_counter()
            fill, verdict = analyze(payload,workers=workers)
            if fill['calibration']['eligible_by_pair'] != dict(spam=56,bank=56) or not any(f['window']=='T3' for f in fill['fits']):
                raise AssertionError('synthetic rehearsal must exercise full calibration and T scoring')
            ended = time.perf_counter()
            result = (canonical(fill),canonical(verdict))
            if expected is not None and result != expected:
                raise AssertionError(label+' full analysis bytes differ')
            expected = result
            receipts.append(dict(mode=label,workers=workers,raw_to_desk_s=loaded-started,
                analysis_s=ended-loaded,total_s=ended-started,fill_sha256=digest(result[0]),verdict_sha256=digest(result[1]),
                eligible_by_pair=fill['calibration']['eligible_by_pair']))
            print(label+' complete', file=sys.stderr,flush=True)
        # Same bytes and same sample count for the pre-change profiler baseline.
        data = b''.join(synthetic_frames(1000))
        original = subprocess.check_output(['git','show','origin/perf/2026-11-08-reduce-sol:joulewise/align/apple/reduce_sol.py'])
        baseline = types.ModuleType('sol_before'); sys.modules['sol_before']=baseline
        exec(compile(original,'<committed-Sol-reducer-before>','exec'),baseline.__dict__)
        parsing = []
        columns = []
        for label,fn in [('element_tree_before',baseline.reduce_stream),('scanner_after',sol.reduce_stream),
                         ('plistlib_oracle',lambda handle: sol.reduce_stream(handle,reference=True))]:
            cpu, wall = time.process_time(),time.perf_counter()
            r = fn(io.BytesIO(data))
            elapsed_cpu,elapsed_wall = time.process_time()-cpu,time.perf_counter()-wall
            columns.append(r.columns)
            parsing.append(dict(mode=label,bytes=len(data),cpu_s=elapsed_cpu,wall_s=elapsed_wall,
                MB_per_cpu_s=len(data)/1e6/elapsed_cpu))
        assert columns[0] == columns[1] == columns[2]
        report = dict(synthetic_only=True,windows=11,members=242,samples_per_member=args.samples,
            source_bytes=byte_count,scanner_available=sol.native.SCAN is not None,
            producer_sha256=sol.producer_sha256(),byte_identical=True,timings=receipts,parser=parsing,
            note='Contended machine; no live data or quiet-window validation. Cold means empty derived cache, not OS cache. Decisions and turn energies recomputed in all four modes.')
        args.output.write_bytes(canonical(report))
        print(json.dumps(report,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
