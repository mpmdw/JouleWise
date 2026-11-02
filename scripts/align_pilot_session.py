#!/usr/bin/env python3
"""Prepare, hand off, and desk one NON-CLAIM align pilot v0 session.

prepare and install are the BYTES item-H runner's (scripts/bytes_h_session.py)
with the align kit: the same measurement view, real window-plan writer,
installer interface and in-chain agent census. desk reads every align member's
bundle read-only into the instrument-check summary (PILOT.json), then runs the
real harvest with --non-claim. Nothing here is registered or claim data.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import bytes_h_session as h

KIT = Path('configs/campaigns/align_pilot_v1')
PACK_ID = 'align-pilot-v1'
SCHEMA = 'joulewise.align_pilot_desk.v0'
# Instrument flags whose presence makes a member's energy unusable for the
# pilot's checks; each is emitted by joulewise.align (sampler/attribution).
ENERGY_BLOCKING = ('power_unavailable', 'trace.missing', 'trace.ambiguous', 'clock_anchor_unresolved')
# Reason code for an estimate the strict JSON writer cannot carry (an
# unresolved anchor gives an infinite half-width): the value becomes null.
NONFINITE = 'estimate.nonfinite'
# Per-turn token counts that define one episode's work (protocol I4).
TURN_COUNTS = ('context_tokens', 'prefill_tokens', 'decode_tokens', 'hidden_tokens')


def prepare(measurement_root, session_root, **kwargs):
    return h.prepare(measurement_root, session_root, kit=KIT, pack_id=PACK_ID,
                     session_prefix='align-pilot-', **kwargs)


def install(session_root, **kwargs):
    return h.install(session_root, **kwargs)


def _member_rows(state):
    directory = Path(state.get('registration_dir', Path(state['measurement_root']) / KIT / 'registration')).parent
    plan = h.read(directory / 'collection_plan.json')
    return plan['members']


def _estimate(values):
    """Finite floats as is; a nonfinite one as null with its reason under 'unavailable'."""
    out, unavailable = {}, {}
    for name, value in values.items():
        if math.isfinite(value):
            out[name] = value
        else:
            out[name] = None
            unavailable[name] = f'{NONFINITE}:{value}'
    if unavailable:
        out['unavailable'] = unavailable
    return out


def turn_counts(summary):
    """The per-turn (context, prefill, decode, hidden) token tuples of one summary."""
    return tuple(zip(*(summary['per_turn_' + name] for name in TURN_COUNTS), strict=True))


def episode_summary(bundle):
    """One member's episode, energy per recorded power channel, and flags."""
    from joulewise.align.apple.workload import read_episode_bundle
    from joulewise.align.attribution import attribute_episode

    episode = read_episode_bundle(bundle)
    energy = {}
    for trace in episode.power_traces:
        result = attribute_episode(episode, source=trace.source, channel=trace.channel)
        energy[f'{trace.source}:{trace.channel}'] = {
            **_estimate({'joules': result.total.joules, 'half_width_j': result.total.half_width_j,
                         'segment_sum_j': math.fsum(s.energy.joules for s in result.segments)}),
            'method': result.total.method, 'segments': len(result.segments), 'flags': list(result.flags),
            'per_turn_j': [math.fsum(s.energy.joules for s in result.segments if s.turn == t.index)
                           for t in episode.turns],
            'per_turn_segments': [{'turn': s.turn, 'kind': s.kind, **_estimate({'joules': s.energy.joules})}
                                  for s in result.segments]}
    from joulewise.align.apple.diagnostics import tool_inventory, end_state, evidence_precheck, telemetry_diagnostics, READ_ONLY_PREFIXES
    from joulewise.desk_compress import read_bytes
    inventory = tool_inventory(episode, bundle)
    try:
        turn_rows = [json.loads(line) for line in read_bytes(Path(bundle) / 'outputs/align_turns.jsonl').splitlines() if line.strip()]
    except FileNotFoundError:
        turn_rows = []
    calls = [[c.name for c in t.tool_calls] for t in episode.turns]
    mutations = set(inventory['state_changing'])
    known = set(inventory['names'])
    totals = episode.totals()
    logged = episode.totals(logged_only=True)
    return {'episode_id': episode.episode_id, 'task_pair': episode.task_pair,
            'condition': episode.condition, 'seed': episode.seed,
            'duration_s': totals['duration_ns'] / 1e9, 'totals': totals, 'logged_totals': logged,
            **{'per_turn_' + name: [getattr(t, name) for t in episode.turns] for name in TURN_COUNTS},
            'main_task_score': episode.main_task_score, 'side_task_success': episode.side_task_success,
            'energy': energy, 'flags': list(episode.flags),
            'tool_inventory': inventory, 'tool_names_per_turn': calls,
            'state_changing_calls': sum(name in mutations or (name not in known and not name.startswith(READ_ONLY_PREFIXES))
                                        for turn in calls for name in turn),
            'unknown_tool_names': sorted({n for turn in calls for n in turn} - set(inventory['names'])),
            'end_state': end_state(episode, turn_rows),
            'ended_in_unclosed_reasoning': bool(episode.turns and not episode.turns[-1].tool_calls and turn_rows
                and 'unclosed_reasoning_span' in turn_rows[-1].get('flags', ())),
            'task_diagnostics': episode.hardware.get('task_diagnostics', {}),
            'window_evidence_precheck': evidence_precheck(bundle),
            **telemetry_diagnostics(bundle, episode)}


