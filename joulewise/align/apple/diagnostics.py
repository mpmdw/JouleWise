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
            'state_changing': [n for n in names if not n.startswith(READ_ONLY_PREFIXES)]}


def end_state(episode, turn_rows=()):
    flags = list(episode.flags)
    for row in turn_rows:
        flags.extend(row.get('flags', ()))
    if any(f.startswith(('episode_error:', 'endpoint_error:', 'runner.error')) for f in flags):
        return 'runner.error'
    context = next((f for f in flags if f.startswith('episode.context_limit:')), None)
    if context:
        return context
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


def evidence_precheck(bundle):
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
    return {'eligible': all(r['eligible'] for r in rows) if rows else None,
            'reasons': sorted({reason for r in rows for reason in r['reasons']}),
            'windows': rows, 'recorded': value}


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
