# Cold gate A1 probe: D3 (witness category matched inside the message) and a candidate cure.
import sys, os, re, gzip, json, pathlib
scratch = pathlib.Path('/tmp/cg-ntpfix2-d528efb2'); root = scratch / 'new'
sys.path.insert(0, str(root)); os.chdir(root)
from joulewise import network_time_window as nt
from tests.test_network_time_window import WindowTests, line
CURE = re.compile(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+[+-]\d\d:?\d\d\s+(?:\S+\s+)?timed\[\d+\]:?\s+\[com\.apple\.timed:data\](?:\s|$)")
attacks = {
    'auditor_payload': line(9900, 'text', 'quoted timed[11]: [com.apple.timed:data]'),
    'payload_no_colon': line(9900, 'text', 'x timed[1] [com.apple.timed:data] y'),
    'other_process_then_timed': line(9900, 'text', 'a b c timed[2]: [com.apple.timed:data]'),
}
for name, text in attacks.items():
    t = WindowTests(); t.setUp()
    try:
        t.query(text)
        print('D3', name, json.dumps({'candidate_verdict': t.verdict(),
              'candidate_regex_matches': bool(nt._DATA_CATEGORY.match(text.rstrip('\n'))),
              'cure_regex_matches': bool(CURE.match(text.rstrip('\n')))}))
    finally:
        t.doCleanups()
print('D3 fixture_true_data_line', bool(CURE.match(line(9900).rstrip('\n'))))
gz = next((root / 'docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/evidence').glob('timed-full-*.gz'))
for label, raw in (('preserved_gz', gzip.decompress(gz.read_bytes())),
                   ('q2_utc', pathlib.Path('/tmp/cg-ntpd-d528efb2/q2_utc.txt').read_bytes())):
    lines = raw.decode().splitlines()
    stamped = [l for l in lines if nt._STAMP.match(l)]
    # Independent positional parse: fields split on whitespace; field 3 is process[pid]:, field 4 the category.
    positional = 0
    for l in stamped:
        f = l.split()
        if len(f) >= 5 and re.fullmatch(r"timed\[\d+\]:?", f[3]) and f[4] == '[com.apple.timed:data]':
            positional += 1
    print('D3', label, json.dumps({'stamped_lines': len(stamped),
          'substring_anywhere': sum('[com.apple.timed:data]' in l for l in lines),
          'candidate_regex': sum(bool(nt._DATA_CATEGORY.match(l)) for l in lines),
          'cure_regex': sum(bool(CURE.match(l)) for l in lines),
          'positional_parse': positional}))
print('PROBE_D3_COMPLETE')
