"""SOL offline raw-PM reduction, independent of the registered instrument.

The cache contains observations only. Anchoring, turn ownership, uncertainty,
eligibility and all statistical decisions are evaluated afresh by the caller.
No model, config, measurement root or network resource is discovered here.
"""
from __future__ import annotations

from array import array
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
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
from types import CodeType, FunctionType
from xml.etree import ElementTree as ET
from xml.parsers import expat

SCHEMA = 'joulewise.powermetrics.reduce-sol.v1'
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


def _validate_tree(root):
    """Validate ignored values as well: bad unused fields must not slip through.

    This common grammar is deliberately conservative. Anything unusual is sent
    to plistlib, which owns acceptance and diagnostics (including binary plists).
    C ElementTree constructs the XML tree; there are no Python XML callbacks.
    """
    if root.tag != 'plist' or len(root) != 1 or root[0].tag != 'dict':
        raise ValueError('unusual plist root')
    for node in root.iter():
        if node.tag == 'plist':
            if node is not root:
                raise ValueError('nested plist')
        elif node.tag == 'dict':
            if len(node) % 2 or any(node[i].tag != 'key' or node[i+1].tag == 'key'
                                    for i in range(0, len(node), 2)):
                raise ValueError('unusual dictionary')
        elif node.tag == 'array':
            if any(child.tag == 'key' for child in node):
                raise ValueError('key in array')
        else:
            if len(node):
                raise ValueError('nested scalar')
            _scalar(node)


def _selected_dict(node, keys):
    if node.tag != 'dict':
        return _value(node)
    # Duplicate keys retain the last value, exactly as plistlib does.
    return {(node[i].text or ''): _value(node[i+1]) for i in range(0, len(node), 2)
            if (node[i].text or '') in keys}


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
    # ElementTree may expand internal entities which plistlib explicitly forbids.
    # Preserve that rejection by routing declarations to the reference parser.
    if b'<!ENTITY' in frame:
        return _project(plistlib.loads(frame))
    try:
        root = ET.fromstring(frame)
        _validate_tree(root)
        result = {}
        for i in range(0, len(root[0]), 2):
            key, value = root[0][i].text or '', root[0][i+1]
            if key == 'processor':
                result[key] = _selected_dict(value, PROCESSOR_KEYS)
            elif key == 'gpu':
                # Keep only the small GPU state array; never materialize cores.
                result[key] = _selected_dict(value, GPU_KEYS)
            elif key in ROOT_KEYS:
                result[key] = _value(value)
        return result
    except (ET.ParseError, ValueError, TypeError, OverflowError):
        # This also preserves the full parser's exact malformed-XML diagnostic.
        return _project(plistlib.loads(frame))


def _frames(handle, digest, size, chunk_bytes=CHUNK_BYTES):
    pending = bytearray()
    while chunk := handle.read(chunk_bytes):
        digest.update(chunk)
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
    if pending.strip():
        yield bytes(pending)


def _documents(handle, digest, size, *, reference=False):
    documents, diagnostic, pending_error = [], None, None
    for index, frame in enumerate(_frames(handle, digest, size)):
        if pending_error is not None:
            raise ValueError(pending_error['error'])
        try:
            document = _project(plistlib.loads(frame)) if reference else _extract_frame(frame)
        except (expat.ExpatError, plistlib.InvalidFileException, ValueError, TypeError) as exc:
            message = f'powermetrics document {index} is not a valid plist: {exc}'
            if not documents:
                raise ValueError(message) from exc
            pending_error = {'frame_index': index, 'byte_count': len(frame),
                             'sha256': hashlib.sha256(frame).hexdigest(), 'error': message}
            continue
        if not isinstance(document, dict):
            raise ValueError(f'powermetrics document {index} is not a dictionary')
        documents.append(document)
    if pending_error is not None:
        diagnostic = pending_error
    if not documents:
        raise ValueError('powermetrics stream contains no complete plist documents')
    return documents, diagnostic


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
        """Use the adapter's float additions in its original order, before ns conversion."""
        from joulewise.validation import finite_float
        anchor = finite_float(first_record_endpoint_s, 'first_record_endpoint_s')
        cumulative = 0.0
        result = array('d')
        for i, elapsed in enumerate(self.columns['elapsed_ns']):
            if i:
                cumulative += elapsed / 1_000_000_000.0
            result.append(anchor + cumulative)
        return result

    def monotonic_t_ns(self, first_record_endpoint_s, offset_ns):
        if type(offset_ns) is not int:
            raise ValueError('clock offset must be integer nanoseconds')
        return array('q', (round(t * 1_000_000_000) + offset_ns
                           for t in self.endpoint_seconds(first_record_endpoint_s)))

    def native_pm_samples(self, first_record_endpoint_s, offset_ns):
        ends = self.monotonic_t_ns(first_record_endpoint_s, offset_ns)
        c = self.columns
        return [{'start_ns': end - c['elapsed_ns'][i], 'end_ns': end,
                 'state': self.thermal_labels[c['thermal_code'][i]],
                 'active_ns': int(c['active_ns'][i]) if c['active_integer'][i] else c['active_ns'][i],
                 'clock_mhz': c['clock_mhz'][i] if c['clock_valid'][i] else None}
                for i, end in enumerate(ends)]

    def mapped_columns(self, first_record_endpoint_s, offset_ns):
        """Fresh arrays on the supplied episode clock (normally monotonic).

        Power supports follow the adapter's float conversion; native thermal
        supports subtract integer elapsed_ns. These two existing conventions
        differ by sub-microsecond rounding and must not be conflated.
        """
        ends = self.monotonic_t_ns(first_record_endpoint_s, offset_ns)
        elapsed = self.columns['elapsed_ns']
        starts = array('q', (round((t - elapsed[i] / 1_000_000_000.0) * 1_000_000_000) + offset_ns
                             for i, t in enumerate(self.endpoint_seconds(first_record_endpoint_s))))
        return {**self.columns, 't_ns': ends, 'power_start_ns': starts,
                'thermal_start_ns': array('q', (end-elapsed[i] for i, end in enumerate(ends)))}

    def power_traces(self, first_record_endpoint_s, *, nominal_interval_ns, evidence=None):
        """Re-use the established support conversion and flags, including edge snapping."""
        from joulewise.align.apple.sampler import power_records
        from joulewise.interfaces import PowerSample
        samples = []
        for i, end in enumerate(self.endpoint_seconds(first_record_endpoint_s)):
            start = end - self.columns['elapsed_ns'][i] / 1_000_000_000.0
            samples.extend(PowerSample(timestamp_s=end, power_w=self.columns[rail][i],
                                       source='powermetrics', rail=rail,
                                       interval_start_s=start, interval_end_s=end) for rail in RAILS)
        return power_records(samples, nominal_interval_ns=nominal_interval_ns, evidence=evidence)


