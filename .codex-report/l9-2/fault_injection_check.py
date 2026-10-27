"""Check every fault-injection child against the clean parent (see fault_injection.py).

usage: fault_injection_check.py <out-dir>   -> prints a markdown table and writes verdicts.json
"""
import json
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
parent = json.loads((OUT / 'parent.json').read_text())
clean = parent['record']
ORDER = [row['step'] for row in clean['steps']]


def digests(record):
    return {(row['step'], row['window'], o['name']): o['sha256'] for row in record['steps'] for o in row['outputs']}


clean_digests = digests(clean)
rows, verdicts = [], []
for path in sorted((OUT / 'children').glob('*.json')):
    child = json.loads(path.read_text())
    info = child['child']
    name = info['name']
    if child['outcome'] == 'no_site':
        continue
    fired = child.get('fired') or []
    first = fired[0] if fired else {}
    verdict = dict(name=name, step=info['step'], k=info['k'], uncached=info['uncached'],
                   site=' <- '.join((first.get('site') or [])[:3]), trigger=first.get('trigger'), fired=len(fired))
    if child['outcome'] != 'ran' or child.get('record') is None:
        verdict.update(result='NO_RECORD', detail=child.get('traceback', '')[-300:], ok=False)
        verdicts.append(verdict)
        continue
    record = child['record']
    stop = next((row for row in record['steps'] if row['status'] != 'ok'), None)
    changed = []
    for row in record['steps']:
        if row['status'] != 'ok':
            continue
        for o in row['outputs']:
            key = (row['step'], row['window'], o['name'])
            if clean_digests.get(key) != o['sha256']:
                changed.append('/'.join(str(x) for x in key))
    refused = stop is not None and stop['status'] in ('tooling_refusal', 'unclassified_refusal')
    at_or_after = stop is not None and ORDER.index(stop['step']) >= ORDER.index(info['step'])
    if not fired:
        result = 'no_firing'
    elif changed:
        result = 'CHANGED_OUTPUT'
    elif refused and at_or_after:
        result = 'refused'
    elif stop is None:
        result = 'ABSORBED_NO_REFUSAL'
    else:
        result = 'OTHER_STOP'
    single = stop is not None and stop['refusal'] == 'calibration_wall_deadline_in_analysis'
    verdict.update(single_code=single, result=result, stop=None if stop is None else f"{stop['step']}/{stop['window']}/{stop['status']}/{stop['refusal']}",
                   changed=changed, ok=result in ('refused',), code=child.get('code'))
    verdicts.append(verdict)

(OUT / 'verdicts.json').write_text(json.dumps(verdicts, indent=1))
print('| child | first firing site | trigger | stop (step/window/status/refusal) | single code | changed ok-step outputs | result |')
print('|---|---|---|---|---|---|---|')
for v in verdicts:
    print(f"| {v['name']} | `{v['site']}` | {v.get('trigger')} | {v.get('stop')} | {v.get('single_code')} | {len(v.get('changed') or [])} | **{v['result']}** |")
print()
print('children with a firing:', len(verdicts), ' refused:', sum(v['result'] == 'refused' for v in verdicts),
      ' findings:', [v['name'] for v in verdicts if v['result'] not in ('refused',)])
print('parent code', parent.get('code'), 'wall_s', parent.get('wall_s'))
print('| step | wall s | refits |'); print('|---|---|---|')
for t in parent['timings']:
    print(f"| {t['step']} | {t['wall_s']} | {t['refits']} |")
