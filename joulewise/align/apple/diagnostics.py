"""Read-only screening diagnostics; none changes reducer eligibility or bundle bytes."""
from __future__ import annotations

import ast
from collections import defaultdict
import json
from pathlib import Path

from joulewise.desk_compress import read_bytes

READ_ONLY_PREFIXES = ('list_', 'view_', 'search_', 'get_')


def tool_inventory(episode, bundle):
    """Prefer recorded schemas; for v0 derive names from pinned SHADE definitions."""
    schemas = episode.hardware.get('task_diagnostics', {}).get('tool_schemas')
    if schemas is not None:
        names = sorted(s['function']['name'] for s in schemas)
        source = 'episode.task_diagnostics.tool_schemas'
    else:
        from joulewise.align.apple.workload import EpisodeSpec
        from joulewise.align.shade.upstream import PinnedUpstream
        config = json.loads(read_bytes(Path(bundle) / 'config.json'))
        spec = EpisodeSpec.from_text(config['workload_profile']['prompt_text'])
        keys = {k: spec.task_kwargs[k] for k in ('cache_dir', 'commit', 'file_sha256') if k in spec.task_kwargs}
        upstream = PinnedUpstream(**keys, allow_fetch=False)
        root = upstream.prepare()
        if root is None:
            return {'source': 'unavailable', 'names': [], 'state_changing': [], 'flags': upstream.flags}
        # Tools are plain function definitions in the verified tools/*.py source.
        # Reading AST avoids environment imports, model loading and service calls.
        names = sorted({node.name for path in (root / 'tools').glob('*.py')
                        for node in ast.parse(path.read_text()).body
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith('_')})
        source = f'SHADE:{upstream.commit}:tools/*.py'
    return {'source': source, 'names': names,
            'state_changing': [n for n in names if n != 'end_task' and not n.startswith(READ_ONLY_PREFIXES)],
            'classification': 'name_rule_v0'}


def action_diagnostics(episode):
    all_calls = [c for t in episode.turns for c in t.tool_calls]
    calls = [c for c in all_calls if c.name != 'end_task']
    observing = any(c.state_changed is not None for c in all_calls) or any(
        f.startswith('tool_state_unavailable:') for f in getattr(episode, 'flags', ()))
    counted, readonly, unobserved = [], [], []
    for call in calls:
        changed = call.state_changed
        if changed is None:
            if observing:
                unobserved.append(call.name)
                continue
            changed = not call.name.startswith(READ_ONLY_PREFIXES)
        (counted if changed else readonly).append(call.name)
    return {'state_changing_calls': len(counted), 'counted_tool_names': counted,
            'read_only_tool_names': readonly, 'unobserved_tool_names': unobserved,
            'classification': 'state_observation_v1' if observing else 'name_rule_v0'}


def end_state(episode, turn_rows=()):
    flags = list(episode.flags)
    for row in turn_rows:
        flags.extend(row.get('flags', ()))
    if any(f.startswith(('episode_error:', 'endpoint_error:', 'runner.error')) for f in flags):
        return 'runner.error'
    context = next((f for f in flags if f.startswith('episode.context_limit:')), None)
    if context:
        return context
    ended = next((f for f in flags if f.startswith('episode.end_task:')), None)
    if ended:
        return ended
    if 'turn_budget_reached' in flags or 'episode.max_turns' in flags:
        return 'episode.max_turns'
    cuts = [f for f in flags if f.startswith(('turn_token_budget_reached:', 'episode.turn_token_budget_reached:'))
            and episode.turns and f.rsplit(':', 1)[-1] == str(episode.turns[-1].index)]
    if cuts:
        return cuts[-1]
    # v0's native stop inside a thought was labelled a normal return.
    # A token-budget cut takes precedence as the cause; both conditions remain
    # visible in the retained turn flags and the summary's unclosed boolean.
    if 'ended_in_unclosed_reasoning' in flags or (
        episode.turns and not episode.turns[-1].tool_calls and turn_rows
        and 'unclosed_reasoning_span' in turn_rows[-1].get('flags', ())
    ):
        return 'ended_in_unclosed_reasoning'
    if any(c.name == 'end_task' for t in episode.turns for c in t.tool_calls):
        return 'end_task'
    return 'returned_without_tool_call'


