"""Print harvested KM003C evidence beside ALIGN rails without changing a fit.

The harvest owns clock mapping, integration and custody. This is a read-only
join of its controller-request integral, which includes gates, holds, tools
and gaps inside that request. It is not turn attribution or a DC detector.
Missing battery evidence must not turn the legacy meter-only fallback into
a whole-machine number. No qualification, threshold or exclusion is added.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from joulewise.desk_compress import read_bytes

SCHEMA = 'joulewise.b5_meter_cross_check.v1'
BOUNDARY = ('whole controller request (sampling_started to sampling_stopped), '
            'KM003C DC input at USB-C brick to MagSafe cable; adapter AC loss excluded')


def read_meter_record(path):
    """Read one explicit harvested record; retain its exact digest or a reason."""
    result = {'path': str(path), 'sha256': None, 'record': None, 'reason': None}
    try:
        raw = read_bytes(Path(path))
        result['sha256'] = hashlib.sha256(raw).hexdigest()
        value = json.loads(raw)
        if not isinstance(value, dict) or value.get('schema') != SCHEMA or not isinstance(value.get('members'), dict):
            raise ValueError('unsupported meter record schema or members')
        result['record'] = value
    except (OSError, ValueError) as exc:
        result['reason'] = f'{type(exc).__name__}: {exc}'
    return result


def _mapping(value):
    return value if isinstance(value, dict) else {}


def _number(value):
    try:
        return value if type(value) in (int, float) and math.isfinite(value) else None
    except OverflowError:
        return None


def member_meter(record, member_id, *, flags=None):
    """Keep raw-meter, signed battery and rail quantities distinct and labelled.

    ``diagnostic`` means numeric evidence was recorded, never native validation
    or small-effect qualification. Inspect flags and the raw capture separately.
    The request span differs from both the GPU episode and turn-owned energy.
    """
    row = _mapping(_mapping(_mapping(record).get('members')).get(member_id))
    machine = _mapping(row.get('machine'))
    meter = _mapping(machine.get('meter'))
    battery = _mapping(machine.get('battery'))
    gross = _number(meter.get('energy_J'))
    battery_gross = _number(battery.get('energy_J'))
    battery_available = machine.get('battery_term_available') is True
    reasons = []
    if record is None:
        reasons.append('meter_record_unavailable')
    elif not row:
        reasons.append('meter_member_unavailable')
    if gross is None:
        reasons.append('meter_integral_unavailable')
    if not battery_available or battery_gross is None:
        reasons.append('battery_term_unavailable')
    complete = gross is not None and battery_available and battery_gross is not None
    return {'status': 'diagnostic' if gross is not None else 'unavailable',
            'non_claim': True, 'boundary': BOUNDARY,
            'method': 'harvested mean sample power times whole request duration',
            'stream': row.get('stream'), 'offset_source': row.get('offset_source'),
            'window_raw_ns': machine.get('window_ns'), 'baseline_raw_ns': machine.get('baseline_ns'),
            'duration_s': _number(machine.get('duration_s')),
            'meter_gross_j': gross, 'meter_delta_j': _number(meter.get('delta_J')),
            'battery_gross_j': battery_gross if battery_available else None,
            'machine_gross_j': _number(gross + battery_gross) if complete else None,
            'machine_delta_j': _number(machine.get('delta_J')) if complete else None,
            'rail_delta_j': _number(row.get('rail_delta_J')),
            'rho': _number(row.get('rho')) if complete else None,
            'flags_status': 'not_supplied' if flags is None else 'supplied',
            'flags': sorted({f['code'] for f in flags or () if isinstance(f, dict)
                             and isinstance(f.get('code'), str) and f['code'].startswith('meter.')}),
            'reasons': reasons}
