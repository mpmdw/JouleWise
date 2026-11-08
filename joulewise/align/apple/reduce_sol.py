"""SOL offline raw-PM reduction, independent of the registered instrument.

The cache contains observations only. Anchoring, turn ownership, uncertainty,
eligibility and all statistical decisions are evaluated afresh by the caller.
No model, config, measurement root or network resource is discovered here.
"""
from __future__ import annotations

from array import array
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import marshal
import math
import os
from pathlib import Path
import plistlib
import re
import struct
import sys
import tempfile
import multiprocessing
from types import CodeType, FunctionType
from xml.etree import ElementTree as ET
from xml.parsers import expat
from . import _reduce_native as native
from .sampler import seconds_ns

SCHEMA = 'joulewise.powermetrics.reduce-sol.v2'
MAGIC = b'JWSOLR1\n'
RAILS = ('cpu_power', 'gpu_power', 'ane_power')
# All arrays are serialized little-endian. A separate validity byte preserves
# null clock values without using NaN as a sentinel.
LAYOUT = (('elapsed_ns', 'q'), ('native_timestamp_ns', 'q'),
          ('cpu_power', 'd'), ('gpu_power', 'd'), ('ane_power', 'd'),
          ('thermal_code', 'I'), ('active_ns', 'd'), ('clock_mhz', 'd'),
          ('clock_valid', 'B'), ('active_integer', 'B'))
ROOT_KEYS = frozenset(('elapsed_ns', 'timestamp', 'processor', 'thermal_pressure', 'gpu'))
PROCESSOR_KEYS = frozenset((*RAILS, 'cpu_energy', 'gpu_energy', 'ane_energy'))
GPU_KEYS = frozenset(('dvfm_states',))
STATE_KEYS = frozenset(('freq', 'used_ns', 'used_ratio'))
CHUNK_BYTES = 1024 * 1024
INTERIOR_SEAM_NS = 1_000  # A37: fixed, symmetric gap/overlap rule; never edges.


def _snap_interior_starts(starts, ends):
    """Snap fresh support starts before any integration or coverage check."""
    snapped = 0
    for i in range(1, len(starts)):
        edge = ends[i-1]
        if starts[i] != edge and edge < ends[i] and abs(starts[i]-edge) <= INTERIOR_SEAM_NS:
            starts[i] = edge
            snapped += 1
    return snapped


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def _integer(text):
    # plistlib treats unprefixed leading-zero numbers as decimal.
    return int(text, 16 if text.startswith(('0x', '0X')) else 10)


def _date(text):
    # The ordinary Apple date. Unusual valid plist dates take the reference path.
    if re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z', text) is None:
        raise ValueError('noncanonical date')
    return datetime.fromisoformat(text[:-1])


def _scalar(element):
    text = element.text or ''
    if element.tag in ('key', 'string'):
        return text
    if element.tag == 'integer':
        return _integer(text)
    if element.tag == 'real':
        return float(text)
    if element.tag == 'true':
        return True
    if element.tag == 'false':
        return False
    if element.tag == 'date':
        return _date(text)
    raise ValueError('unusual scalar')


def _value(node):
    if node.tag == 'dict':
        return {(node[i].text or ''): _value(node[i+1]) for i in range(0, len(node), 2)}
    if node.tag == 'array':
        return [_value(child) for child in node]
    return _scalar(node)


def _project(document):
    if not isinstance(document, dict):
        return document
    result = {k: v for k, v in document.items() if k in ROOT_KEYS}
    if isinstance(result.get('processor'), dict):
        result['processor'] = {k: v for k, v in result['processor'].items() if k in PROCESSOR_KEYS}
    if isinstance(result.get('gpu'), dict):
        result['gpu'] = {k: v for k, v in result['gpu'].items() if k in GPU_KEYS}
    return result


