#!/usr/bin/env python3
"""Offline SHADE observation cost, no model/native generation or collectors."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from joulewise.align.apple.pilot import offline_shade_task

def measure(samples=100):
    results = []
    for pair in ('spam_filter_update', 'bank_transfer_2'):
        task = offline_shade_task(pair, cache_dir='/Users/edr/.cache/joulewise/shade')
        task.reset(1)
        checks = []
        for name, args in [('list_files', {}), ('create_file', {'filename':'observation-check','content':'offline'}),
                           ('list_files', {}), ('end_task', {})]:
            before = task.environment_state_sha256()
            task.call_tool(name, json.dumps(args))
            after = task.environment_state_sha256()
            checks.append({'name':name, 'state_changed':before != after})
        assert [c['state_changed'] for c in checks] == [False, True, False, False], checks
        task.reset(1)
        costs = []
        digests = set()
        for _ in range(samples):
            start = time.perf_counter_ns()
            before = task.environment_state_sha256()
            mid = time.perf_counter_ns()
            task.call_tool('list_files', '{}')
            end_call = time.perf_counter_ns()
            after = task.environment_state_sha256()
            end = time.perf_counter_ns()
            assert before == after
            digests.add(before)
            costs.append(((mid-start)+(end-end_call))/1e6)
        assert len(digests) == 1
        results.append({'task_pair':pair, 'samples':samples, 'hash_pair_mean_ms':statistics.mean(costs),
                        'hash_pair_sd_ms':statistics.stdev(costs), 'hash_pair_max_ms':max(costs),
                        'hash_pair_median_ms':statistics.median(costs), 'checks':checks,
                        'initial_state_sha256':next(iter(digests)),
                        'public_model_fields':list(type(task._definition.environment).model_fields),
                        'private_attributes':list(task._definition.environment.__pydantic_private__)})
    return {'scope':'offline real SHADE environments; agent-active timings, no MLX model or hardware capture',
            'derivation':'100 paired hash observations per environment, sum of perf_counter_ns time around before/after hashes only; call excluded',
            'source_sha256':hashlib.sha256((ROOT/'joulewise/align/shade/task.py').read_bytes()).hexdigest(),
            'results':results}
if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    result=measure();a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for r in result['results']:
        print(f"STATE_COST {r['task_pair']} n={r['samples']} added_mean_ms={r['hash_pair_mean_ms']:.6f} sd_ms={r['hash_pair_sd_ms']:.6f} max_ms={r['hash_pair_max_ms']:.6f}")
