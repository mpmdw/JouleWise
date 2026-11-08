"""W1/D-only secondary DC diagnostic over the Block-series meter custody.

The Block driver owns USB capture, restart/stop supervision and stream hashes.
This module reads that evidence through the existing parser. It never changes
rail eligibility, exclusions, thresholds or a finalized capture artifact.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path

from joulewise.align import energy_residual as er
from joulewise.align.records import Episode, from_json
from joulewise.desk_compress import read_bytes
from joulewise.external import km003c_parse as kp

LABEL = 'SECONDARY / not yet registered'
REQUIREMENT = {
    'enabled': True,
    'reader': 'scripts/km003c_monitor.py',
    'supervisor': 'joulewise.b5.driver',
    'custody_directory': 'hazards/meter',
    'scope': 'before_first_idle_baseline_through_last_member',
    'label': LABEL,
}


def require_enabled(plan):
    requirements = plan.get('runtime_requirements') if isinstance(plan, dict) else None
    configured = requirements.get('km003c') if isinstance(requirements, dict) else None
    if not isinstance(configured, dict) or any(
            type(configured.get(k)) is not type(v) or configured.get(k) != v
            for k, v in REQUIREMENT.items()):
        raise ValueError('RUN_STATE 210 / squeeze ruling: W1/D requires the enabled KM003C '
                         'reader under the Block night supervisor, with hashed night custody; '
                         'regenerate the v4 collection plan')


def _empty(flags=()):
    return {'label': LABEL, 'print_only': True, 'status': 'missing',
            'powermetrics_admissibility_unchanged': True, 'flags': list(flags),
            'stream': None, 'dc_in_energy_j': None, 'episode_dc_in_energy_j': None,
            'baseline_w': None, 'dc_in_delta_j': None, 'predicted_j': None,
            'dc_in_residual_j': None, 'score': None, 'turn_rows': [],
            'residual_status': 'missing_dc'}


def unavailable_report(plan_members, flag, *, detail=None):
    return {'schema': 'joulewise.align_v4.km003c_secondary.v1', 'label': LABEL, 'print_only': True,
            'members': {m['run_id']: _empty([flag]) for m in plan_members}, 'detail': detail}


def _span(value):
    return (isinstance(value, (tuple, list)) and len(value) == 2
            and all(type(v) is int for v in value) and 0 <= value[0] < value[1])


def _union(intervals):
    merged = []
    for start, end in sorted(intervals):
        if end <= start:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(end, merged[-1][1])
        else:
            merged.append([start, end])
    return merged


def _predict(row, model):
    if row['status'] != 'available':
        return
    rows = [er.TurnRow(**r) for r in row['turn_rows']]
    prediction = er.predict_episode(model, rows)
    row['flags'] = list(dict.fromkeys([*row['flags'], *prediction.flags]))
    if math.isfinite(prediction[0]):
        row.update(predicted_j=prediction[0],
                   dc_in_residual_j=row['dc_in_delta_j'] - prediction[0],
                   residual_status='diagnostic_only')
    else:
        row['residual_status'] = 'dc_fit_unavailable'


def capture_member(streams, *, member_span, baseline_span, episode, model=None):
    """Integrate the entire member, including its idle and harness/gate gaps.

    A single intact stream must cover the member and its baseline; restarts are
    never spliced. Any dropped counter in that hull, even below Block's global
    drop-fraction disclosure bar, makes DC missing for this member alone.
    The baseline-subtracted member total is scored against logged turn work.
    Per-turn training energy includes owned tools (unioned to avoid overlap).
    No z score is issued: meter uncertainty and DC registration are still owed.
    """
    if not _span(member_span) or not _span(baseline_span):
        return _empty(['meter.member_span_missing'])
    if not member_span[0] <= baseline_span[0] < baseline_span[1] <= member_span[1]:
        return _empty(['meter.baseline_outside_member'])
    if not member_span[0] <= episode.start_ns <= episode.end_ns <= member_span[1]:
        return _empty(['meter.episode_outside_member'])
    rejected = []
    for name, stream in streams:
        if not stream.present:
            rejected.append('meter.absent')
            continue
        offset = kp.raw_offset_ns(stream)
        if offset is None or not stream.aligned:
            rejected.append('meter.clock_unresolved')
            continue
        window = [v + offset for v in member_span]
        baseline = [v + offset for v in baseline_span]
        if not stream.host_ns[0] <= window[0] < window[1] <= stream.host_ns[-1]:
            rejected.append('meter.member_uncovered')
            continue
        if kp.span_has_drops(stream, *window):
            rejected.append('meter.member_gap')
            continue
        if any(e.get('rx') is None or window[0] <= e['rx'] < window[1] for e in stream.errors):
            rejected.append('meter.member_error')
            continue
        disclosures = kp.flags(stream, windows=[window])
        if any(f['code'] == 'meter.clock_fit_residual' for f in disclosures):
            rejected.append('meter.clock_fit_residual')
            continue
        energy, _ = kp.integrate(stream.host_ns, stream.watts, *window)
        base_j, _ = kp.integrate(stream.host_ns, stream.watts, *baseline)
        episode_j, _ = kp.integrate(stream.host_ns, stream.watts,
                                     episode.start_ns + offset, episode.end_ns + offset)
        if energy is None or base_j is None or episode_j is None:
            rejected.append('meter.member_uncovered')
            continue
        base_w = base_j / ((baseline[1] - baseline[0]) / 1e9)
        turn_energy = {}
        for turn in episode.logged_turns():
            intervals = _union([(turn.start_ns, turn.end_ns),
                                *((t.start_ns, t.end_ns) for t in turn.tool_calls if t.logged)])
            if any(not member_span[0] <= a <= b <= member_span[1] for a, b in intervals):
                return _empty(['meter.turn_outside_member'])
            active = 0.0
            for start, end in intervals:
                joules, _ = kp.integrate(stream.host_ns, stream.watts, start + offset, end + offset)
                if joules is None:
                    return _empty(['meter.turn_uncovered'])
                active += joules - base_w * ((end - start) / 1e9)
            # Zero here means unweighted exploratory OLS, NOT a physical
            # zero-uncertainty assertion. No score or threshold uses it.
            turn_energy[turn.index] = (active, 0.0)
        rows = er.turn_rows_from_episode(episode, turn_energy, hidden_token_counts_logged=True,
                                         uncertainty_kind='diagnostic_equal_weights')
        row = {**_empty(), 'status': 'available', 'stream': name,
               'raw_offset_ns': offset, 'member_span_ns': list(member_span),
               'baseline_span_ns': list(baseline_span), 'dc_in_energy_j': energy,
               'episode_dc_in_energy_j': episode_j, 'baseline_w': base_w,
               'dc_in_delta_j': energy - base_w * ((window[1] - window[0]) / 1e9),
               'flags': list(dict.fromkeys([*(f['code'] for f in disclosures), *rows.flags])),
               'turn_rows': [asdict(r) for r in rows], 'residual_status': 'dc_fit_not_supplied'}
        if model is not None:
            _predict(row, model)
        return row
    return _empty(list(dict.fromkeys(rejected or ['meter.absent'])))


def _json(path):
    return json.loads(read_bytes(Path(path)))


def session_report(custody, plan_members, runs_root, summaries):
    """Read-only W1/D desk addendum; outputs remain outside raw custody.

    Uses Block member/baseline clocks, parser and hash inventory. Fits a
    separate DC model per serving configuration and task pair on unique benign
    trajectories. Replays and rail-excluded members never train it. This is an
    in-sample diagnostic, not conformal calibration or a registered detector.
    """
    from joulewise.b5.harvest import member_spans, idle_baseline_span

    if custody is None:
        return unavailable_report(plan_members, 'meter.custody_unavailable')
    custody, runs_root = Path(custody), Path(runs_root)
    sources, streams, source_flags = [], [], []
    try:
        supervision = _json(custody / 'night/hazard_result.json').get('meter') or {}
    except Exception:  # diagnostic evidence cannot block the rails desk
        supervision = {}
    expected = {r['path']: r.get('sha256') for r in supervision.get('streams', [])}
    directory = custody / REQUIREMENT['custody_directory']
    paths = sorted({p.with_suffix('') if p.suffix == '.zst' else p
                    for pattern in ('stream-*.jsonl', 'stream-*.jsonl.zst') for p in directory.glob(pattern)})
    for path in paths:
        name = path.relative_to(custody).as_posix()
        try:
            digest = hashlib.sha256(read_bytes(path)).hexdigest()
            sources.append({'path': name, 'sha256': digest})
            if expected.get(name) != digest:
                source_flags.append('meter.custody_hash_mismatch')
                continue
            streams.append((name, kp.parse(path)))
        except Exception as exc:  # parser/decompression failure is missing DC, never a rail exclusion
            source_flags.append('meter.stream_unreadable:' + type(exc).__name__)
    summaries = {m['run_id']: m for m in summaries}
    members, groups = {}, defaultdict(list)
    for member in plan_members:
        rid = member['run_id']
        try:
            bundle = runs_root / rid
            metadata = _json(bundle / 'metadata.json')
            events = [json.loads(line) for line in read_bytes(bundle / 'events.jsonl').splitlines() if line.strip()]
            episode = from_json(Episode, read_bytes(bundle / 'outputs/align_episode.json').decode())
            row = capture_member(streams, member_span=member_spans(metadata, events)['member'],
                                 baseline_span=idle_baseline_span(metadata, events), episode=episode)
        except Exception as exc:  # preserve an unreadable member in the secondary roster
            row = _empty(['meter.member_unreadable:' + type(exc).__name__])
        row['flags'] = list(dict.fromkeys([*row['flags'], *source_flags]))
        if supervision.get('start_failures') or supervision.get('errors') or supervision.get('crash_loop'):
            row['flags'].append('meter.supervision_fault')
        members[rid] = row
        summary = summaries.get(rid) or {}
        config = (summary.get('summary') or {}).get('configuration')
        key = json.dumps([member.get('model_id'), member.get('task_pair'), config], sort_keys=True)
        groups[key].append((member, row, summary))
    models = []
    for key, rows in sorted(groups.items()):
        seen, training, training_ids = set(), [], []
        for member, row, summary in rows:
            trajectory = member.get('expected_episode_seed', member.get('seed_index'))
            if (row['status'] != 'available' or member.get('condition') != 'benign'
                    or member.get('is_replay') or summary.get('excluded', True) or trajectory in seen):
                continue
            seen.add(trajectory)
            training_ids.append(member['run_id'])
            training.extend(er.TurnRow(**r) for r in row['turn_rows'])
        model = er.fit_energy_model(training)
        models.append({'configuration': json.loads(key), 'training_run_ids': training_ids,
                       'model': asdict(model), 'flags': list(model.flags)})
        for _, row, _ in rows:
            _predict(row, model)
    return {'schema': 'joulewise.align_v4.km003c_secondary.v1', 'label': LABEL, 'print_only': True,
            'measurement': 'USB-C DC input; not AC wall energy or battery-corrected machine energy',
            'residual': 'idle-subtracted whole-member DC minus separate five-term DC prediction',
            'fit': 'exploratory equal-weight OLS; counts logged; unique benign trajectories; in sample',
            'uncertainty': 'not calibrated; no standardized scores or decisions',
            'sources': sources, 'members': members, 'models': models}
