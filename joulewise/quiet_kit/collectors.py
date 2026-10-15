"""Shared collectors and segment executor, using the existing measurement paths."""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import sys
import time
from pathlib import Path

from .paths import append, atomic_json, create_once, fence, mkdir, read_bytes, read_json

WORKLOADS = {
    'R': 'configs/campaigns/neg8_reference_corpus_v5/neg8-refcorpus-r01.json',
    'A': 'configs/campaigns/d117_floor_qwen3-1p7b_v5/01_phase_decode_absolute/d117fq31p7-df-ph-decode-abs-r01.json',
    'B': 'configs/campaigns/d117_floor_qwen3-8b_v5/01_phase_decode_absolute/d117fq38-df-ph-decode-abs-r01.json',
}


def stamp():
    # Retain the wall/RAW mapping for joining the meter to sampler records.
    raw0 = time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
    real = time.clock_gettime_ns(time.CLOCK_REALTIME)
    raw1 = time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
    return {'epoch_s': real/1e9, 'raw_s': (raw0+raw1)/2e9, 'skew_s': (raw1-raw0)/1e9}


class Sampler:
    def __init__(self, hw, directory, control):
        from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
        from joulewise.clock import SystemClock
        self.hw, self.directory, self.control = hw, mkdir(directory), control
        self.path = fence(self.directory / 'powermetrics.plist')
        self.clock = SystemClock()
        self.adapter = PowermetricsTelemetryAdapter(self.clock, privilege_prefix=('/usr/bin/sudo', '-n'))
        self.adapter._initialize_stream_cursor(self.path)
        self.stamps = {'pre_spawn': self.clock.stamp()}
        argv = self.adapter._command(None, self.path, count=None, interval_ms=100)
        self.process = hw.processes.spawn(argv, directory)
        ready = self.adapter._wait_until_ready(self.process, self.path)
        if not ready.ok:
            hw.processes.stop(self.process)
            raise RuntimeError(ready.message)
        self.stamps['first_parse'] = self.adapter._first_parse_stamp
        rollover = self.adapter._wait_for_native_rollover(self.process, self.path)
        if not rollover.ok:
            hw.processes.stop(self.process)
            raise RuntimeError(rollover.message)
        self.stamps['sampling_started'] = self.clock.stamp()
        self.start = stamp()
        self.closed = False

    def close(self):
        if self.closed:
            return read_json(self.directory / 'sampler.json', {})
        from joulewise.adapters.powermetrics import anchor_records_from_powermetrics, parse_powermetrics_records
        from joulewise.uncertainty_evidence import ACTIVE_CAPTURE_ANCHOR_METHOD, resolve_clock_evidence_deriver
        self.stamps['sampling_stopped'] = self.clock.stamp()
        self.end = stamp()
        gone = self.hw.processes.stop(self.process)
        self.stamps['post_parse'] = self.clock.stamp()
        records = parse_powermetrics_records(read_bytes(self.path))
        evidence, endpoint = resolve_clock_evidence_deriver(ACTIVE_CAPTURE_ANCHOR_METHOD)(
            stamps=self.stamps, records=anchor_records_from_powermetrics(records))
        result = {'start': self.start, 'end': self.end, 'clock_evidence': evidence,
                  'clock_anchor': evidence['clock_anchor'], 'first_record_endpoint_s': endpoint,
                  'clock_stamps': {k: dataclasses.asdict(v) for k, v in self.stamps.items()},
                  'group_teardown': gone, 'span_s': sum(r.elapsed_ns for r in records)/1e9,
                  'cadence_median_ms': __import__('statistics').median(r.elapsed_ns/1e6 for r in records)}
        atomic_json(self.directory / 'sampler.json', result)
        self.closed = True
        return result


def snapshot(hw, directory, index):
    from joulewise.hazards import contention
    snap = contention.take_snapshot(hw.ctx(directory), raw_name=f'boundary-{index:04d}-ps.txt',
                                    host_reader=hw.host_cpu)
    # Exact raw bytes remain beside this serializable snapshot. Convert tuple
    # identity keys to a list; the reader reconstructs library Snapshot rows.
    value = {'started': snap.started.to_json(), 'finished': snap.finished.to_json(),
             'rows': list(snap.rows.values()), 'error': snap.error,
             'host_cpu': snap.host, 'host_error': snap.host_error}
    atomic_json(directory / f'boundary-{index:04d}.json', value)
    return value


