"""Fenced readers of production formats; no desk-only data path."""
from __future__ import annotations

import json
import math
import re
import statistics
import struct
from pathlib import Path

from joulewise.schemas import RunStatus

from .paths import children, fence, read_bytes, read_json


def json_lines(path):
    rows = []
    try:
        raw = read_bytes(path)
    except FileNotFoundError:
        return rows
    for line in raw.splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def relative(directory, path):
    """Raw descriptors cannot escape their own attempt, even to unblinded data."""
    root, target = fence(directory), fence(Path(directory) / path)
    if target != root and root not in target.parents:
        raise ValueError('raw path escapes attempt')
    return target


def parse_sntp(text):
    # Apple's sntp: '+0.001234 +/- 0.00 ... server ...'. Other output is
    # retained as an unmeasured query; never guess the meaning of a number.
    for line in text.splitlines():
        match = re.search(r'(?:^|\s)([+-]\d+(?:\.\d+)?)\s+\+/-\s+\d', line)
        if match:
            value = float(match[1])
            return value if math.isfinite(value) else None
        match = re.search(r'offset\s+([+-]?\d+(?:\.\d+)?)\s*(?:s|sec)', line, re.I)
        if match:
            return float(match[1])
    return None


def powermetrics(directory):
    from joulewise.adapters.powermetrics import parse_powermetrics_records, samples_from_records
    info = read_json(fence(directory / 'sampler.json'), {})
    endpoint = info.get('first_record_endpoint_s')
    if endpoint is None:
        return [], [{'reason': 'sampler anchor undefined; raw power retained'}]
    records = parse_powermetrics_records(read_bytes(fence(directory / 'powermetrics.plist')),
                                          first_record_endpoint_s=endpoint)
    samples_from_records(records)  # exercise the production rails conversion
    mapping = info.get('start', {})
    offset = mapping.get('epoch_s', 0)-mapping.get('raw_s', 0)
    rows = [{'start_s': r.timestamp_s-r.elapsed_ns/1e9, 'end_s': r.timestamp_s,
             'raw_start_s': r.timestamp_s-r.elapsed_ns/1e9-offset, 'raw_end_s': r.timestamp_s-offset,
             'total': r.combined_power_w, **r.rail_power_w} for r in records]
    return rows, []


def meter(path):
    from joulewise.external import km003c_parse
    try:
        stream = km003c_parse.parse(fence(path))
    except (ValueError, KeyError, struct.error, TypeError) as e:
        stream = km003c_parse.Stream(None, None, [], [{'parse_error': str(e)}], None, None,
                                     [], [], [], [], fit_error=str(e))
    rows = [{'raw_s': ns/1e9, 'meter': power} for ns, power in zip(stream.host_ns, stream.watts)]
    flags = [{'reason': f.get('detail', f.get('code', 'meter flag')), 'meter': f} for f in km003c_parse.flags(stream)]
    if stream.fit_error:
        flags.append({'reason': 'meter sample/clock fit undefined', 'detail': stream.fit_error})
    if stream.samples:
        gaps = km003c_parse.drops(stream.samples)
        if gaps['dropped']:
            flags.append({'reason': 'meter lost samples', 'drops': gaps})
    fit = None
    if stream.fit and stream.samples:
        residuals = []
        newest = {}
        for dev, batch in zip(stream.samples.dev_ms, stream.samples.batch):
            newest[batch] = dev
        for batch, dev in newest.items():
            residuals.append((stream.batches[batch]['rx']-stream.fit.host_ns(dev))/1e6)
        fit = {'rate_ppm': (stream.fit.b_ns_per_ms/1e6-1)*1e6,
               'rx_residual_sd_ms': statistics.stdev(residuals) if len(residuals) > 1 else None,
               'n': len(residuals), 'method': 'library earliest-arrival sample-index fit',
               'library_statistics': stream.fit.stats}
    return rows, stream, fit, flags


def ps_snapshot(document):
    from joulewise.hazards.contention import Snapshot
    from joulewise.hazards.base import Stamp
    rows = {(r['pid'], r['start_identity']): r for r in document.get('rows', [])}
    return Snapshot(Stamp.from_json(document['started']), Stamp.from_json(document['finished']), rows,
                    None, document.get('error'), document.get('host_cpu'), document.get('host_error'))


def ps_interval(before, after, roots=()):
    from joulewise.hazards.contention import interval
    return interval(ps_snapshot(before), ps_snapshot(after), tree_roots=roots,
                    include_kernel_task=True, limit=.05)


