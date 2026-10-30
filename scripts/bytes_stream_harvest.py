#!/usr/bin/env python3
"""Harvest the isolated known-bytes archive into the unchanged reader contract."""
from __future__ import annotations

import argparse
import bisect
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.bytes_stream_capture import read, write, sha
from joulewise.external import km003c_parse as kp


def native_trace(capture):
    """Reparse original plist; adapter evidence supplies the current-era anchor.

    Native elapsed_ns advances the RAW timeline. No point interpolation and
    no independent fit of the power trace is introduced here.
    """
    from joulewise.adapters.powermetrics import parse_powermetrics_records, decode_rich_telemetry
    stop = read(capture/'capture_stop.json')
    anchor = stop['uncertainty_evidence']['clock_anchor']['first_sample_end_point_epoch_s']
    if anchor is None:
        raise ValueError('continuous capture has no resolved native anchor')
    raw = (capture/'raw/powermetrics.plist').read_bytes()
    records = parse_powermetrics_records(raw, first_record_endpoint_s=anchor)
    rich = decode_rich_telemetry(raw, first_record_endpoint_s=anchor)
    stamp = stop['start_stamp']
    # The adapter used RAW brackets. Pair the first native endpoint with that
    # same epoch/RAW observation, then advance only by native integer durations.
    endpoint = round((anchor-stamp['epoch_s'] +
                      (stamp['monotonic_before_s']+stamp['monotonic_after_s'])/2)*1e9)
    rows = {'rails': [], 'gpu': []}
    previous = None
    for i, record in enumerate(records):
        if i:
            endpoint += record.elapsed_ns
        start = endpoint - record.elapsed_ns
        if record.elapsed_ns <= 0 or previous is not None and start < previous:
            raise ValueError('native support order invalid at row ' + str(i))
        previous = endpoint
        for key, power in (('rails', math.fsum(record.rail_power_w.values())),
                           ('gpu', record.rail_power_w['gpu_power'])):
            if not math.isfinite(power) or power < 0:
                raise ValueError('invalid native power at row ' + str(i))
            rows[key].append(dict(start_ns=start, end_ns=endpoint, power_w=power))
    device = stop['device_metadata']
    stack = dict(telemetry_backend=device.get('telemetry'),
                 measurement_boundary_label={'rails': device.get('rail_manifest')})
    gpu = [dict(start_ns=row['start_ns'], end_ns=row['end_ns'], state=desc['gpu'])
           for row,desc in zip(rows['gpu'],rich) if desc.get('gpu') is not None]
    return rows, stack, gpu


def rail_energy(rows, span, bound):
    from joulewise.bundle_read import TracePoint, Window
    from joulewise.reduce import _integrate, _anchor_shift_envelope
    if not rows or rows[0]['start_ns'] > span[0] or rows[-1]['end_ns'] < span[1]:
        return None, None
    origin = span[0]
    curve = [TracePoint((r['end_ns']-origin)/1e9, r['power_w'],
                        (r['start_ns']-origin)/1e9, (r['end_ns']-origin)/1e9) for r in rows]
    window = Window(0, (span[1]-origin)/1e9)
    integral = _integrate(curve, window.start_s, window.end_s)
    envelope = _anchor_shift_envelope([(curve, [window])], bound)
    return integral, None if envelope is None else envelope['max_abs_delta_j']


def points(times, watts, span):
    lo, hi = bisect.bisect_left(times, span[0]), bisect.bisect_left(times, span[1])
    return [dict(stamp_ns=t, power_w=w) for t,w in zip(times[lo:hi],watts[lo:hi])]


