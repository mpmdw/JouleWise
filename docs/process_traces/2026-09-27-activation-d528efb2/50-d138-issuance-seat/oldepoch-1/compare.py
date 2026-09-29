#!/usr/bin/env python3
"""Compare D-138 old-epoch replay output and show numeric differences/refusals."""
import json
import math
import sys
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit('usage: compare.py <dirA> <dirB>')
a, b = (Path(s) for s in sys.argv[1:])

def read(root):
    status = (root / 'exit-status.txt').read_text().strip()
    report_path = root / 'bracket.json'
    report = json.loads(report_path.read_text()) if report_path.exists() else None
    return status, report, (root / 'stdout.txt').read_text(), (root / 'stderr.txt').read_text()

left, right = read(a), read(b)
def walk(x, y, path='$'):
    if isinstance(x, dict) and isinstance(y, dict):
        for key in sorted(x.keys() | y.keys()):
            if key not in x or key not in y:
                print(f'SHAPE {path}.{key}: {"missing" if key not in x else "present"} / {"missing" if key not in y else "present"}')
            else:
                walk(x[key], y[key], f'{path}.{key}')
    elif isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y):
            print(f'SHAPE {path}.length: {len(x)} / {len(y)}')
        for i, (u, v) in enumerate(zip(x, y)):
            walk(u, v, f'{path}[{i}]')
    elif type(x) in (int, float) and type(y) in (int, float):
        if x != y and not (isinstance(x, float) and isinstance(y, float) and math.isnan(x) and math.isnan(y)):
            print(f'NUMERIC {path}: {x!r} / {y!r}')
    elif x != y:
        print(f'VALUE {path}: {x!r} / {y!r}')

print(f'exit status: {left[0]} / {right[0]}')
if left[1] is None or right[1] is None:
    print('report: absent on ' + ', '.join(label for label, item in (('A', left), ('B', right)) if item[1] is None))
else:
    if left[1] == right[1]:
        print('report: IDENTICAL')
    else:
        walk(left[1], right[1])
for label, item in (('A', left), ('B', right)):
    report = item[1]
    print(f'{label} refusal stderr: {item[3].strip() or "<none>"}')
    if report:
        print(f'{label} bracket status: {report.get("bracket", {}).get("status")}')
        print(f'{label} refusal reasons: {report.get("reasons")}')
        print(f'{label} acceptance freshness: {report.get("bracket", {}).get("acceptance", {}).get("freshness", {}).get("status")}')
if left == right:
    print('ALL CONTENT IDENTICAL')