def run_bundle(directory, row):
    doc = read_json(relative(directory, row['bundle'] + '/summary_metrics.json'), {})
    ttft, decode = doc.get('ttft_s'), doc.get('decode_latency_s')
    flags = [] if doc else [{'reason': 'run summary missing'}]
    succeeded = doc.get('status') == RunStatus.SUCCEEDED.value and doc.get('failure_reason') is None
    if row.get('returncode') not in (0, None) or not succeeded:
        flags.append({'reason': 'model child or bundle reported a non-success status',
                      'returncode': row.get('returncode'), 'bundle_status': doc.get('status')})
    failures = []
    if row.get('run_path_error'):
        failures.append({'reason': 'run_path_error', 'detail': row['run_path_error']})
    if row.get('returncode') not in (0, None):
        failures.append({'reason': 'nonzero_exit', 'returncode': row['returncode'],
                         'diagnostics': row.get('exit_diagnostics')})
    if not doc:
        failures.append({'reason': 'run_summary_missing'})
    elif not succeeded:
        failures.append({'reason': doc.get('failure_reason') or 'run_status_not_succeeded',
                         'status': doc.get('status'), 'message': doc.get('failure_message')})
    if not doc.get('phase_energy_j'):
        failures.append({'reason': 'phase_energies_missing'})
    baseline = {'idle_baseline_delivered_s': None, 'idle_baseline_record_count': None,
                'idle_baseline_undefined': 'canonical raw idle baseline missing', 'idle_baseline_attempts': []}
    from joulewise.adapters.powermetrics import parse_powermetrics_records
    raw_dir = relative(directory, row['bundle']+'/raw')
    for path in children(raw_dir):
        if path.name != 'powermetrics_idle.plist' and not re.fullmatch(r'powermetrics_idle_attempt_\d+\.plist', path.name):
            continue
        entry = {'path': str(path.relative_to(directory))}
        try:
            records = parse_powermetrics_records(read_bytes(path))
            entry.update(delivered_s=math.fsum(r.elapsed_ns/1e9 for r in records), records=len(records))
            if not records:
                entry['undefined'] = 'empty idle capture'
            if path.name == 'powermetrics_idle.plist':
                baseline.update(idle_baseline_delivered_s=entry['delivered_s'], idle_baseline_record_count=len(records),
                                idle_baseline_undefined=entry.get('undefined'))
        except (ValueError, OSError) as exc:
            entry['undefined'] = str(exc)
            if path.name == 'powermetrics_idle.plist':
                baseline['idle_baseline_undefined'] = str(exc)
        baseline['idle_baseline_attempts'].append(entry)
    return {**row, 'phase_energy_j': doc.get('phase_energy_j') or {},
            'duration_s': ttft+decode if ttft is not None and decode is not None else None,
            'phase_duration_s': {'prefill': ttft, 'decode': decode},
            'token_rate': doc.get('throughput_tokens_s'),
            'decode_token_rate': doc.get('inter_token_throughput_tokens_s'),
            'summary_metrics': doc, 'flags': flags, 'failure_reasons': failures, **baseline}


def capture(directory, row):
    from .fiducial import derive, report
    capdir = relative(directory, row['directory'])
    info = read_json(capdir / 'capture.json', {})
    sampler = read_json(capdir / 'raw/sampler.json', {})
    try:
        detection = derive(read_bytes(capdir / 'raw/powermetrics.plist'), read_bytes(capdir / 'events.jsonl'),
            sampler['clock_anchor'], protocol_id=info.get('protocol_id'), scale=info.get('scale', 1.))
        values = report(detection)
    except (ValueError, KeyError, OSError) as e:
        values = {'bound_s': None, 'flags': [{'reason': f'capture rederivation undefined: {e}'}]}
    values['flags'] += info.get('instrument_flags', [])
    if row.get('returncode') not in (0, None):
        diagnostics = None
        if row.get('child_stderr'):
            try:
                diagnostics = read_bytes(relative(capdir, row['child_stderr'])).decode(errors='replace')[-4000:]
            except OSError as exc:
                diagnostics = f'child stderr unavailable: {exc}'
        last_line = diagnostics.strip().splitlines()[-1] if diagnostics and diagnostics.strip() else 'reason unavailable'
        values['flags'].append({'reason': 'capture child failed: '+last_line, 'returncode': row['returncode'],
                                'detail': diagnostics, 'capture': row.get('id')})
    return {**row, **values, 'cadence_median_ms': info.get('cadence_median_ms'),
            'faulty_context_reproduced': (info.get('cadence_median_ms') or 0) > 200
                if row.get('condition') == 'utility' else None,
            'sampler': sampler}


