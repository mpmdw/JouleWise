"""Per-turn energy table, reduced once per member (R17 / Ed's reduce-once directive).

Not a new integral: the table is the REGISTERED per-member code run once on the Air,
``scripts.align_pilot_session.episode_summary`` (per-channel turn energies from the
attribution) and ``thermal_desk.read_bundle_record`` + ``align_v4_thermal_desk.enrich_record``
(turn-owned energy, per-turn decode clock), exactly as the full desk calls them. Every
input file is digest-bound. :func:`from_pilot` extracts the same table from the full
desk's PILOT.json; the two must be equal (tests/align/test_harvest_off.py), which is the
gate before any analysis reads tables instead of bundles.

Energy is outcome-bearing: the table lives under the same restriction as withheld/.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = 'joulewise.align_v4.turn_table.v1'
INPUT_FILES = ('config.json', 'outputs/align_episode.json', 'outputs/align_turns.jsonl',
               'outputs/align_thermal.jsonl', 'power_trace.csv', 'rich_telemetry.jsonl',
               'raw/powermetrics.plist')
THERMAL_KEYS = ('turn_owned_j', 'turn_owned_half_width_j', 'gross_episode_j', 'gross_episode_half_width_j',
                'turn_owned_basis', 'per_turn')


def _canonical(value: Any) -> Any:
    from joulewise.align.apple.pilot_analysis import finite_json
    # The desk writes PILOT.json through finite_json and JSON; compare in that same form.
    return json.loads(json.dumps(finite_json(value), sort_keys=True, allow_nan=False))


def _table(run_id: str, summary: dict | None, thermal: dict | None) -> dict[str, Any]:
    channels = {}
    for name, energy in sorted(((summary or {}).get('energy') or {}).items()):
        channels[name] = {k: energy.get(k) for k in ('joules', 'half_width_j', 'segment_sum_j',
                                                     'per_turn_j', 'per_turn_segments')}
    return _canonical({'run_id': run_id, 'channels': channels,
                       'thermal': {k: (thermal or {}).get(k) for k in THERMAL_KEYS}})


def member_table(bundle: Path | str, run_id: str) -> dict[str, Any]:
    """Compute one member's table from its bundle with the desk's own functions."""
    from joulewise.desk_compress import read_bytes
    from joulewise.align.apple.thermal_desk import read_bundle_record
    from scripts.align_pilot_session import episode_summary
    from scripts.align_v4_thermal_desk import enrich_record
    bundle = Path(bundle)
    inputs = {}
    for name in INPUT_FILES:
        try:
            inputs[name] = hashlib.sha256(read_bytes(bundle / name)).hexdigest()
        except FileNotFoundError:
            inputs[name] = None
    try:
        summary = episode_summary(bundle)
    except Exception:  # the desk records an unreadable member with summary None
        summary = None
    try:
        thermal = enrich_record(read_bundle_record(bundle), bundle)
    except (OSError, ValueError):
        thermal = None
    return {'schema': SCHEMA, 'inputs': inputs, **_table(run_id, summary, thermal)}


def from_pilot(pilot: dict[str, Any], run_id: str) -> dict[str, Any]:
    """The same table, read from the full desk's PILOT.json."""
    member = next(m for m in pilot['members'] if m['run_id'] == run_id)
    thermal_rows = ((pilot.get('extra_checks') or {}).get('thermal') or {}).get('members') or []
    thermal = next((r for r in thermal_rows if r.get('id') == run_id and 'error' not in r), None)
    return _table(run_id, member.get('summary'), thermal)


def equal_to_pilot(table: dict[str, Any], pilot: dict[str, Any]) -> bool:
    return {k: v for k, v in table.items() if k not in ('schema', 'inputs')} == from_pilot(pilot, table['run_id'])