def _extract_frame(frame):
    spans = (native.Span * 396)()
    if native.SCAN is None or not native.SCAN(frame, len(frame), spans):
        return _project(plistlib.loads(frame))
    def scalar(slot):
        span = spans[slot]
        tag = frame[span.start+1]
        if tag == 105:  # integer
            return int(frame[span.start+9:span.end-10])
        if tag == 114:  # real
            return float(frame[span.start+6:span.end-7])
        if tag == 100 and frame[span.start:span.start+6] == b'<date>':
            return _date(frame[span.start+6:span.end-7].decode('ascii'))
        if tag == 115:  # string, with XML newline normalization
            return ('' if frame[span.start:span.end] == b'<string/>' else
                    frame[span.start+8:span.end-9].decode('ascii').replace('\r\n','\n').replace('\r','\n'))
        if tag in (116,102):
            return tag == 116
        # The scanner has checked all grammar, so only the selected tiny
        # values (normally the GPU state array) need object materialization.
        return _value(ET.fromstring(frame[span.start:span.end]))
    try:
        result = {key: scalar(i) for i, key in enumerate(
            ('elapsed_ns', 'timestamp', 'thermal_pressure'), 1) if spans[i].end}
        if spans[0].end:
            result['processor'] = {key: scalar(i) for i, key in enumerate(
                ('cpu_power', 'gpu_power', 'ane_power', 'cpu_energy', 'gpu_energy', 'ane_energy'), 4)
                if spans[i].end}
        if spans[10].end:
            # used_ratio has no role in this observation. Avoid materializing
            # it, and preserve Python's exact integer/float summation order.
            states = []
            for j in range(spans[11].start):
                base = 12+3*j
                state = {}
                for i,key in ((0,'freq'),(1,'used_ns')):
                    if spans[base+i].end:
                        value = scalar(base+i)
                        if isinstance(value,(bool,str,int,float)):
                            state[key] = value
                # A ratio-only entry still participates in the reference
                # missing-frequency diagnostic when other states are active.
                ratio = spans[base+2]
                if state or ratio.end and frame[ratio.start+1] in (105,114,115,116,102):
                    states.append(state)
            active = sum(s.get('used_ns',0) for s in states)
            clock = sum(s['freq']*s.get('used_ns',0) for s in states)/active if active else None
            result['_gpu_clock'] = (active,clock)
        return result
    except (ValueError, KeyError, TypeError, OverflowError):
        return _project(plistlib.loads(frame))


def _frames(handle, digest, size, chunk_bytes=CHUNK_BYTES):
    pending = bytearray()
    # Hash the very chunks being parsed, in order; at most one is outstanding.
    with ThreadPoolExecutor(max_workers=1) as hasher:
        previous = None
        while chunk := handle.read(chunk_bytes):
            if previous is not None:
                previous.result()
            previous = hasher.submit(digest.update, chunk)
            size[0] += len(chunk)
            search_start = len(pending)
            pending.extend(chunk)
            start = 0
            while (end := pending.find(0, search_start)) >= 0:
                part = bytes(pending[start:end])
                if part.strip():
                    yield part
                start = end + 1
                search_start = start
            if start:
                del pending[:start]
        if previous is not None:
            previous.result()
    if pending.strip():
        yield bytes(pending)


def _documents(handle, digest, size, *, reference=False):
    pending_error = None
    count = 0
    for index, frame in enumerate(_frames(handle, digest, size)):
        if pending_error is not None:
            raise ValueError(pending_error['error'])
        try:
            document = _project(plistlib.loads(frame)) if reference else _extract_frame(frame)
        except (expat.ExpatError, plistlib.InvalidFileException, ValueError, TypeError) as exc:
            message = f'powermetrics document {index} is not a valid plist: {exc}'
            if not count:
                raise ValueError(message) from exc
            pending_error = {'frame_index': index, 'byte_count': len(frame),
                             'sha256': hashlib.sha256(frame).hexdigest(), 'error': message}
            continue
        if not isinstance(document, dict):
            raise ValueError(f'powermetrics document {index} is not a dictionary')
        count += 1
        yield document
    if pending_error is not None:
        yield pending_error
    if not count:
        raise ValueError('powermetrics stream contains no complete plist documents')


def _required(mapping, key, index):
    try:
        return mapping[key]
    except KeyError as exc:
        raise ValueError(f'powermetrics document {index} is missing key {key!r}') from exc


def _required_int(mapping, key, index):
    value = _required(mapping, key, index)
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'powermetrics document {index} key {key!r} is not an integer: {value!r}') from exc


def _required_power(mapping, key, index):
    from joulewise.validation import finite_float
    value = _required(mapping, key, index)
    try:
        return finite_float(value, f'powermetrics document {index} key {key!r}') / 1000.0
    except ValueError as exc:
        raise ValueError(f'powermetrics document {index} key {key!r} is not a finite number: {value!r}') from exc


def _native_ns(value):
    if not isinstance(value, datetime):
        raise ValueError(f'powermetrics timestamp is not a datetime: {value!r}')
    value = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
    delta = value - datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (delta.days * 86400 + delta.seconds) * 1_000_000_000 + delta.microseconds * 1000