def half_crossing(points, command, edge, low, high):
    """Nearest half-amplitude crossing within 1 s; interpolate linearly."""
    threshold = (low+high)/2
    candidates = []
    for (t0, p0), (t1, p1) in zip(points, points[1:]):
        # Lost sample gaps cannot support a precise interpolated edge.
        if t1-t0 > .060 or t1 <= t0 or p1 == p0:
            continue
        crossed = p0 <= threshold < p1 if edge == 'on' else p1 < threshold <= p0
        if crossed:
            t = t0+(threshold-p0)/(p1-p0)*(t1-t0)
            if abs(t-command) <= 1:
                candidates.append(t)
    return min(candidates, key=lambda t: abs(t-command)) if candidates else None


def read_attempt(directory):
    directory = fence(directory)
    document = read_json(directory / 'collection.json', {})
    data = {'segments': [], 'runs': [], 'captures': [], 'flags': [], 'meter_present': False}
    records = []
    if document.get('sampler_dir'):
        try:
            records, flags = powermetrics(relative(directory, document['sampler_dir']))
            data['flags'] += flags
        except (ValueError, OSError) as e:
            data['flags'].append({'reason': f'sampler raw undefined: {e}'})
    meter_rows, stream = [], None
    if document.get('meter_file'):
        try:
            meter_rows, stream, fit, flags = meter(relative(directory, document['meter_file']))
            data.update(meter_present=stream.present, meter_fits=[fit] if fit else [])
            data['flags'] += flags
        except (OSError, ValueError, KeyError) as e:
            data['flags'].append({'reason': f'meter raw undefined: {e}'})
    for s in document.get('segments', []):
        start, end = s['start']['epoch_s'], s['end']['epoch_s']
        rs = [{**r, 'start_s': max(r['start_s'], start), 'end_s': min(r['end_s'], end)}
              for r in records if min(r['end_s'], end) > max(r['start_s'], start)]
        raw_start, raw_end = s['start']['raw_s'], s['end']['raw_s']
        ms = [r for r in meter_rows if raw_start <= r['raw_s'] < raw_end]
        # Rails and meter retain distinct sample counts. Do not interpolate
        # wall samples to pretend they were sampler records.
        combined = rs + [{'meter': r['meter']} for r in ms]
        reports = s.get('load_reports', [])
        data['flags'] += [{'reason': 'load child failed or supplied no resource report',
                          'segment': s.get('id'), 'reading': report} for report in reports
                         if report.get('error') or report.get('returncode') not in (0, None)]
        cpu = sum(r['cpu_seconds'] for r in reports if r.get('cpu_seconds') is not None)
        current = []
        if stream:
            current = [v['B0AC'] for ns, v in zip(stream.poll_ns, stream.smc)
                       if raw_start*1e9 <= ns < raw_end*1e9 and v.get('B0AC') is not None]
        interval = None
        if len(s.get('snapshots', [])) == 2:
            interval = ps_interval(*s['snapshots'], roots=document.get('tree_roots', []))
        ticks = s.get('tick_snapshots', [])
        tick_pairs = [s['snapshots'][0], *ticks, s['snapshots'][-1]] if s.get('snapshots') else []
        accounting = [ps_interval(a, b, roots=document.get('tree_roots', [])) for a, b in zip(tick_pairs, tick_pairs[1:])]
        load_pids = set(s.get('load_pids', []))
        for reading, (a, b) in zip(accounting, zip(tick_pairs, tick_pairs[1:])):
            all_processes = ps_interval(a, b)
            seen = [r for r in all_processes.get('outside_listed', []) if r['pid'] in load_pids]
            missing = [r for r in all_processes.get('unaccounted', []) if r['pid'] in load_pids]
            reading['load_cpu_rate_ps_counted'] = sum(r['cpu_s_per_s'] for r in seen)
            reading['load_cpu_ps_rows'] = seen
            reading['load_unaccounted'] = missing
            reading['load_not_seen'] = sorted(load_pids-{r['pid'] for r in seen}-{r['pid'] for r in missing})
            reading['load_cpu_note'] = 'zero counted work is not proof of zero work; short-lived or exited processes can be invisible'
        tick_values = []
        for reading in accounting:
            window = reading.get('interval', {}).get('wall_ns', [])
            if len(window) == 2:
                t = sum(window)/2e9
                near = [r['total'] for r in rs if r['start_s'] <= t < r['end_s']]
                tick_values.append({'outside_cpu_rate': reading.get('outside_total_cpu_s_per_s'),
                                    'rail_power_w': statistics.mean(near) if near else None,
                                    'epoch_s': t, 'interval': reading})
        data['segments'].append({**s, 'records': combined, 'cpu_seconds': cpu,
            'elapsed_s': end-start, 'battery_current_ma': current,
            'burst_on_s': s.get('burst_on', {}).get('epoch_s'), 'burst_off_s': s.get('burst_off', {}).get('epoch_s'),
            'accounting_intervals': accounting, 'outside_cpu_rate': interval.get('outside_total_cpu_s_per_s') if interval else None,
            'ticks': tick_values})
    data['runs'] = [run_bundle(directory, r) for r in document.get('runs', [])]
    data['captures'] = [capture(directory, c) for c in document.get('captures', [])]
    for row in data['runs']+data['captures']:
        data['flags'] += row.get('flags', [])
    data['clock'] = json_lines(relative(directory, document.get('clock_file', 'clock.jsonl')))
    data['flags'] += [{'reason': 'clock logger probe unmeasured', 'detail': r['error']}
                     for r in data['clock'] if r.get('error')]
    data['longest_sampler_s'] = document.get('longest_sampler_s', 0)
    data['minimum_clock_span_s'] = 10800*document.get('scale', 1.)
    data['queries'] = json_lines(relative(directory, document.get('queries_file', 'sntp.jsonl')))
    data['long_waits'] = json_lines(directory / 'long-wait.jsonl')
    if document.get('test_id') == 'm13-meter-edges':
        edges = []
        for c in data['captures']:
            root = relative(directory, c['directory'])
            mapping = c.get('sampler', {}).get('start', {})
            offset = mapping.get('epoch_s', 0)-mapping.get('raw_s', 0)
            points = [(r['raw_s'], r['meter']) for r in meter_rows]
            powers = [p for _, p in points]
            low = sorted(powers)[int(.1*(len(powers)-1))] if powers else 0
            high = sorted(powers)[int(.9*(len(powers)-1))] if powers else 0
            fits = c.get('detector', {}).get('fits', [])
            pulse = 0
            for event in json_lines(root / 'events.jsonl'):
                typ = event.get('event_type', '')
                if typ not in ('pulse_command_on', 'pulse_command_off'):
                    continue
                edge = typ.rsplit('_', 1)[1]
                raw_command = event['metadata'].get('monotonic_raw_ns')
                command = raw_command/1e9 if raw_command is not None else event['metadata']['clock_stamp']['epoch_s']-offset
                fit = fits[pulse] if pulse < len(fits) else {}
                delta = fit.get('delta_on_s' if edge == 'on' else 'delta_off_s')
                edges.append({'capture': c['id'], 'edge': edge, 'command_s': command,
                    'command_clock': 'CLOCK_MONOTONIC_RAW' if raw_command is not None else 'legacy epoch-to-RAW offset',
                    'meter_s': half_crossing(points, command, edge, low, high),
                    'sampler_s': command+delta if delta is not None else None})
                if edge == 'off':
                    pulse += 1
        data['edges'] = edges
    return data