def evidence_precheck(bundle, target_paths=None):
    value = json.loads(read_bytes(Path(bundle) / 'summary_metrics.json')).get('window_evidence_precheck', {})
    rows = []
    def visit(obj, path):
        if not isinstance(obj, dict):
            return
        if 'eligible' in obj:
            rows.append({'window': path, 'eligible': obj['eligible'], 'reasons': obj.get('reasons', [])})
        for key, child in obj.items():
            if isinstance(child, dict):
                visit(child, path + '/' + key)
    visit(value, '')
    # None is the standalone desk's request-energy diagnostic. An explicit
    # empty path list mirrors harvest._precheck_flags: null target paths are
    # skipped. In either case absent precheck evidence is not eligible.
    if target_paths is None:
        target_paths = [(key,) for key in ('gross_request', 'idle_subtracted_request') if key in value]
    selected = []
    for path in target_paths:
        node = value
        for key in path:
            node = node.get(key) if isinstance(node, dict) else None
        eligible = node.get('eligible') if isinstance(node, dict) else None
        reasons = node.get('reasons') if isinstance(node, dict) else None
        if not isinstance(reasons, list) or (eligible is not True and not reasons):
            reasons = ['window_evidence_precheck_missing']
        selected.append({'window': '/' + '/'.join(path),
                         'eligible': eligible, 'reasons': reasons})
    return {'eligible': bool(rows) and all(r['eligible'] is True for r in selected),
            'reasons': sorted({reason for r in selected for reason in r['reasons']}
                              | ({'window_evidence_precheck_missing'} if not rows else set())),
            'windows': selected, 'recorded': value,
            'phase_windows': [r for r in rows if r['window'].startswith('/phase/')],
            'request_windows': [r for r in rows if r['window'] in ('/gross_request', '/idle_subtracted_request')]}


def member_thermal_readings(custody):
    """OS thermal readings in spawn-to-exit member intervals, same monotonic clock."""
    custody = Path(custody)
    try:
        clocks = [json.loads(line) for line in read_bytes(custody / 'collection/run_clock.jsonl').splitlines() if line.strip()]
        readings = [json.loads(line) for line in read_bytes(custody / 'hazards/monitor/thermal.jsonl').splitlines() if line.strip()]
    except FileNotFoundError:
        return {}
    spans = defaultdict(dict)
    for row in clocks:
        if row.get('event') in ('start', 'end'):
            for run_id in row.get('unit_run_ids') or [row.get('run_id')]:
                spans[run_id][row['event']] = row['clock']['monotonic_ns']
    result = {}
    for run_id, span in spans.items():
        if not all(k in span for k in ('start', 'end')):
            continue
        samples = [r for r in readings if r.get('kind') == 'reading'
                   and span['start'] <= r['finished']['monotonic_ns'] <= span['end']]
        result[run_id] = {'interval_monotonic_ns': [span['start'], span['end']],
                          'sources': sorted({r['values'].get('source', 'unknown') for r in samples}),
                          'readings_monotonic_ns_level': [[r['finished']['monotonic_ns'], r['values'].get('level')] for r in samples],
                          'errors': [r['error'] for r in samples if r.get('error')]}
    return result


def telemetry_diagnostics(bundle, episode):
    """Clip interval supports to paired episode epoch stamps.

    Thermal samples use native elapsed_ns with the rich trace's first endpoint
    (the controller's recorded clock alignment), rather than rounded plist dates.
    GPU MHz = sum(freq * active_ns * overlap/elapsed) / sum(active_ns * overlap/elapsed).
    """
    from joulewise.adapters.powermetrics import parse_powermetrics_records
    bundle = Path(bundle)
    stamps = episode.hardware['paired_clock_stamps_ns']
    start, end = (s['epoch_ns'] / 1e9 for s in (stamps[0], stamps[-1]))
    flags = []
    try:
        rich = [json.loads(line) for line in read_bytes(bundle / 'rich_telemetry.jsonl').splitlines() if line.strip()]
    except FileNotFoundError:
        rich = []
        flags.append('diagnostic.rich_telemetry_unavailable')
    def overlap(t, elapsed):
        return max(0.0, min(end, t) - max(start, t - elapsed))
    numerator = denominator = 0.0
    for row in rich:
        elapsed = row['elapsed_ns'] / 1e9
        fraction = overlap(row['timestamp_s'], elapsed) / elapsed if elapsed > 0 else 0
        for state in (row.get('gpu') or {}).get('dvfm_states', ()):
            active = state.get('used_ns', 0) * fraction
            numerator += state['freq'] * active
            denominator += active
    thermal = defaultdict(float)
    try:
        raw = read_bytes(bundle / 'raw/powermetrics.plist')
        records = parse_powermetrics_records(raw, **(
            {'first_record_endpoint_s': rich[0]['timestamp_s']} if rich else {}))
        if not rich:
            flags.append('diagnostic.thermal_native_rounded_clock')
        for row in records:
            thermal[row.thermal_pressure or 'Unknown'] += overlap(row.timestamp_s, row.elapsed_ns / 1e9)
    except FileNotFoundError:
        flags.append('diagnostic.thermal_pressure_unavailable')
    return {'thermal_pressure_seconds': dict(thermal),
            'active_gpu_clock_mhz': numerator / denominator if denominator else None,
            'active_gpu_seconds': denominator / 1e9, 'diagnostic_flags': flags}
