"""Test-side encoders of actual instrument bytes, independent of kit readers."""
from __future__ import annotations

import dataclasses
import datetime
import json
import math
import plistlib
import struct
from pathlib import Path

EPOCH = 1_790_000_000.
RAW = 1000.


def plist_stream(records):
    docs = []
    for r in records:
        duration = r['end_s']-r['start_s']
        rails = {rail: r.get(rail, 0.) for rail in ('cpu_power', 'gpu_power', 'ane_power')}
        processor = {k: v*1000 for k, v in rails.items()}
        processor.update({k.replace('power', 'energy'): round(v*duration*1000) for k, v in rails.items()})
        docs.append(plistlib.dumps({'timestamp': datetime.datetime.fromtimestamp(
            math.floor(r['end_s']), datetime.timezone.utc), 'elapsed_ns': round(duration*1e9),
            'is_delta': True, 'hw_model': 'Mac15,9', 'kern_osversion': '25G83', 'processor': processor}))
    return b'\0'.join(docs)+b'\0'


def meter_stream(powers, *, start_raw=RAW, start_epoch=EPOCH, drop=None, lag_s=0.):
    lines = [{'k': 'h', 'schema': 'joulewise.km003c_stream.v1', 'status': 'streaming', 'reason': None,
              'model':'POWER-Z KM003C', 'vid':'ffff', 'pid':'ffff', 'qos':'default',
              'init_errors':[], 'process_id':0,
              'sps': 50, 'poll_s': .02, 'smc_keys': ['B0AC','B0AV','PDTR','PSTR','PPBR'],
              'smc_units': {'B0AC':'mA','B0AV':'mV','PDTR':'W','PSTR':'W','PPBR':'W'},
              'rate_idx': 2, 'start_raw_ns': round(start_raw*1e9), 'start_mono_ns': round(start_raw*1e9),
              'start_real_ns': round(start_epoch*1e9)}]
    # The parser's 20-byte sample is: seq uint16, marker uint16, V microvolt
    # int32, I microamp int32, then four uint16 auxiliary words.
    sample = struct.Struct('<HHiiHHHH')
    for i, power in enumerate(powers):
        if i == drop:
            continue
        raw_s = start_raw+i*.02+lag_s
        payload = sample.pack((i*20)%65536, 0, 28_000_000, round(power/28*1e6), 0, 0, 0, 0)
        lines.append({'k': 'b', 'tx': round(raw_s*1e9)-1_000_000, 'rx': round(raw_s*1e9),
                      'rt': round((start_epoch+i*.02)*1e9), 'n': 1, 'p': payload.hex(),
                      'smc': {'B0AC': 0, 'B0AV': 12000, 'PDTR':power, 'PSTR':power, 'PPBR':0.}})
    lines.append({'k': 't', 'polls':len(powers)-(drop is not None), 'empties':0, 'bad':0, 'usb_errors':0,
                  'elapsed_s':len(powers)*.02, 'stop_reason':'stop_file',
                  'utime_s':0.,'stime_s':0.,'maxrss':0,'nvcsw':0,'nivcsw':0,
                  'end_raw_ns': round((start_raw+len(powers)*.02)*1e9),
                  'end_mono_ns': round((start_raw+len(powers)*.02)*1e9)})
    return ''.join(json.dumps(r)+'\n' for r in lines).encode()