def instrument_checks(members):
    """The pilot's success criteria as an instrument check; never a hypothesis test.

    I1 every planned episode has a readable bundle; I2 each has energy on at
    least one channel with no blocking flag; I3 attribution tiles the episode
    (segment sum agrees within 1% of the smallest attribution half-width); I4 greedy
    repeats of one cell generate identical per-turn (context, prefill, decode,
    hidden) token counts. Repeat energy spreads are reported for the lead, with
    no pass bar, only for cells whose repeats did identical work. A null
    (nonfinite) estimate is never energy and never tiles.
    """
    readable = [m for m in members if m.get('summary')]
    usable = [m for m in readable if any(e['joules'] is not None for e in m['summary']['energy'].values())
              and not any(f.startswith(ENERGY_BLOCKING) for f in m['summary']['flags'])]
    # Agreement allowance: 1% of the smallest recorded attribution half-width
    # (about 1 J per real run), far above 1e6 x double summation roundoff.
    # Minimal synthetic dictionaries without uncertainty use that 1 J scale.
    widths = [e.get('half_width_j', 1.0) for m in usable for e in m['summary']['energy'].values()
              if e.get('half_width_j', 1.0) is not None and e.get('half_width_j', 1.0) > 0]
    agreement_j = 0.01 * min(widths) if widths else 0.01
    tiled = all(e['joules'] is not None and e['segment_sum_j'] is not None
                and abs(e['segment_sum_j'] - e['joules']) <= agreement_j
                for m in usable for e in m['summary']['energy'].values())
    cells = defaultdict(list)
    for m in readable:
        # Configuration blocks are different work, never greedy repeats of each other.
        cell = (m.get('block'), m['task_pair'], m['condition'])
        cells[cell].append(m['summary'])
    deterministic, spreads = {}, {}
    for (block, pair, condition), rows in sorted(cells.items(), key=lambda x: str(x[0])):
        key = (f'{block}/' if block else '') + f'{pair}/{condition}'
        deterministic[key] = len({turn_counts(r) for r in rows}) == 1
        if not deterministic[key]:
            continue
        for channel in sorted({c for r in rows for c in r['energy']}):
            values = [r['energy'][channel]['joules'] for r in rows
                      if channel in r['energy'] and r['energy'][channel]['joules'] is not None]
            if len(values) > 1:
                mean = math.fsum(values) / len(values)
                sd = math.sqrt(math.fsum((v - mean) ** 2 for v in values) / (len(values) - 1))
                spreads.setdefault(key, {})[channel] = {'n': len(values), 'mean_j': mean, 'sd_j': sd,
                                                        'range_j': max(values) - min(values),
                    'thermal_ineligible': any('thermal_pressure_elevated_in_window' in
                        r.get('window_evidence_precheck', {}).get('reasons', []) for r in rows),
                    'per_turn_j': [r['energy'][channel].get('per_turn_j', []) for r in rows if channel in r['energy']]}
    checks = {'I1_all_bundles_readable': len(readable) == len(members),
              'I2_energy_on_every_episode': len(usable) == len(members),
              'I3_attribution_tiles_episode': bool(usable) and tiled,
              'I4_greedy_repeats_identical_tokens': bool(deterministic) and all(deterministic.values())}
    prechecks = [m['summary'].get('window_evidence_precheck', {}) for m in readable]
    checks['chain_eligibility'] = bool(prechecks) and all(p.get('eligible') is not False for p in prechecks)
    return checks, deterministic, spreads