def meter_fields(stream, spans):
    """RAW-span adaptation of pass-1 meter_decode's edge prescription.

    kp.integrate is unchanged. Unlike the claim helper, this test retains
    device gaps and reports them for the reader's registered gap charge.
    Receipts already use RAW: DO NOT add raw_offset_ns (that helper converts
    pass-1 controller monotonic spans, which these receipts are not).
    """
    if stream is None or not stream.present or not stream.aligned or stream.fit is None:
        return dict(energy_j={'meter': None, 'battery': None}, idle={s:{'meter': [], 'battery': []}
                    for s in ('pre','post')}, r_max_s=None, tau_s=None, meter_edge_w=None,
                    battery_edge_j=None, battery_samples=[], meter_gaps=None)
    for t, name in ((stream.host_ns, 'meter'), (stream.poll_ns, 'poll')):
        if any(b < a for a,b in zip(t,t[1:])):
            raise ValueError(name + ' stamps not in native order')
    from joulewise.bytes_analysis import _battery_stream_data, _battery_delay_ns
    bt, bw, _ = _battery_stream_data(stream)
    tau_ns = _battery_delay_ns(stream)
    stat = stream.fit.stats
    residual = max(abs(stat[k]) for k in ('excess_latency_ms_min','excess_latency_ms_max'))/1000
    span = spans['stream']
    meter, _ = kp.integrate(stream.host_ns, stream.watts, *span)
    battery, n = kp.integrate(bt, bw, *span)
    if span[0] < stream.host_ns[0] or span[1] > stream.host_ns[-1]:
        meter = None
    # Same T/n sum(abs(P_b)) over each [edge,edge+tau) as meter_decode.
    duration = (span[1]-span[0])/1e9
    battery_edges = None
    if n and bt and stream.poll_ns[-1] >= span[1]+tau_ns:
        battery_edges = [duration/n * math.fsum(abs(w) for w in
            bw[bisect.bisect_left(bt,e):bisect.bisect_left(bt,e+tau_ns)]) for e in span]
    powers = []
    for edge in span:
        right = bisect.bisect_left(stream.host_ns, edge)
        lo = min(max(0,right-1), bisect.bisect_left(stream.host_ns, edge-residual*1e9))
        hi = max(min(len(stream.host_ns),right+1), bisect.bisect_right(stream.host_ns,edge+residual*1e9))
        powers.append(max(stream.watts[lo:hi]) if hi > lo else None)
    gaps = []
    s = stream.samples
    for before, after in zip(s.dev_ms, s.dev_ms[1:]):
        # Enumerate the exact missing device stamps; fit once for the whole stream.
        for name, own in spans.items():
            missing = sum(own[0] <= stream.fit.host_ns(d) < own[1]
                          for d in range(before+s.step_ms, after, s.step_ms))
            if missing:
                gaps.append(dict(span=name, missing_samples=missing))
    idle = {name: {'meter': (points(stream.host_ns,stream.watts,spans[name])
                             if stream.host_ns[0] <= spans[name][0] and stream.host_ns[-1] >= spans[name][1] else []),
                   'battery': points(bt,bw,spans[name])} for name in ('pre','post')}
    return dict(energy_j={'meter': meter, 'battery': battery}, idle=idle,
                r_max_s=residual, tau_s=tau_ns/1e9, meter_edge_w=powers,
                battery_edge_j=battery_edges,
                battery_samples=points(bt,bw,(spans['pre'][0],spans['post'][1])), meter_gaps=gaps)


