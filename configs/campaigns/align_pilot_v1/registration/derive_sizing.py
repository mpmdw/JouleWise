#!/usr/bin/env python3
"""Capture read-only pilot-1/BYTES sizing inputs; no model or sampler runs."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def derive(pilot_session, bytes_sessions):
    runs = pilot_session / 'runs-parent/runs_align_pilot_v0'
    log_path = runs / 'campaign_log.jsonl'
    logs = [json.loads(line) for line in log_path.read_text().splitlines() if line.strip()]
    observations, episodes = [], []
    for row in logs:
        if 'duration_s' not in row or not row.get('run_id', '').startswith('align-pilot-v0-episodes-'):
            continue
        path = runs / row['run_id'] / 'outputs/align_episode.json'
        e = read(path)
        observations.append({'run_id': row['run_id'], 'member_s': row['duration_s'],
                             'episode_s': (e['end_ns']-e['start_ns'])/1e9, 'episode': digest(path)})
        episodes.append(e)
    observations.sort(key=lambda r:r['run_id'])
    episodes.sort(key=lambda e:e['episode_id'])
    def rate(e, turn):
        t=e['turns'][turn]
        return {'episode_id':e['episode_id'], 'turn':turn, 'prefill_tokens':t['prefill_tokens'],
                'decode_tokens':t['decode_tokens'], 'prefill_s':(t['first_token_ns']-t['start_ns'])/1e9,
                'decode_s':(t['end_ns']-t['first_token_ns'])/1e9,
                'prefill_tok_s':t['prefill_tokens']/((t['first_token_ns']-t['start_ns'])/1e9),
                'decode_tok_s':t['decode_tokens']/((t['end_ns']-t['first_token_ns'])/1e9)}
    long = [e for e in episodes if len(e['turns']) == 7]  # Pilot-1 long cell: seven recorded turns.
    journal_path = pilot_session / 'custody/night/chain-stages.jsonl'
    journal = [json.loads(line) for line in journal_path.read_text().splitlines() if line.strip()]
    start=min(r['started_epoch_s'] for r in journal)
    end=max(r['ended_epoch_s'] for r in journal)
    science=[r for r in journal if r['kind']=='campaign_collection' and '-episodes-' in r['stage_id']]
    scaffold=end-start-sum(r['ended_epoch_s']-r['started_epoch_s'] for r in science)
    rates={}
    for model in ('qwen3-30b-a3b','qwen3-next-80b'):
        rows=[]
        for path in sorted(bytes_sessions.glob(f'*/runs-parent/*/bytes-{model}-abs-*/summary_metrics.json')):
            summary=read(path)
            if summary['status'] != 'succeeded':
                continue
            event_path=path.parent/'events.jsonl'
            events=[json.loads(line) for line in event_path.read_text().splitlines() if line.strip()]
            spans={}
            for phase in ('prefill','decode'):
                a=[e['timestamp_s'] for e in events if e.get('event_type')=='phase_start' and e.get('phase')==phase]
                b=[e['timestamp_s'] for e in events if e.get('event_type')=='phase_end' and e.get('phase')==phase]
                spans[phase]=b[-1]-a[-1]
            c=read(path.parent/'config.json')
            p=c['workload_profile']['prompt_tokens']; d=c['workload_profile']['output_tokens']
            rows.append({'run_id':path.parent.name, 'summary':digest(path), 'events':digest(event_path),
                         'prefill_tokens':p, 'decode_tokens':d, **{k+'_s':v for k,v in spans.items()},
                         'prefill_tok_s':p/spans['prefill'], 'decode_tok_s':d/spans['decode']})
        if not rows:
            raise ValueError('no succeeded BYTES absolute records for '+model)
        rates[model]=rows
    config=read(runs/observations[0]['run_id']/'config.json')
    return {'non_claim':True, 'member_observations':observations, 'campaign_log':digest(log_path),
            'scaffold_s':scaffold, 'scaffold_derivation':{'journal':digest(journal_path), 'start_s':start, 'end_s':end,
                'episode_stage_s':[r['ended_epoch_s']-r['started_epoch_s'] for r in science],
                'formula':'last_end-first_start-sum(episode_stage_wall); includes actual stage settles'},
            'pilot1_idle_s':config['sampling']['idle_seconds'],
            'long_context_start':rate(long[0],0), 'long_context_end':rate(long[-1],len(long[-1]['turns'])-1),
            'factor_derivation':'last long-cell repeat final turn / first long-cell repeat initial turn; includes thermal slowdown',
            'bytes_rates':rates, 'bytes_rate_derivation':'mean of all succeeded absolute records, tokens / recorded prefill or decode phase duration'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pilot-session',type=Path,required=True)
    p.add_argument('--bytes-sessions',type=Path,required=True)
    p.add_argument('--out',type=Path,default=Path(__file__).with_name('sizing_evidence.json'))
    a=p.parse_args()
    a.out.write_text(json.dumps(derive(a.pilot_session,a.bytes_sessions),indent=2,sort_keys=True)+'\n')
    print('derived sizing evidence')

if __name__=='__main__':
    main()