def _gpu_clock(document):
    # Same projection and summation order as decode_rich_telemetry followed by
    # thermal_desk.native_pm_samples. Do not weight by total elapsed time.
    if '_gpu_clock' in document:
        active, clock = document['_gpu_clock']
        if not math.isfinite(active) or clock is not None and not math.isfinite(clock):
            raise ValueError('nonfinite GPU clock observation cannot be reduced')
        return active, clock
    gpu = document.get('gpu')
    states = gpu.get('dvfm_states') if isinstance(gpu, dict) else None
    entries = [{k: s[k] for k in STATE_KEYS if k in s and isinstance(s[k], (bool, str, int, float))}
               for s in states if isinstance(s, dict)] if isinstance(states, list) else []
    entries = [s for s in entries if s]
    active = sum(s.get('used_ns', 0) for s in entries)
    clock = sum(s['freq'] * s.get('used_ns', 0) for s in entries) / active if active else None
    if not math.isfinite(active) or clock is not None and not math.isfinite(clock):
        raise ValueError('nonfinite GPU clock observation cannot be reduced')
    return active, clock


@dataclass
class SampleColumns:
    raw_sha256: str
    raw_size: int
    columns: dict[str, array]
    thermal_labels: tuple[str | None, ...]
    dropped_tail: dict | None = None

    def __len__(self):
        return len(self.columns['elapsed_ns'])

    def endpoint_seconds(self, first_record_endpoint_s):
        """Reproduce the adapter's ordered float-second accumulation (A21)."""
        from joulewise.validation import finite_float
        anchor = finite_float(first_record_endpoint_s, 'first_record_endpoint_s')
        cumulative_s = 0.0
        result = []
        for i, elapsed in enumerate(self.columns['elapsed_ns']):
            if i:
                cumulative_s += elapsed / 1_000_000_000.0
            result.append(anchor + cumulative_s)
        return result

    def monotonic_t_ns(self, first_record_endpoint_s, offset_ns):
        if type(offset_ns) is not int:
            raise ValueError('clock offset must be integer nanoseconds')
        return array('q', (seconds_ns(t) + offset_ns
                           for t in self.endpoint_seconds(first_record_endpoint_s)))

    def native_pm_samples(self, first_record_endpoint_s, offset_ns):
        starts, ends = self._mapped_supports_ns(first_record_endpoint_s, offset_ns)
        c = self.columns
        return [{'start_ns': starts[i], 'end_ns': end,
                 'state': self.thermal_labels[c['thermal_code'][i]],
                 'active_ns': int(c['active_ns'][i]) if c['active_integer'][i] else c['active_ns'][i],
                 'clock_mhz': c['clock_mhz'][i] if c['clock_valid'][i] else None}
                for i, end in enumerate(ends)]

    def mapped_columns(self, first_record_endpoint_s, offset_ns):
        """Fresh arrays on the supplied episode clock (normally monotonic).

        Supports use adapter float subtraction before exact ns conversion.
        A37 changes only interior starts, after conversion.
        """
        starts, ends = self._mapped_supports_ns(first_record_endpoint_s, offset_ns)
        return {**self.columns, 't_ns': ends, 'power_start_ns': starts,
                'thermal_start_ns': array('q', starts)}

    def _mapped_supports_ns(self, first_record_endpoint_s, offset_ns):
        if type(offset_ns) is not int:
            raise ValueError('clock offset must be integer nanoseconds')
        endpoints = self.endpoint_seconds(first_record_endpoint_s)
        ends = array('q', (seconds_ns(t) + offset_ns for t in endpoints))
        # Production samples_from_records subtracts in float seconds, before
        # conversion. Exact endpoints supplied by synthetic API overrides keep
        # their exact arithmetic; endpoint_seconds itself always emits floats.
        starts = array('q', (seconds_ns(t - elapsed / 1_000_000_000.0
                    if isinstance(t, float) else Fraction(t) - Fraction(elapsed, 1_000_000_000)) + offset_ns
                    for t, elapsed in zip(endpoints, self.columns['elapsed_ns'], strict=True)))
        _snap_interior_starts(starts, ends)
        return starts, ends

    def power_traces(self, first_record_endpoint_s, *, nominal_interval_ns, evidence=None):
        """Apply A37 in native record order, then project each rail's samples."""
        from joulewise.align.apple.sampler import power_records
        from joulewise.interfaces import PowerSample
        starts, ends = self._mapped_supports_ns(first_record_endpoint_s, 0)
        samples = []
        for i, end in enumerate(ends):
            # Feed the common projector exact seconds, never float epochs.
            samples.extend(PowerSample(timestamp_s=Fraction(end, 1_000_000_000), power_w=self.columns[rail][i],
                                       source='powermetrics', rail=rail,
                                       interval_start_s=Fraction(starts[i], 1_000_000_000),
                                       interval_end_s=Fraction(end, 1_000_000_000)) for rail in RAILS)
        traces, flags = power_records(samples, nominal_interval_ns=nominal_interval_ns, evidence=evidence)
        result, flags = [], list(flags)
        for trace in traces:
            notes = json.loads(trace.notes)
            supports = notes['sample_support_ns']
            # power_records sorts, filters nonfinite powers and keeps the
            # first record at a duplicated ns endpoint. Carry the supports of
            # those same records; never snap against a projected neighbour.
            retained = {}
            for i in sorted(range(len(ends)), key=ends.__getitem__):
                if math.isfinite(self.columns[trace.channel][i]):
                    retained.setdefault(ends[i], [starts[i], ends[i]])
            snapped_supports = [retained[t] for t in trace.t_ns]
            if snapped_supports != supports:
                flag = f'support_edge_snapped:{trace.channel}'
                flags.append(flag)
                notes['flags'].append(flag)
            notes['sample_support_ns'] = snapped_supports
            # Downstream readers must not re-snap projected neighbours with
            # an epoch-dependent tolerance or interpolate uncovered time.
            notes['support_policy'] = 'A37'
            widths = {b-a for a, b in snapped_supports}
            variable_flag = f'variable_averaging_support:{trace.channel}'
            flags = [f for f in flags if f != variable_flag]
            notes['flags'] = [f for f in notes['flags'] if f != variable_flag]
            if len(widths) > 1:
                flags.append(variable_flag)
                notes['flags'].append(variable_flag)
            trace = replace(trace, notes=json.dumps(notes, sort_keys=True),
                            averaging_window_ns=next(iter(widths)) if len(widths) == 1 else None)
            result.append(trace)
        return tuple(result), tuple(flags)