def harvest(archive):
    """Archive layout: SESSION.json, roots claim/bound, custody, all copied whole.

    No absolute paths recorded at collection are followed. Harvest is fully
    relocatable and reads no live ledger or files outside this archive.
    """
    from joulewise.b6 import calibration
    archive = Path(archive)
    session = read(archive/'SESSION.json')
    claim = archive/'runs_bytes_stream_test'
    capture = claim/'capture'
    diagnostics = []
    scan = read(capture/'SCAN.json') if (capture/'SCAN.json').is_file() else {
        'status': 'knee not found', 'K': None, 'reason': 'scan not completed; see STAGE.json'}
    reg = session['calibration_registration']
    own = [calibration.read_own_capture(claim/'instrument_validation'/s) for s in ('pre','post')]
    cal = calibration.evaluate(*own, reg, [], [archive.name], False)
    bound = None if cal['operative_bound_s'] is None else float(cal['operative_bound_s'])
    try:
        native, stack, gpu = native_trace(capture)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        native, stack, gpu = {'rails': [], 'gpu': []}, {}, []
        diagnostics.append('native capture unavailable: ' + str(exc))
    streams = sorted((archive/'custody/hazards/meter').glob('stream-*.jsonl'))
    meter = None
    if len(streams) == 1:
        try:
            _, _, batches, _ = kp.load(streams[0])
            # parse's governed sort must not repair an out-of-order archive.
            if any(b['rx'] < a['rx'] for a,b in zip(batches,batches[1:])):
                raise ValueError('meter poll order invalid in archive')
            meter = kp.parse(streams[0])  # one and only one fit
        except (OSError, ValueError, KeyError, TypeError) as exc:
            diagnostics.append('meter parse unavailable: ' + str(exc))
    else:
        diagnostics.append('one continuous meter stream required; found ' + str(len(streams)))
    thermal_path = archive/'custody/hazards/monitor/thermal.jsonl'
    thermal = []
    if thermal_path.is_file():
        for line in thermal_path.read_text().splitlines():
            try:
                thermal.append(json.loads(line))
            except ValueError:
                diagnostics.append('thermal journal malformed line retained in archive')
    records = []
    for path in sorted((capture/'calls').glob('*.json')):
        receipt = read(path)
        spans = dict(stream=(receipt['start_ns'],receipt['end_ns']),
            pre=(receipt['idle_pre_start_ns'],receipt['idle_pre_end_ns']),
            post=(receipt['idle_post_start_ns'],receipt['idle_post_end_ns']))
        try:
            h = meter_fields(meter, spans)
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            diagnostics.append(path.name + ': meter spans unavailable: ' + str(exc))
            h = meter_fields(None, spans)
        envelopes = []
        for key in ('rails','gpu'):
            energy, envelope = rail_energy(native[key],spans['stream'],bound)
            h['energy_j'][key] = energy
            envelopes.append(envelope)
            for name in ('pre','post'):
                covered = bool(native[key] and native[key][0]['start_ns'] <= spans[name][0]
                               and native[key][-1]['end_ns'] >= spans[name][1])
                h['idle'][name][key] = [r for r in native[key]
                    if r['start_ns'] < spans[name][1] and r['end_ns'] > spans[name][0]] if covered else []
        h.update(anchor_shift_j=None if any(v is None for v in envelopes) else max(envelopes),
                 operative_timing_bound_s=bound, capture_stack=stack,
                 adapter_max_w=session['adapter_max_w'], adapter_source=session['adapter_source'],
                 battery_source='KM003C poll SMC B0AC/B0AV; km003c_parse.Stream.battery_watts')
        if gpu:
            h['gpu_state'] = [row for row in gpu if row['start_ns'] < spans['stream'][1]
                              and row['end_ns'] > spans['stream'][0]]
        if thermal:
            h['thermal_spans'] = [row for row in thermal
                if spans['stream'][0] <= (row.get('finished') or {}).get('monotonic_raw_ns',-1) <= spans['stream'][1]]
        records.append(dict(receipt=receipt,harvest=h))
    stage = read(capture/'STAGE.json') if (capture/'STAGE.json').is_file() else {}
    if all(k in stage for k in ('measured_session_start_ns','measured_session_end_ns')):
        elapsed = (stage['measured_session_end_ns']-stage['measured_session_start_ns'])/1e9
        for record in records:
            record['harvest']['hour_as_run_s'] = elapsed
    sources = {str(p.relative_to(archive)): sha(p) for p in archive.rglob('*')
               if p.is_file() and p.name not in ('INPUT.json','HARVEST.json','READ.json')}
    return dict(scan=scan, records=records, non_claim=True,
                provenance=dict(sources=sources, calibration=cal, diagnostics=diagnostics,
                                meter_stream_count=len(streams)))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args(argv)
    result = harvest(a.archive)
    write(a.out, result)
    print(json.dumps({'records': len(result['records']), 'scan': result['scan']['status'],
                      'diagnostics': result['provenance']['diagnostics']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
