import sys, json, pathlib, dataclasses
sys.path.insert(0, '.')
from joulewise.hazards import battery, base
ROOT = pathlib.Path('.')
FX = ROOT/'tests/fixtures/hazards/battery'
sys.path.insert(0, str(ROOT/'tests/hazards'))
import test_battery as tb
out = {}
for f in sorted(FX.glob('*.ioreg')):
    raw = f.read_bytes()
    for kw in ({}, {'age_s': 240}, {'timed_out': True}, {'returncode': 1}):
        try:
            m = tb.measure_bytes(raw, **kw)
            v = battery.judge(m, tb.LIMITS)
            rec = {'status': str(v.status), 'verdict': base._jsonable(dataclasses.asdict(v)) if dataclasses.is_dataclass(v) else repr(v)}
        except Exception as e:
            rec = {'exception': repr(e)}
        out[f"{f.name}|{kw}"] = rec
# publications table
table = json.loads((FX/'publications-20260925-20261005.json').read_text())
out['publications_keys'] = sorted(table.keys())
json.dump(out, open(sys.argv[1], 'w'), indent=1, sort_keys=True, default=str)
print('records', len(out))