def desk(session_root, *, run=subprocess.run, harvest=True):
    session = Path(session_root).resolve()
    state = h.read(session / 'session.json')
    plan = h.read(state['plan_path'])
    custody = Path(plan['custody_root'])
    if not (custody / 'night/result.json').is_file():
        raise ValueError('terminal record is required before desk')
    runs_root = Path(state['runs_roots'].get('claim') or Path(state['inputs']['runs_parent']) / 'runs_align_pilot_v0')
    members = []
    for row in _member_rows(state):
        bundle = runs_root / row['run_id']
        entry = {k: row[k] for k in ('run_id', 'task_pair', 'condition', 'repeat', 'ordinal')}
        for key in ('model_id', 'block'):
            if key in row:
                entry[key] = row[key]
        try:
            entry['summary'] = episode_summary(bundle)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            entry['summary'] = None
            entry['unreadable'] = f'{type(exc).__name__}: {exc}'
        members.append(entry)
    checks, deterministic, spreads = instrument_checks(members)
    # Read-only extraction first; the harvest may compress the runs afterwards.
    pilot = {'schema_version': SCHEMA, 'non_claim': True, 'session_id': state['session_id'],
             'plan_id': state['session_id'], 'runs_root': str(runs_root), 'members': members,
             'checks': checks, 'repeat_token_identity': deterministic, 'repeat_energy_spread': spreads,
             'status': 'instrument_ok' if all(checks.values()) else 'instrument_incomplete'}
    h.write(session / 'PILOT.json', pilot)
    measurement = Path(state['measurement_root'])
    argv = [str(measurement / '.venv/bin/python'), str(measurement / 'scripts/harvest_b6_session.py'),
            '--plan', state['plan_path'], '--archive-root', str(session / 'archive'),
            '--registration-dir', state['registration_dir'], '--pack-records-root', str(session / 'private'),
            '--export-dir', str(session / 'export'), '--non-claim']
    if harvest:
        result = run(argv, check=False, capture_output=True, text=True, timeout=h.HARVEST_TIMEOUT_S)
    else:
        from types import SimpleNamespace
        result = SimpleNamespace(returncode=None, stdout='', stderr='')
    (session / 'staging/harvest.stdout').write_text(result.stdout or '')
    (session / 'staging/harvest.stderr').write_text(result.stderr or '')
    status = {'schema_version': SCHEMA, 'non_claim': True, 'plan_id': state['session_id'],
              'pilot': str(session / 'PILOT.json'), 'pilot_status': pilot['status'], 'checks': checks,
              'harvest_argv': argv, 'harvest_exit': result.returncode,
              'harvest_status': ('not_run' if not harvest else 'ok' if result.returncode in (0, 6) else 'program_fault')}
    h.write(session / 'desk.json', status)
    print('pilot_status: ' + pilot['status'])
    for name, ok in checks.items():
        print(f'{name}: {"pass" if ok else "fail"}')
    for member in members:
        summary = member.get('summary')
        if summary is None:
            print(member['run_id'] + ': unreadable ' + member['unreadable'])
            continue
        pre = summary['window_evidence_precheck']
        print(member['run_id'] + ': ' + json.dumps({
            'end_state': summary['end_state'], 'state_changing_calls': summary['state_changing_calls'],
            'tool_names_per_turn': summary['tool_names_per_turn'], 'unknown_tool_names': summary['unknown_tool_names'],
            'thermal_pressure_seconds': summary['thermal_pressure_seconds'],
            'active_gpu_clock_mhz': summary['active_gpu_clock_mhz'],
            'chain_eligible': pre['eligible'], 'chain_reasons': pre['reasons'],
            'window_evidence_precheck': {r['window']: {'eligible': r['eligible'], 'reasons': r['reasons']} for r in pre['windows']},
            'ended_in_unclosed_reasoning': summary['ended_in_unclosed_reasoning']}, sort_keys=True))
    print('repeat_energy_spread: ' + json.dumps(spreads, sort_keys=True))
    print('harvest_exit: ' + str(result.returncode))
    return status


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('prepare')
    p.add_argument('--measurement-root', type=Path, required=True)
    p.add_argument('--session-root', type=Path, required=True)
    for name in ('install', 'desk'):
        commands.add_parser(name).add_argument('--session-root', type=Path, required=True)
    commands.choices['desk'].add_argument('--no-harvest', action='store_true', help='Extract only; do not run archive/compression stages.')
    args = parser.parse_args(argv)
    try:
        if args.command == 'prepare':
            prepare(args.measurement_root, args.session_root)
        elif args.command == 'install':
            install(args.session_root)
        else:
            status = desk(args.session_root, harvest=not args.no_harvest)
            return 0 if status['harvest_status'] in ('ok', 'not_run') and status['pilot_status'] == 'instrument_ok' else 2
        return 0
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print('align_pilot_session: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