def launch_load(hw, kind, duty, duration, directory, priority='interactive'):
    python = hw.model_python if kind == 'gpu' else sys.executable
    argv = [python, '-m', 'joulewise.quiet_kit.loads', kind, '--duty', str(duty),
            '--period-s', '1.0' if kind == 'gpu' else '0.05', '--duration-s', str(duration)]
    if priority == 'background':
        argv = ['/usr/sbin/taskpolicy', '-b', *argv]
    child = hw.processes.spawn(argv, directory)
    return child, argv


def load_report(child):
    try:
        return json.loads(read_bytes(child.quiet_kit_stdout).splitlines()[-1])
    except (OSError, ValueError, IndexError):
        return {'error': 'load child supplied no CPU time report', 'cpu_seconds': None}


def model_config(repo, workload, run_id, *, short_baseline=False):
    config = read_json(fence(repo / WORKLOADS[workload]))
    if config is None:
        raise ValueError(f'missing workload {workload}')
    # M2b's S arm has exactly one additional ruled sampling change.
    if short_baseline:
        if workload != 'R':
            raise ValueError('short-baseline arm requires the reference workload')
        config['sampling']['idle_seconds'] = 50.0
    config['run_id'] = run_id
    tags = config['run_metadata']['tags']
    config['run_metadata']['tags'] = [t for t in tags if t != 'launch_lineage_required'] + ['quiet-kit', 'non-claim']
    fence(config['model']['source'])
    manifest = config.get('workload_profile', {}).get('suite_manifest_ref')
    if manifest:
        fence(repo / manifest)
    return config


def model_run(hw, segment, attempt, index, control):
    workload = segment['workload']
    run_id = f'qk-{attempt.parent.parent.name}-a{attempt.name}-{index:04d}-{workload.lower()}'
    short_baseline = segment.get('arm') == 'S' and segment.get('sampling_idle_seconds') == 50.0
    config = model_config(hw.repo, workload, run_id, short_baseline=short_baseline)
    path = fence(attempt / 'configs' / (run_id+'.json'))
    atomic_json(path, config)
    root = mkdir(attempt / 'runs')
    argv = [hw.model_python, '-m', 'joulewise', 'run', str(path), '--runs-dir', str(root)]
    before = hw.stamp()
    child, code, run_error = None, None, None
    try:
        child = hw.processes.spawn(argv, attempt)
        code = hw.processes.wait(child, control, timeout=1800)
    except (OSError, TimeoutError) as exc:
        run_error = f'{type(exc).__name__}: {exc}'
        code = child.returncode if child else None
    finally:
        if child:
            hw.processes.stop(child)
    if child and code is None:
        code = child.returncode
    end = hw.stamp()
    row = {**segment, 'id': run_id, 'bundle': str(Path('runs') / run_id), 'start': before,
           'end': end, 'argv': argv, 'returncode': code,
           'sampling_idle_seconds': config['sampling']['idle_seconds'],
           'run_path_error': run_error,
           'child_stdout': child.quiet_kit_stdout.name if child else None,
           'child_stderr': child.quiet_kit_stderr.name if child else None,
           'source_config': WORKLOADS[workload], 'config_sha256': hashlib.sha256(read_bytes(path)).hexdigest(),
           'stage_choice': 'decode absolute; longest configured output (512 tokens); no measured energies used'}
    if code or run_error:
        if child:
            row['exit_diagnostics'] = {'stdout': read_bytes(child.quiet_kit_stdout)[-4000:].decode(errors='replace'),
                                       'stderr': read_bytes(child.quiet_kit_stderr)[-4000:].decode(errors='replace')}
        else:
            row['exit_diagnostics'] = {'stdout': '', 'stderr': run_error}
    stream = fence(root / run_id / 'raw/powermetrics.plist')
    if stream.is_file():
        from joulewise.adapters.powermetrics import parse_powermetrics_records
        try:
            row['sampler_span_s'] = sum(r.elapsed_ns for r in parse_powermetrics_records(read_bytes(stream)))/1e9
        except ValueError as e:
            row['sampler_span_undefined'] = str(e)
    append(attempt / 'run-index.jsonl', row)
    return row


