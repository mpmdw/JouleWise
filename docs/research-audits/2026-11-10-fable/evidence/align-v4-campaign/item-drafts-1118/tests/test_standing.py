"""Renewal boundary and unchanged item-346 ledger law on synthetic clocks/ledgers."""
import datetime as dt
import difflib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo
HERE=Path(__file__).resolve().parents[1]
text=(HERE/'STANDING-F0-r2.md').read_text(); original=(HERE/'evidence/standing-f0-original.md').read_text()
meta=json.loads((HERE/'items.json').read_text()); start=int(dt.datetime.fromisoformat(meta['standing']['renewal_start']).timestamp()); end=start+7*86400
assert start==1795377084 and end==1795981884
assert meta['standing']['pin_unchanged']
# Every original hash and all ten rules' operational bytes stay unchanged.
assert re.search("<<'HASHES'\n(.*?)\nHASHES",original,re.S).group(1)==re.search("<<'HASHES'\n(.*?)\nHASHES",text,re.S).group(1)
assert '--fresh-soak --parts C' in text and '14400' in text and 'len(today) >= 3' in text
oldblocks=re.findall(r'```sh\n(.*?)```',original,re.S); blocks=re.findall(r'```sh\n(.*?)```',text,re.S)
assert blocks[1:]==oldblocks[1:]
patch=(HERE/'evidence/standing-f0-r2.diff').read_text()
expected=''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile=f"origin/main@{meta['standing']['source_main']}:RUN_STATE item 346",tofile='STANDING-F0-r2.md'))
assert patch==expected
checks=0
gate=re.search(r'renewal_gate\(\) \{.*?\n\}',text,re.S).group()
for shell in ('bash','zsh'):
    for label,issued,now,ok in [('unissued','UNFILLED',start,False),('early',str(start),start-1,False),('start',str(start),start,True),('last second',str(start),end-1,True),('expiry',str(start),end,False),('later actual issue',str(start+1),start+1,False)]:
        script=f'RENEWAL_START_EPOCH={start}\nEXPIRY_EPOCH={end}\nRENEWAL_ISSUED_EPOCH={issued}\n{gate}\ndate() {{ echo {now}; }}\nrenewal_gate\n'
        r=subprocess.run([shell],input=script,text=True,capture_output=True)
        assert (r.returncode==0)==ok,(label,r.stdout,r.stderr); checks+=1; print('PASS',shell,'renewal',label)
program=re.search(r'F0_NOW=.*?<<\'PY\'\n(.*?)\nPY',text,re.S).group(1)
TZ=ZoneInfo('America/Los_Angeles')
with tempfile.TemporaryDirectory(prefix='.standing-test-',dir=HERE) as temp:
    ledger=Path(temp)/'SYNTHETIC-ledger.tsv'
    def test(name,now,t0s=(),bound='none',ok=True):
        global checks
        ledger.write_text(''.join(f'{t}\tsynthetic\tSYNTHETIC\n' for t in t0s))
        code=program.replace('now = time.time();',f'now = {now};')
        r=subprocess.run([sys.executable,'-I','-B','-',str(ledger),str(bound),'none'],input=code,text=True,capture_output=True)
        assert (r.returncode==0)==ok,(name,r.stdout,r.stderr); checks+=1; print('PASS F0 original ledger law',name)
    day=dt.datetime(2026,11,22,tzinfo=TZ).timestamp()
    test('02:34:59 refused',day+9299,ok=False); test('02:35 admitted',day+9300)
    test('22:40 admitted',day+81600); test('22:40:01 refused',day+81601,ok=False)
    test('spacing 14399 refused',start,[start-14399],ok=False); test('spacing 14400 allowed',start,[start-14400])
    test('three today refused',day+81600,[day+9300,day+23700,day+38100],ok=False)
    test('counted bound exact allowed',start,bound=start+12180+1200)
    test('counted bound second short refused',start,bound=start+12180+1199,ok=False)
print(checks,'standing-F0 checks; zero failures; unchanged hash table/launch/Check and spacing/day/window rules')
