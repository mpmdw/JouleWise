#!/usr/bin/env python3
"""Derive pilot-4 planning receipts from immutable pilot-3 files, without MLX."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from joulewise.desk_compress import read_bytes


def digest(path):
    path = Path(path)
    resolved = path.resolve()
    recorded_path = resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(path)
    return {'path': recorded_path, 'sha256': hashlib.sha256(read_bytes(path)).hexdigest(),
            'digest_bytes': 'logical uncompressed bytes'}


def read(path):
    return json.loads(read_bytes(path))


def lines(path):
    return [json.loads(line) for line in read_bytes(path).splitlines() if line.strip()]


def derive(session):
    session = Path(session).resolve()
    state = read(session / 'session.json')
    runs = Path(state['runs_roots']['claim'])
    log_path = runs / 'campaign_log.jsonl'
    logs = {r['run_id']: r for r in lines(log_path) if 'duration_s' in r}
    observations, rates, trajectories, first_prompts = [], {'A': [], 'B': [], 'C': []}, [], []
    collection = read(Path(state['registration_dir']).parent / 'collection_plan.json')
    for member in collection['members']:
        run_id = member['run_id']
        bundle = runs / run_id
        ep_path, events_path = bundle / 'outputs/align_episode.json', bundle / 'events.jsonl'
        turns_path = bundle / 'outputs/align_turns.jsonl'
        episode, turns, events = read(ep_path), lines(turns_path), lines(events_path)
        inventory = [{'path': p.relative_to(bundle).as_posix(), 'bytes': p.stat().st_size}
                     for p in sorted(bundle.rglob('*')) if p.is_file()]
        observations.append({'run_id': run_id, 'block': member['block'], 'member_s': logs[run_id]['duration_s'],
                             'episode_s': (episode['end_ns'] - episode['start_ns']) / 1e9,
                             'bundle_bytes': sum(p['bytes'] for p in inventory), 'bundle_inventory': inventory,
                             'episode': digest(ep_path), 'events': digest(events_path), 'turns': digest(turns_path)})
        starts, durations = {}, {}
        for event in events:
            phase = event.get('phase')
            index = event.get('metadata', {}).get('align_turn_index')
            if phase not in ('prefill', 'decode') or index is None:
                continue
            key = (index, phase)
            if event['event_type'] == 'phase_start':
                starts[key] = event['timestamp_s']
            elif event['event_type'] == 'phase_end':
                durations[key] = event['timestamp_s'] - starts[key]
        represented = []
        fresh_s = 0.0
        for t, row in zip(episode['turns'], turns, strict=True):
            p, o = row['generation']['prompt_token_ids'], row['generation']['output_token_ids']
            n = 0
            for a, b in zip(represented, p):
                if a != b:
                    break
                n += 1
            n = min(n, len(p) - 1)
            rate = {'run_id': run_id, 'turn': t['index']}
            for phase, count in (('prefill', row['generation']['prefill_tokens']), ('decode', len(o))):
                rate[phase + '_tokens'] = count
                rate[phase + '_s'] = durations[(t['index'], phase)]
                rate[phase + '_tok_s'] = count / rate[phase + '_s']
            rates[member['block']].append(rate)
            fresh_s += (len(p) - n) / rate['prefill_tok_s']
            represented = p + o
        old_prefill = sum(r['prefill_s'] for r in rates[member['block']] if r['run_id'] == run_id)
        trajectories.append({'run_id': run_id, 'block': member['block'],
                             'cached_episode_forecast_s': observations[-1]['episode_s'] - old_prefill + fresh_s,
                             'uncached_episode_s': observations[-1]['episode_s']})
        first_prompts.append(len(turns[0]['generation']['prompt_token_ids']))
    journal_path = session / 'custody/night/chain-stages.jsonl'
    journal = lines(journal_path)
    start, end = min(r['started_epoch_s'] for r in journal), max(r['ended_epoch_s'] for r in journal)
    science = [r['ended_epoch_s'] - r['started_epoch_s'] for r in journal if '-episodes-' in r['stage_id']]
    align_ids = {r['run_id'] for r in observations}
    scaffold = [{'path': str(p), 'bytes': sum(f.stat().st_size for f in p.rglob('*') if f.is_file())}
                for root in sorted((session / 'runs-parent').iterdir()) if root.is_dir()
                for p in sorted(root.iterdir()) if p.is_dir() and (p / 'config.json').is_file() and p.name not in align_ids]
    old_path = ROOT / 'configs/campaigns/align_pilot_v1/registration/sizing_b5.json'
    old = next(iter(read(old_path)['packs'].values()))['blocks'][0]
    largest_prefill = max(rates['A'], key=lambda r: r['prefill_s'])
    slowest_decode = min(rates['A'], key=lambda r: r['decode_tok_s'])
    planning_turn_observations = {
        'population': 'all measured turns of all 12 pilot3 A members, both task pairs and conditions, including all three greedy repeats per cell',
        'n_turns': len(rates['A']),
        'source': 'digested events.jsonl prefill/decode phase_start..phase_end markers and align_turns.jsonl generation token counts',
        'largest_fed_prefill': {**largest_prefill, 'statistic': 'maximum fed-prefill phase duration',
                               'planning_s': math.ceil(largest_prefill['prefill_s'] * 1000) / 1000,
                               'rounding': 'up to 0.001 s'},
        'slowest_decode': {**slowest_decode, 'statistic': 'minimum decode tokens / decode phase duration',
                           'planning_tok_s': math.floor(slowest_decode['decode_tok_s'] * 100) / 100,
                           'rounding': 'down to 0.01 tok/s'},
    }
    return {'non_claim': True, 'source_session': str(session), 'session': digest(session / 'session.json'),
            'collection_plan': digest(Path(state['registration_dir']).parent / 'collection_plan.json'),
            'campaign_log': digest(log_path), 'member_observations': observations,
            'phase_rates': rates, 'cache_trajectory_forecasts': trajectories,
            'planning_turn_observations': planning_turn_observations,
            'smallest_first_prompt_tokens': min(first_prompts), 'pilot3_idle_s': 300,
            'scaffold_s': end - start - sum(science), 'scaffold_bundle_bytes': scaffold,
            'scaffold_derivation': {'journal': digest(journal_path), 'start_s': start, 'end_s': end,
                                    'episode_stage_s': science, 'formula': 'last_end-first_start-sum(episode_stage_s)'},
            'disk_derivation': 'sum regular-file stat sizes per pilot3 bundle; OLS bytes ~ 1 + member_s',
            **{k: old[k] for k in ('tool_s_per_turn', 'tool_calls_per_turn_observed_max',
                                   'state_observation_s_per_call', 'tool_allowance_s_per_turn')},
            'tool_allowance_source': digest(old_path),
            'forecast_derivation': 'Keep pilot3 non-prefill episode time; replace each prefill duration by fed LCP delta / same-turn measured full-prompt rate. Transferring full-prompt rates to cached fed deltas is unmeasured; rehearsal records per-turn fed-token prefill rates with cached-context counts to replace it. Native-state ledger = prompt+emitted IDs, including EOS; conditional transfer, not hardware validation.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot-session', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=Path(__file__).with_name('sizing_evidence.json'))
    args = parser.parse_args(argv)
    args.out.write_text(json.dumps(derive(args.pilot_session), indent=2, sort_keys=True) + '\n')
    print('derived pilot3 sizing evidence (no model work)')


if __name__ == '__main__':
    main()