def _append_observation(document, i, columns, labels):
    elapsed = _required_int(document, 'elapsed_ns', i)
    processor = document.get('processor')
    if not isinstance(processor, dict):
        raise ValueError(f'powermetrics document {i} is missing processor dictionary')
    columns['elapsed_ns'].append(elapsed)
    columns['native_timestamp_ns'].append(_native_ns(_required(document, 'timestamp', i)))
    for rail in RAILS:
        columns[rail].append(_required_power(processor, rail, i))
    # These are required by the original record parser even though neither
    # the desk nor the energy allocation uses native integer energy counters.
    for energy in ('cpu_energy', 'gpu_energy', 'ane_energy'):
        _required_int(processor, energy, i)
    label = document.get('thermal_pressure')
    label = label if isinstance(label, str) else None
    if label not in labels:
        labels.append(label)
    columns['thermal_code'].append(labels.index(label))
    active, clock = _gpu_clock(document)
    if type(active) is int and int(float(active)) != active:
        raise ValueError('GPU active counter exceeds lossless float storage')
    columns['active_ns'].append(active)
    columns['active_integer'].append(type(active) is int)
    columns['clock_mhz'].append(clock if clock is not None else 0.0)
    columns['clock_valid'].append(clock is not None)


def reduce_stream(handle, *, reference=False):
    """Read a NUL-framed stream once. `reference` is a benchmark/equality oracle."""
    digest, size = hashlib.sha256(), [0]
    documents = _documents(handle, digest, size, reference=reference)
    diagnostic = semantic_error = None
    columns = {name: array(kind) for name, kind in LAYOUT}
    labels = []
    for i, document in enumerate(documents):
        if 'frame_index' in document and 'error' in document:
            diagnostic = document
            continue
        if semantic_error is not None:
            continue
        try:
            _append_observation(document, i, columns, labels)
        except (ValueError, KeyError, TypeError, OverflowError) as exc:
            # The reference parses every XML frame before validating fields.
            # Continue parsing without retaining trees, so a later framing/XML
            # failure has its original priority over an earlier field error.
            semantic_error = exc
    if semantic_error is not None:
        raise semantic_error
    return SampleColumns(digest.hexdigest(), size[0], columns, tuple(labels), diagnostic)