def reduce_stream(handle, *, reference=False):
    """Read a NUL-framed stream once. `reference` is a benchmark/equality oracle."""
    digest, size = hashlib.sha256(), [0]
    documents, diagnostic = _documents(handle, digest, size, reference=reference)
    columns = {name: array(kind) for name, kind in LAYOUT}
    labels = []
    for i, document in enumerate(documents):
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
    return SampleColumns(digest.hexdigest(), size[0], columns, tuple(labels), diagnostic)


def _portable_code(code):
    # Source locations do not participate in parsing. Keep opcodes, constants,
    # names and line tables, but allow the same loaded build in another clone.
    return code.replace(co_filename='<loaded-reducer>', co_consts=tuple(
        _portable_code(value) if isinstance(value, CodeType) else value for value in code.co_consts))


def producer_sha256():
    """Fingerprint code *as loaded*, never just source files on disk."""
    from joulewise import validation
    digest = hashlib.sha256(_json([SCHEMA, LAYOUT, sorted(ROOT_KEYS), sorted(PROCESSOR_KEYS),
                                  sorted(GPU_KEYS), sorted(STATE_KEYS), sys.version,
                                  ET.VERSION, expat.EXPAT_VERSION]))
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

    A hit always rehashes raw bytes. A miss rehashes the stream actually parsed
    as well, refusing a concurrent raw change rather than misbinding evidence.
    """
    raw_path = Path(raw_path)
    expected = _sha_file(raw_path) if cache_dir is not None else None
    path = cache_path(cache_dir, expected) if cache_dir is not None else None
    if path is not None:
        try:
            cached = decode_columns(path.read_bytes(), raw_sha256=expected)
            return cached
        except (FileNotFoundError, ValueError, KeyError, TypeError, OverflowError):
            pass
    with raw_path.open('rb') as handle:
        samples = reduce_stream(handle)
    if expected is not None and samples.raw_sha256 != expected:
        raise ValueError('raw changed during reduction')
    if path is not None:
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
    return samples


def _member_job(args):
    path, cache_dir = args
    return reduce_file(path, cache_dir=cache_dir)


def reduce_members(raw_paths, *, cache_dir=None, workers=1):
    """Parallelize independent members only; preserve input order and bytes."""
    if type(workers) is not int or not 1 <= workers <= 8:
        raise ValueError('workers must be an integer in [1, 8]')
    jobs = [(str(path), str(cache_dir) if cache_dir is not None else None) for path in raw_paths]
    if workers == 1:
        return [_member_job(job) for job in jobs]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_member_job, jobs, chunksize=1))


def turn_energy_table(samples, episode, *, first_record_endpoint_s, nominal_interval_ns, evidence=None):
    """Fresh existing-attribution results for recorded turns, tools, holds and gaps.

    Do not cache this return value: it depends on the supplied episode, clock
    mapping and uncertainty evidence. No fitting or eligibility occurs here.
    """
    from joulewise.align.attribution import attribute_episode
    traces, flags = samples.power_traces(first_record_endpoint_s,
                                         nominal_interval_ns=nominal_interval_ns, evidence=evidence)
    joined = replace(episode, power_traces=traces,
                     flags=tuple(dict.fromkeys((*episode.flags, *flags))))
    result = {}
    for rail in RAILS:
        attributed = attribute_episode(joined, source='powermetrics', channel=rail)
        result[rail] = {'attribution': asdict(attributed), 'turns': [
            {'turn': turn.index,
             'owned_j': sum(s.energy.joules for s in attributed.segments if s.turn == turn.index),
             'owned_half_width_j': sum(s.energy.half_width_j for s in attributed.segments if s.turn == turn.index)}
            for turn in episode.turns]}
    return result
