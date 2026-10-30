"""Reader paths that raise instead of printing a reasoned record. Usage: python3.13 -B refusals.py /tmp/jw /tmp/kbout"""
import json, sys
from copy import deepcopy
sys.path[:0] = [sys.argv[1]]
from scripts import bytes_stream_test as p
inp = json.load(open(sys.argv[2]+'/input_A_knee_found.json'))
scan, base = inp['scan'], inp['records']
def attempt(name, records, sc=scan):
    try:
        r = p.read_known_bytes(records, sc)
        print(f'{name}: printed; rails={r["boundaries"]["rails"]["class"]} reasons={r["reasons"]}')
    except Exception as e:
        print(f'{name}: RAISED {type(e).__name__}: {e}')
r = deepcopy(base); r[3]['harvest']['meter_gaps'] = [{'span': 'stream', 'missing_samples': 1}]; r[3]['harvest']['adapter_source'] = ''
attempt('gap with unnamed adapter source', r)
r = deepcopy(base); r[3]['harvest']['meter_gaps'] = [{'span': 'stream', 'missing_samples': 1}]; del r[3]['harvest']['adapter_max_w']
attempt('gap with adapter rating missing', r)
attempt('seven calls (one call lost)', deepcopy(base[:7]))
r = deepcopy(base); del r[0]['harvest']['r_max_s']
attempt('r_max missing (no meter clock fit)', r)
r = deepcopy(base); r[0]['harvest']['energy_j']['meter'] = None
attempt('meter stream integral missing', r)
r = deepcopy(base); del r[0]['harvest']['operative_timing_bound_s']
attempt('operative timing bound missing (description)', r)
r = deepcopy(base); r[0]['harvest']['idle']['pre']['meter'][1]['stamp_ns'] = r[0]['harvest']['idle']['pre']['meter'][0]['stamp_ns']
attempt('one duplicated meter stamp in a pre-idle span', r)