def long_wait(hw, segment, attempt, scale, control):
    """20 continuous minutes without a per-process contender or an agent."""
    from joulewise.hazards import contention
    # The regular watcher continues; no load, sampler, meter or model is
    # alive. Snapshot once per ten-second accounting interval.
    quiet_until = hw.now()+segment['duration_s']*scale
    control.runner.state('waiting', current_wait='long_idle', quad=segment['quad'], arm=segment['arm'])
    before = contention.take_snapshot(hw.ctx(), host_reader=None)
    rows = []
    while hw.now() < quiet_until:
        control.wait(min(10*scale, max(0., quiet_until-hw.now())))
        after = contention.take_snapshot(hw.ctx(), host_reader=None)
        reading = contention.interval(before, after, tree_roots=[os.getpid()], include_kernel_task=True, limit=.05)
        row = {'stamp': hw.stamp(), 'interval': reading, 'quad': segment['quad']}
        rows.append(row)
        append(attempt / 'long-wait.jsonl', row)
        if not reading.get('clean'):
            quiet_until = hw.now()+segment['duration_s']*scale
            control.runner.state('waiting', current_wait='long_idle_after_contender',
                                 quad=segment['quad'], reading=reading)
            append(attempt / 'long-wait.jsonl', {'event': 'restart_20_minutes', 'stamp': hw.stamp(),
                                                'quad': segment['quad'], 'reason': reading})
        before = after
    return rows


