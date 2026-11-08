"""Reduce-once of a raw powermetrics plist stream (HARVEST-OFF-opus §9, Ed 2026-11-08).

Raw ``raw/powermetrics*.plist`` stays the custody evidence and is never changed.
The harvest (on the Air) reduces each member's stream ONCE into a compact,
digest-bound columnar file; analysis then reads only reduced artifacts.

Targeted extractor. About 87% of every powermetrics document is the per-CPU
``processor.clusters`` subtree, which no energy/thermal consumer reads. The fast
path cuts exactly that subtree out of the document bytes and hands the rest to
``plistlib`` itself, so every retained value is produced by the same parser with
the same semantics (dates, reals, integers, booleans, strings). A document is
cut only when ``<key>clusters</key>`` occurs once and is followed by a balanced
``<array>`` subtree; otherwise it is parsed whole. ``verify_every`` re-parses a
deterministic sample of documents fully with ``plistlib`` and refuses on any
difference (first, last and every Nth), so equality is checked on real bytes at
run time too, not only in tests.

The columnar file is a NumPy ``.npy`` (version 1.0) structured array written
with the standard library only; its header binds the raw file's SHA-256 and size
and the extractor version. Values are native (no clock mapping or attribution):
time mapping and per-turn integration use the registered episode code (§9.3).
"""
from __future__ import annotations

import hashlib
import json
import plistlib
import re
import struct
from typing import Any

EXTRACTOR_VERSION = 'pm_reduce.v1'
_CLUSTERS_KEY = b'<key>clusters</key>'
_ARRAY_TAG = re.compile(rb'<array>|</array>|<array/>')
_LEADING_ARRAY = re.compile(rb'\s*<array(/?)>')
THERMAL_CODES = {None: 0, 'Nominal': 1, 'Fair': 2, 'Serious': 3, 'Critical': 4, 'Moderate': 5, 'Heavy': 6,
                 'Trapping': 7, 'Sleeping': 8}
COLUMNS = (('elapsed_ns', '<i8'), ('plist_timestamp_s', '<f8'), ('cpu_w', '<f8'), ('gpu_w', '<f8'),
           ('ane_w', '<f8'), ('cpu_mj', '<i8'), ('gpu_mj', '<i8'), ('ane_mj', '<i8'), ('thermal', '<i8'),
           ('gpu_active_mhz', '<f8'))
_STRUCT = struct.Struct('<' + ''.join('q' if dtype.endswith('i8') else 'd' for _, dtype in COLUMNS))


class ReduceRefused(ValueError):
    """The fast extractor disagreed with plistlib, or a required field is absent."""


def strip_clusters(part: bytes) -> bytes | None:
    """``part`` without its single ``processor.clusters`` key and array, or None (parse whole)."""
    start = part.find(_CLUSTERS_KEY)
    if start < 0 or part.find(_CLUSTERS_KEY, start + 1) >= 0:
        return None
    opening = _LEADING_ARRAY.match(part, start + len(_CLUSTERS_KEY))
    if opening is None:
        return None
    if opening.group(1) == b'/':
        return part[:start] + part[opening.end():]
    depth = 1
    for tag in _ARRAY_TAG.finditer(part, opening.end()):
        token = tag.group(0)
        if token == b'<array>':
            depth += 1
        elif token == b'</array>':
            depth -= 1
            if depth == 0:
                return part[:start] + part[tag.end():]
    return None


def _without_clusters(document: Any) -> Any:
    if isinstance(document, dict) and isinstance(document.get('processor'), dict):
        document = dict(document)
        document['processor'] = {k: v for k, v in document['processor'].items() if k != 'clusters'}
    return document


def fast_documents(data: bytes, *, verify_every: int = 64) -> list[dict[str, Any]]:
    """Every NUL-framed document, as plistlib would give it minus ``processor.clusters``.

    Raises (never drops) on an unparseable frame: reduction is for complete
    captures; the harvest's own assessment still records dropped-frame cases.
    """
    parts = [part for part in data.split(b'\0') if part.strip()]
    documents = []
    for index, part in enumerate(parts):
        stripped = strip_clusters(part)
        document = plistlib.loads(stripped if stripped is not None else part)
        if stripped is None:
            document = _without_clusters(document)
        if verify_every and (index == 0 or index == len(parts) - 1 or index % verify_every == 0):
            if _without_clusters(plistlib.loads(part)) != document:
                raise ReduceRefused(f'fast extractor differs from plistlib at document {index}')
        if not isinstance(document, dict):
            raise ReduceRefused(f'document {index} is not a dictionary')
        documents.append(document)
    return documents