def flag_segments(data, watch):
    """A hazard reading is in force until the next read (10 s maximum by design)."""
    readings = [(r.get('stamp', {}).get('monotonic_raw_ns', 0)/1e9, r['physics'], r.get('source_job_id'))
                for r in watch if r.get('physics')]
    def bad(values):
        current = values.get('battery_current_ma')
        return (values.get('thermal_level') not in (0, None) or
                current is not None and abs(current)>200 or bool(values.get('error')))
    ends = [next((other[0] for other in readings[i+1:] if other[2] == source_job), t+10)
            for i,(t,values,source_job) in enumerate(readings)]
    spans = [(t, ends[i], source_job)
             for i,(t,values,source_job) in enumerate(readings) if bad(values)]
    data['clock_clean'] = [row for row in data.get('clock', []) if row.get('anchor') is not None and not any(
        (source_job is None or row.get('source_job_id') == source_job) and
        start <= row['anchor']['monotonic_raw_ns']/1e9 < end for start,end,source_job in spans)]
    for collection in ('segments', 'runs', 'captures'):
        for segment in data.get(collection, []):
            start = segment.get('start', {}).get('raw_s', 0)
            stop = segment.get('end', {}).get('raw_s', start)
            flags, thermals = [], []
            for i, (time_s, values, source_job) in enumerate(readings):
                end = ends[i]
                if min(end, stop) <= max(time_s, start):
                    continue
                level = values.get('thermal_level')
                if level is not None:
                    thermals.append(level)
                if level not in (0, None):
                    flags.append('thermal pressure')
                current = values.get('battery_current_ma')
                if current is not None and abs(current) > 200:
                    flags.append('battery current over 200 mA')
                if values.get('error'):
                    flags.append('unmeasured watcher probe')
            segment['hazard_flags'] = sorted(set(flags))
            segment['thermal_levels'] = thermals
            if collection == 'segments' and any(abs(v) > 200 for v in segment.get('battery_current_ma', [])):
                segment['hazard_flags'].append('meter battery current over 200 mA')
    return data