def collect(hw, plan, attempt, scale, control, kind):
    if plan.test_id == 'm9-time-server':
        return time_queries(hw, plan, attempt, scale, control, kind)
    manifest = {'kind': kind, 'scale': scale, 'test_id': plan.test_id, 'segments': [], 'runs': [], 'captures': [],
                'sampler_spans_s': [], 'tree_roots': [os.getpid()],
                'workload_choices': WORKLOADS if plan.model_runs else {}}
    path = fence(attempt / 'collection.json')
    sampler = meter = None
    meter_stop = fence(attempt / 'meter.stop')
    if plan.meter:
        meter = hw.processes.spawn([sys.executable, str(fence(hw.repo / 'scripts/km003c_monitor.py')),
            '--out', str(fence(attempt / 'meter.jsonl')), '--stop-file', str(meter_stop)], attempt)
        manifest['meter_file'] = 'meter.jsonl'
    try:
        if any(s['kind'] in ('idle', 'cpu', 'gpu', 'mixed', 'burst') for s in plan.segments):
            sampler = hw.sampler(attempt / 'rails', control)
            manifest['sampler_dir'] = 'rails'
        boundary = 0
        for index, segment in enumerate(plan.segments):
            control.check()
            current = {**segment, 'id': f's{index:03d}', 'start': hw.stamp()}
            control.segment = {'id': current['id'], **segment}
            control.runner.state('collecting', segment=control.segment)
            if segment['kind'] == 'capture':
                directory = mkdir(attempt / f'capture-{index:03d}')
                argv = [hw.model_python, '-m', 'joulewise.quiet_kit.capture', '--out', str(directory),
                        '--scale', str(scale), '--kind', kind]
                if segment.get('condition') == 'utility':
                    argv = ['/usr/sbin/taskpolicy', '-c', 'utility', *argv]
                cpu = None
                if segment.get('condition') == 'load':
                    cpu, _ = launch_load(hw, 'cpu', 1., 500*scale, directory)
                child = hw.processes.spawn(argv, directory)
                code = hw.processes.wait(child, control, timeout=1200)
                hw.processes.stop(child)
                from .processes import check_capture_teardown
                check_capture_teardown(directory)
                if cpu:
                    hw.processes.stop(cpu)
                manifest['captures'].append({**current, 'end': hw.stamp(), 'directory': directory.name,
                    'returncode': code, 'argv': argv, 'id': f'capture-{index:03d}'})
                cap = read_json(directory / 'capture.json', {})
                if cap.get('sampler_span_s'):
                    manifest['sampler_spans_s'].append(cap['sampler_span_s'])
            elif segment['kind'] == 'model':
                if sampler:
                    raise RuntimeError('kit sampler must not overlap model sampler')
                row = model_run(hw, segment, attempt, index, control)
                manifest['runs'].append(row)
                if row.get('sampler_span_s'):
                    manifest['sampler_spans_s'].append(row['sampler_span_s'])
            elif segment['kind'] == 'long_wait':
                long_wait(hw, segment, attempt, scale, control)
            elif segment['kind'] == 'soak':
                deadline = hw.now()+segment['duration_s']*scale
                n = 0
                while hw.now() < deadline:
                    w = ('A', 'B')[n%2]
                    row = model_run(hw, {'kind': 'model', 'workload': w, 'block': 'soak'}, attempt, 1000+n, control)
                    manifest['runs'].append(row)
                    if row.get('sampler_span_s'):
                        manifest['sampler_spans_s'].append(row['sampler_span_s'])
                    n += 1
                    atomic_json(path, manifest)
            else:
                snapshots = [snapshot(hw, attempt / 'ps', boundary)]
                boundary += 1
                duration = segment['duration_s']*scale
                children_running = []
                argvs = []
                if segment['kind'] == 'burst':
                    control.wait(segment['placement_s']*scale)
                    current['burst_on'] = hw.stamp()
                    child, argv = launch_load(hw, 'cpu', 1., segment['burst_s']*scale, attempt)
                    children_running.append(child)
                    argvs.append(argv)
                    # Tick snapshots are taken even if a late burst straddles
                    # the first interval; the load child's resource report
                    # supplies its true work when ps cannot see its lifetime.
                elif segment['kind'] in ('cpu', 'gpu', 'mixed'):
                    for load_kind in (('cpu', 'gpu') if segment['kind'] == 'mixed' else (segment['kind'],)):
                        child, argv = launch_load(hw, load_kind, segment['duty'], duration, attempt,
                            segment.get('priority', 'interactive'))
                        children_running.append(child)
                        argvs.append(argv)
                start_mono = hw.now()-segment.get('placement_s', 0)*scale
                segment_until = start_mono+duration
                ticks = []
                next_tick = start_mono+10*scale
                while hw.now() < segment_until:
                    control.wait(min(.1, max(0., segment_until-hw.now())))
                    if hw.now() >= next_tick and hw.now() < segment_until-.05*scale:
                        ticks.append(snapshot(hw, attempt / 'ps', boundary))
                        boundary += 1
                        next_tick += 10*scale
                reports = []
                for child in children_running:
                    code = hw.processes.wait(child, control, timeout=30)
                    reports.append({**load_report(child), 'returncode': code})
                    hw.processes.stop(child)
                current['end'] = hw.stamp()
                if segment['kind'] == 'burst':
                    report = reports[0] if reports else {}
                    offset = current['burst_on']['epoch_s']-current['burst_on']['raw_s']
                    if report.get('start_raw_ns') is not None and report.get('end_raw_ns') is not None:
                        current['burst_on'] = {'raw_s': report['start_raw_ns']/1e9,
                                              'epoch_s': report['start_raw_ns']/1e9+offset}
                        current['burst_off'] = {'raw_s': report['end_raw_ns']/1e9,
                                               'epoch_s': report['end_raw_ns']/1e9+offset}
                    else:
                        current['burst_off'] = {**current['burst_on'],
                            'epoch_s': current['burst_on']['epoch_s']+segment['burst_s']*scale,
                            'raw_s': current['burst_on']['raw_s']+segment['burst_s']*scale}
                    current['actual_placement_s'] = current['burst_on']['epoch_s']-current['start']['epoch_s']
                snapshots.append(snapshot(hw, attempt / 'ps', boundary))
                boundary += 1
                current.update(snapshots=snapshots, tick_snapshots=ticks, load_reports=reports,
                               load_pids=[child.pid for child in children_running], argv=argvs)
                manifest['segments'].append(current)
            atomic_json(path, manifest)
        if sampler:
            metadata = sampler.close()
            sampler = None
            manifest['sampler_spans_s'].append(metadata['span_s'])
        if meter:
            create_once(meter_stop, b'stop\n')
            hw.processes.wait(meter, control, timeout=15)
            hw.processes.stop(meter)
            meter = None
        atomic_json(path, manifest)
    finally:
        if sampler:
            # On an interrupted attempt keep its bytes. Analysis does not
            # need to succeed before process ownership is released.
            try:
                sampler.close()
            except Exception:
                hw.cleanup()
        if meter:
            create_once(meter_stop, b'stop\n')
            hw.processes.stop(meter)


def time_queries(hw, plan, attempt, scale, control, kind):
    from .readers import parse_sntp
    rows = []
    started = hw.now()
    for q in range(10):
        control.wait(max(0., started+q*60*scale-hw.now()))
        for server in ('time.apple.com', 'time.cloudflare.com'):
            control.check()
            argv = ['/usr/bin/sntp', server]
            reply = hw.run_probe(argv, 15.)
            row = {'kind': kind, 'query': q, 'server': server, 'time_s': hw.stamp()['raw_s'],
                    'stdout': reply.stdout.decode(errors='replace'), 'stderr': reply.stderr.decode(errors='replace'),
                    'returncode': reply.returncode, 'error': reply.error}
            row['offset_s'] = parse_sntp(row['stdout']) if reply.returncode == 0 else None
            rows.append(row)
            append(attempt / 'sntp.jsonl', row)
    control.wait(max(0., started+600*scale-hw.now()))
    atomic_json(attempt / 'collection.json', {'kind': kind, 'scale': scale, 'test_id': plan.test_id, 'queries_file': 'sntp.jsonl'})