def _weighted_gpu_mhz(gpu: Any) -> float:
    states = gpu.get('dvfm_states') if isinstance(gpu, dict) else None
    if not isinstance(states, list):
        return float('nan')
    active = sum(s.get('used_ns', 0) for s in states if isinstance(s, dict))
    if not active:
        return float('nan')
    return sum(s['freq'] * s.get('used_ns', 0) for s in states if isinstance(s, dict)) / active


def sample_rows(documents: list[dict[str, Any]]) -> list[tuple]:
    from datetime import timezone
    rows = []
    for index, d in enumerate(documents):
        try:
            p = d['processor']
            stamp = d['timestamp'].replace(tzinfo=timezone.utc).timestamp()
            rows.append((int(d['elapsed_ns']), float(stamp), float(p['cpu_power']) / 1000.0,
                         float(p['gpu_power']) / 1000.0, float(p['ane_power']) / 1000.0,
                         int(p['cpu_energy']), int(p['gpu_energy']), int(p['ane_energy']),
                         THERMAL_CODES.get(d.get('thermal_pressure'), -1), _weighted_gpu_mhz(d.get('gpu'))))
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise ReduceRefused(f'document {index} lacks a required field: {type(exc).__name__}: {exc}') from exc
    return rows


def to_npy(rows: list[tuple], *, raw_sha256: str, raw_size: int) -> bytes:
    """Structured ``.npy`` v1.0 bytes; the header dict also carries the raw binding."""
    descr = repr([(name, dtype) for name, dtype in COLUMNS])
    binding = json.dumps({'raw_sha256': raw_sha256, 'raw_size': raw_size, 'extractor': EXTRACTOR_VERSION,
                          'thermal_codes': {k or '': v for k, v in THERMAL_CODES.items()}}, sort_keys=True)
    header = ("{'descr': %s, 'fortran_order': False, 'shape': (%d,), 'jw_binding': %r, }"
              % (descr, len(rows), binding))
    pad = 64 - (10 + len(header) + 1) % 64
    header = (header + ' ' * pad + '\n').encode('latin1')
    body = b''.join(_STRUCT.pack(*row) for row in rows)
    return b'\x93NUMPY\x01\x00' + struct.pack('<H', len(header)) + header + body


def read_npy(raw: bytes) -> tuple[dict[str, Any], list[tuple]]:
    """Stdlib reader for :func:`to_npy` output: (binding, rows)."""
    import ast
    if raw[:8] != b'\x93NUMPY\x01\x00':
        raise ReduceRefused('not a reduced powermetrics file')
    length = struct.unpack('<H', raw[8:10])[0]
    header = ast.literal_eval(raw[10:10 + length].decode('latin1'))
    body = raw[10 + length:]
    rows = [_STRUCT.unpack_from(body, offset) for offset in range(0, len(body), _STRUCT.size)]
    if len(rows) != header['shape'][0]:
        raise ReduceRefused('row count differs from header')
    return json.loads(header['jw_binding']), rows


def reduce_plist(data: bytes, *, verify_every: int = 64) -> bytes:
    """Raw plist bytes -> digest-bound columnar bytes."""
    return to_npy(sample_rows(fast_documents(data, verify_every=verify_every)),
                  raw_sha256=hashlib.sha256(data).hexdigest(), raw_size=len(data))


def reduce_member(task: dict[str, str]) -> dict[str, Any]:
    """Reduce every ``raw/powermetrics*.plist`` of one bundle into ``out_dir/<run_id>/``.

    Reads through ``desk_compress.read_bytes`` (plain or compressed runs) and
    writes exclusively; returns the per-file binding rows in name order.
    """
    from pathlib import Path
    from joulewise.desk_compress import read_bytes
    bundle, out = Path(task['bundle_path']), Path(task['out_dir']) / task['run_id']
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    for raw_path in sorted((bundle / 'raw').glob('powermetrics*.plist*')):
        name = raw_path.name.removesuffix('.zst')
        data = read_bytes(bundle / 'raw' / name)
        reduced = reduce_plist(data, verify_every=int(task.get('verify_every', 64)))
        target = out / (name + '.npy')
        with target.open('xb') as sink:
            sink.write(reduced)
        rows.append({'raw': f"{task['run_id']}/raw/{name}", 'raw_sha256': hashlib.sha256(data).hexdigest(),
                     'raw_size': len(data), 'reduced': f"{task['run_id']}/{target.name}",
                     'reduced_sha256': hashlib.sha256(reduced).hexdigest(), 'reduced_size': len(reduced)})
    return {'run_id': task['run_id'], 'files': rows}


def reduce_members(tasks: list[dict[str, str]], *, workers: int = 1) -> list[dict[str, Any]]:
    """Order-preserving pool across members (one member per task)."""
    if workers <= 1 or len(tasks) <= 1:
        return [reduce_member(task) for task in tasks]
    import concurrent.futures
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(reduce_member, tasks))