def ps_bytes(cpu, *, pid=4242, name='fixture-qk-daemon'):
    minutes = int(cpu//60)
    seconds = cpu-minutes*60
    return (f'  PID  PPID                  STARTED     TIME UCOMM\n'
            f' {pid} 1 Wed Oct 14 12:00:00 2026 {minutes}:{seconds:05.2f} {name}\n').encode()


def power_attempt(path, segments, *, meter=False, kind='measurement'):
    """Create raw plist + real meter bytes and an ordinary collection manifest."""
    path.mkdir(parents=True, exist_ok=True)
    rails = path/'rails'
    rails.mkdir()
    rows, descriptors, powers = [], [], []
    cursor = EPOCH
    rawcursor = RAW
    for i, s in enumerate(segments):
        duration = s.get('duration_s', 2.)
        descriptor = {**s, 'id': f's{i:03d}', 'start': {'epoch_s': cursor, 'raw_s': rawcursor},
                      'end': {'epoch_s': cursor+duration, 'raw_s': rawcursor+duration},
                      'load_reports': [{'cpu_seconds': s.get('cpu_seconds', 0)}]}
        if s.get('kind') == 'burst':
            on = cursor+s.get('placement_s', .5)
            descriptor.update(burst_on={'epoch_s': on}, burst_off={'epoch_s': on+s.get('burst_s', .62)})
        descriptors.append(descriptor)
        for j in range(round(duration/.1)):
            power = s.get('power', .05)
            if s.get('kind') == 'burst':
                p0 = cursor+j*.1
                fraction = max(0., min(p0+.1, on+s.get('burst_s', .62))-max(p0, on))/.1
                power = .05+4*fraction
            if 'scatter' in s:
                power += s['scatter'][j%len(s['scatter'])]
            rows.append({'start_s': cursor+j*.1, 'end_s': cursor+(j+1)*.1,
                         'cpu_power': power, 'gpu_power': s.get('gpu', 0), 'ane_power': 0.})
        powers += [s.get('meter_power', s.get('power', .05)) for _ in range(round(duration/.02))]
        cursor += duration
        rawcursor += duration
    (rails/'powermetrics.plist').write_bytes(plist_stream(rows))
    anchor = {'first_sample_end_point_epoch_s': EPOCH+.1}
    (rails/'sampler.json').write_text(json.dumps({'first_record_endpoint_s': EPOCH+.1,
        'clock_anchor': anchor, 'start': {'epoch_s': EPOCH, 'raw_s': RAW}}))
    doc = {'kind': kind, 'sampler_dir': 'rails', 'segments': descriptors, 'sampler_spans_s': [cursor-EPOCH]}
    if meter:
        (path/'meter.jsonl').write_bytes(meter_stream(powers))
        doc['meter_file'] = 'meter.jsonl'
    (path/'collection.json').write_text(json.dumps(doc))
    return doc


def synthetic_capture(*, count=59, offset=.012):
    """59 pulses, production v3 byte shape, with a constructed known delay."""
    from joulewise.clock import ClockStamp
    from joulewise.uncertainty_evidence import ACTIVE_CAPTURE_ANCHOR_METHOD, resolve_anchor_deriver
    from joulewise.adapters.powermetrics import anchor_records_from_powermetrics, parse_powermetrics_records
    from joulewise.powermetrics_fiducial import PROTOCOL_ID
    first = EPOCH+.05
    warmups = [(first+2.95+2.5*i, first+3.95+2.5*i) for i in range(3)]
    # Encode the frozen van-der-Corput gaps independently.
    pulses, cursor = [], first+14.95
    for i in range(1, count+1):
        pulses.append((cursor, cursor+1.))
        n, vdc, factor = i, 0., .5
        while n:
            vdc += (n%2)*factor
            n //= 2
            factor /= 2
        cursor += 2.5+vdc
    end = pulses[-1][1]+5.
    records = []
    for i in range(math.ceil((end-first)/.1)+1):
        t = first+i*.1
        overlap = sum(max(0., min(t, off+offset)-max(t-.1, on+offset))/.1
                      for on, off in warmups+pulses)
        records.append({'start_s': t-.1, 'end_s': t, 'gpu_power': 2+20*overlap,
                        'cpu_power': 0., 'ane_power': 0.})
    raw = plist_stream(records)
    def cs(epoch):
        mono = epoch-EPOCH+RAW
        return ClockStamp(epoch, mono-1e-6, mono+1e-6, 1e-6, 1e-6)
    stamps = {'pre_spawn': cs(first-.101), 'first_parse': cs(first+.001),
              'sampling_started': cs(first+.15), 'sampling_stopped': cs(end+.5), 'post_parse': cs(end+1.)}
    anchor = resolve_anchor_deriver(ACTIVE_CAPTURE_ANCHOR_METHOD)(stamps=stamps,
        records=anchor_records_from_powermetrics(parse_powermetrics_records(raw)))
    events = []
    for kind, pairs in (('warmup', warmups), ('pulse', pulses)):
        for i, (on, off) in enumerate(pairs):
            for edge, epoch in (('on', on), ('off', off)):
                events.append({'timestamp_s': epoch, 'event_type': f'{kind}_command_{edge}',
                               'metadata': {'clock_stamp': dataclasses.asdict(cs(epoch)), f'{kind}_index': i}})
    return raw, ''.join(json.dumps(e)+'\n' for e in events).encode(), anchor, PROTOCOL_ID


def capture_meter_stream(events):
    """Meter bytes with a 12 ms lag from these synthetic capture commands."""
    pending, pairs = {}, []
    for row in (json.loads(line) for line in events.splitlines()):
        kind, edge = row['event_type'].split('_command_')
        t = row['timestamp_s']-EPOCH
        if edge == 'on':
            pending[kind] = t
        else:
            pairs.append((pending.pop(kind), t))
    duration = max(off for _, off in pairs)+5
    powers = []
    for i in range(math.ceil(duration/.02)):
        t = i*.02
        powers.append(28.+sum(10*min(max(0., min(1., (t-(on+.012-.02))/.04)),
                                      max(0., min(1., ((off+.012+.02)-t)/.04))) for on, off in pairs))
    return meter_stream(powers)