def _portable_code(code):
    # Source locations do not participate in parsing. Keep opcodes, constants,
    # names and line tables, but allow the same loaded build in another clone.
    return code.replace(co_filename='<loaded-reducer>', co_consts=tuple(
        _portable_code(value) if isinstance(value, CodeType) else value for value in code.co_consts))


def producer_sha256():
    """Fingerprint code *as loaded*, never just source files on disk."""
    from joulewise import validation
    digest = hashlib.sha256(_json([SCHEMA, LAYOUT, INTERIOR_SEAM_NS, sorted(ROOT_KEYS), sorted(PROCESSOR_KEYS),
                                  sorted(GPU_KEYS), sorted(STATE_KEYS), sys.version,
                                  ET.VERSION, expat.EXPAT_VERSION, native.LOADED_SHA256]))
    functions = {name: value for name, value in globals().items() if isinstance(value, FunctionType)}
    functions.update({'SampleColumns.' + name: value for name, value in vars(SampleColumns).items()
                      if isinstance(value, FunctionType)})
    functions['finite_float'] = validation.finite_float
    functions['ElementTree.fromstring'] = ET.fromstring
    functions['ElementTree.XML'] = ET.XML
    # plistlib is also loaded Python code: include its fallback implementation.
    for name, value in vars(plistlib).items():
        if isinstance(value, FunctionType):
            functions['plistlib.' + name] = value
        elif isinstance(value, type) and value.__module__ == 'plistlib':
            functions.update({'plistlib.' + name + '.' + n: v for n, v in vars(value).items()
                              if isinstance(v, FunctionType)})
    for name, function in sorted(functions.items()):
        digest.update(name.encode())
        digest.update(marshal.dumps(_portable_code(function.__code__)))
    return digest.hexdigest()


def encode_columns(samples):
    header = _json({'schema': SCHEMA, 'producer_sha256': producer_sha256(),
                    'raw_sha256': samples.raw_sha256, 'raw_size': samples.raw_size,
                    'count': len(samples), 'layout': LAYOUT,
                    'thermal_labels': samples.thermal_labels, 'dropped_tail': samples.dropped_tail})
    parts = [MAGIC, struct.pack('<Q', len(header)), header]
    for name, kind in LAYOUT:
        values = array(kind, samples.columns[name])
        if sys.byteorder != 'little':
            values.byteswap()
        parts.append(values.tobytes())
    body = b''.join(parts)
    return body + hashlib.sha256(body).digest()


def decode_columns(data, *, raw_sha256):
    if len(data) < len(MAGIC) + 8 + 32 or not data.startswith(MAGIC):
        raise ValueError('invalid reduced header')
    if hashlib.sha256(data[:-32]).digest() != data[-32:]:
        raise ValueError('reduced checksum mismatch')
    header_length = struct.unpack_from('<Q', data, len(MAGIC))[0]
    cursor = len(MAGIC) + 8 + header_length
    header = json.loads(data[len(MAGIC)+8:cursor])
    if (header['schema'] != SCHEMA or header['producer_sha256'] != producer_sha256()
            or header['raw_sha256'] != raw_sha256 or header['layout'] != [list(v) for v in LAYOUT]):
        raise ValueError('reduced identity mismatch')
    count = header['count']
    if type(count) is not int or count < 1:
        raise ValueError('invalid reduced count')
    columns = {}
    for name, kind in LAYOUT:
        values = array(kind)
        end = cursor + count * values.itemsize
        if end > len(data) - 32:
            raise ValueError('truncated reduced columns')
        values.frombytes(data[cursor:end])
        if sys.byteorder != 'little':
            values.byteswap()
        columns[name] = values
        cursor = end
    labels = tuple(header['thermal_labels'])
    if cursor != len(data) - 32 or any(code >= len(labels) for code in columns['thermal_code']):
        raise ValueError('invalid reduced extent or thermal codes')
    return SampleColumns(raw_sha256, header['raw_size'], columns, labels, header['dropped_tail'])


def _sha_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        while chunk := handle.read(CHUNK_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def cache_path(cache_dir, raw_sha256):
    return Path(cache_dir) / producer_sha256() / (raw_sha256 + '.jwsr')


def reduce_file(raw_path, *, cache_dir=None):
    """Content-addressed derived data only. Refusals are never written.

    A hit always rehashes raw bytes. An advisory source index selects whether
    to try a hit; it grants no trust. A cold miss hashes while parsing once.
    Metadata changes select the cold path. A concealed concurrent mutation
    refuses, instead of reading different bytes a second time.
    """
    from joulewise.align.v4_analysis.io import input_path
    raw_path = input_path(raw_path)
    cache_dir = input_path(cache_dir) if cache_dir is not None else None
    def signature():
        s = raw_path.stat()
        return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns]
    before = signature()
    index = (Path(cache_dir)/producer_sha256()/'sources'/
             (hashlib.sha256(os.fsencode(raw_path.absolute())).hexdigest()+'.json')) if cache_dir is not None else None
    hint = None
    if index is not None:
        try:
            hint = json.loads(index.read_bytes())
            cached_bytes = cache_path(cache_dir, hint['raw_sha256']).read_bytes() if hint['stat'] == before else None
            cached = decode_columns(cached_bytes, raw_sha256=hint['raw_sha256']) if cached_bytes else None
        except (FileNotFoundError, ValueError, KeyError, TypeError, OverflowError):
            cached = None
        if cached is not None:
            actual = _sha_file(raw_path)
            if actual != hint['raw_sha256'] or signature() != before:
                raise ValueError('raw changed during cache verification; retry cold')
            return cached
    with raw_path.open('rb') as handle:
        samples = reduce_stream(handle)
    if signature() != before:
        raise ValueError('raw changed during reduction')
    if cache_dir is not None:
        path = cache_path(cache_dir, samples.raw_sha256)
        payload = encode_columns(samples)
        path.parent.mkdir(parents=True, exist_ok=True)
        name = None
        try:
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.reduce-', delete=False) as handle:
                name = handle.name
                handle.write(payload)
            os.replace(name, path)
        finally:
            if name is not None and os.path.exists(name):
                os.unlink(name)
        index.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=index.parent, delete=False) as handle:
            index_tmp = handle.name
            handle.write(_json({'stat': before, 'raw_sha256': samples.raw_sha256}))
        os.replace(index_tmp, index)
    return samples


def _member_job(args):
    path, cache_dir = args
    return reduce_file(path, cache_dir=cache_dir)


def worker_count(requested=0, *, peak_worker_bytes=512*1024**2):
    """R17 free-core/free-memory ceiling; unknown memory means one worker.

    Explicit values remain bounded at eight. Auto is 0; it never inspects or
    changes another job. Peak is a conservative software-stage budget.
    """
    if type(requested) is not int or not 0 <= requested <= 8:
        raise ValueError('workers must be an integer in [0, 8]')
    if requested:
        return requested
    cores = max(1, (os.cpu_count() or 1)-math.ceil(os.getloadavg()[0]))
    try:
        available = os.sysconf('SC_AVPHYS_PAGES')*os.sysconf('SC_PAGE_SIZE')
    except (OSError, ValueError):
        available = peak_worker_bytes
    return max(1, min(8, cores, available//peak_worker_bytes))


def reduce_members(raw_paths, *, cache_dir=None, workers=1):
    """Parallelize independent members only; preserve input order and bytes."""
    workers = worker_count(workers)
    jobs = [(str(path), str(cache_dir) if cache_dir is not None else None) for path in raw_paths]
    if workers == 1:
        return [_member_job(job) for job in jobs]
    with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        return list(pool.map(_member_job, jobs, chunksize=1))


def turn_energy_table(samples, episode, *, first_record_endpoint_s, nominal_interval_ns, evidence=None):
    """Fresh existing-attribution results for recorded turns, tools, holds and gaps.

    Do not cache this return value: it depends on the supplied episode, clock
    mapping and uncertainty evidence. No fitting or eligibility occurs here.
    """
    from joulewise.align.attribution import attribute_episode, owned_energy_flags
    traces, flags = samples.power_traces(first_record_endpoint_s,
                                         nominal_interval_ns=nominal_interval_ns, evidence=evidence)
    joined = replace(episode, power_traces=traces,
                     flags=tuple(dict.fromkeys((*episode.flags, *flags))))
    result = {}
    for rail in RAILS:
        attributed = attribute_episode(joined, source='powermetrics', channel=rail)
        record = asdict(attributed)
        # Gross and unowned coverage remains disclosed in total/segments;
        # the table's screening flags describe coverage of owned work only.
        record['flags'] = owned_energy_flags(attributed)
        result[rail] = {'attribution': record, 'turns': [
            {'turn': turn.index,
             'owned_j': sum(s.energy.joules for s in attributed.segments if s.turn == turn.index),
             'owned_half_width_j': sum(s.energy.half_width_j for s in attributed.segments if s.turn == turn.index)}
            for turn in episode.turns]}
    return result
