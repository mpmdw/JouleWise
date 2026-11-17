"""Execute hp-02's exact item gates in both shells on synthetic observations."""
import ast
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE=Path(__file__).resolve().parents[1]
checks=0
for item in json.loads((HERE/'hp-02/items.json').read_text()):
    text=(HERE/'hp-02'/('ITEM-'+item['item']+'.md')).read_text()
    blocks=re.findall(r'```sh\n(.*?)```',text,re.S)
    assert sum(x.count('hp_gate || exit 1') for x in blocks)==2
    gates=blocks[0].split('# BEGIN TESTABLE GATES\n')[1].split('# END TESTABLE GATES')[0]
    now=item['bands'][2][0]; protected=item['worst_case_s']+560+1200
    defaults={'HP_LOOK_RUN':'no','HP_DELTA_OK':'yes','HP01_SMOKE_PASS':'yes','LINE2_OK':'yes','LINE9_OK':'yes',
        'CHECKLIST_OK':'yes','STOPS_CLEAR':'yes','HOST_STATE_RECORDED':'yes','COPY_TYPED_OK':'yes',
        'HOST_RESTORE_OK':'yes','GROUPS_ABSENT':'yes','HP_LOOK_RECORD':'synthetic no-run record',
        'COPY_EVIDENCE':'synthetic typed marker','HP01_DATES_RECORD':'synthetic date census',
        'ISSUED_EPOCH':now-100,'KIT_ISSUED_EPOCH':now-1000,'WATCH_UNTIL_EPOCH':now+1000,
        'QUAL_CLOSE_EPOCH':now-2000,'LATEST_CLOSE_EPOCH':now-1200,'PRIOR_CLOSE_EPOCH':now-2000,
        'NEXT_COUNTED_EPOCH':now+protected,'QUAL_DATE':item['date'],'QUAL_CLEAN':'yes','QUAL_RECORD':'synthetic qualification',
        'HP01_T0_DATES':'2026-11-15','SESSION_READY':'no','COUNTED_READY':'no','F2_READY':'no','F0_ELIGIBLE':'no',
        'F0_REASON':'daily_cap','PRIORITY_RECORD':'synthetic priority','LAST_CLOSE_KIND':'other',
        'LATEST_CLOSE_RECORD':'synthetic census','PREDECESSOR_CLEAN':'yes','PREDECESSOR_RECORD':'synthetic predecessor'}
    for shell in ('bash','zsh'):
        parsed=subprocess.run([shell,'-n'],input='\n'.join(blocks),capture_output=True,text=True)
        assert parsed.returncode==0,parsed.stderr
        def test(label,changes=None,want=False,stamp=now,command='hp_gate'):
            global checks
            obs={**defaults,**(changes or {})}
            lines=['PY='+repr(sys.executable),'PROTECTED_S='+str(protected),gates,f'date() {{ echo {stamp}; }}']
            for k,v in obs.items(): lines.append('unset '+k if v is None else k+'='+__import__('shlex').quote(str(v)))
            lines+=['ARG=$(pick_arg '+str(stamp)+')',command]
            r=subprocess.run([shell],input='\n'.join(lines)+'\n',text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
            assert (r.returncode==0)==want,(item['span'],shell,label,r.stdout,r.stderr)
            checks+=1
        test('complete path',want=True)
        for key in defaults: test('missing '+key,{key:None})
        for changes in ({'HP_LOOK_RUN':'yes'},{'QUAL_DATE':'2026-11-20'},{'QUAL_CLOSE_EPOCH':now+1},
            {'HP01_T0_DATES':item['date']},{'F2_READY':'yes'},{'SESSION_READY':'yes'},{'COUNTED_READY':'yes'},
            {'F0_ELIGIBLE':'yes'},{'F0_REASON':'restore_failed'},{'NEXT_COUNTED_EPOCH':now+protected-1},
            {'LATEST_CLOSE_EPOCH':now-1199},{'ISSUED_EPOCH':now-86400},{'KIT_ISSUED_EPOCH':now-604800},
            {'KIT_ISSUED_EPOCH':now+1},{'WATCH_UNTIL_EPOCH':now},{'WATCH_UNTIL_EPOCH':now+86401},
            {'PREDECESSOR_CLEAN':'no'},{'COPY_TYPED_OK':'no'}): test(str(changes),changes)
        test('kit second before expiry',{'KIT_ISSUED_EPOCH':now-604799},want=True)
        test('campaign interval 300',{'LATEST_CLOSE_EPOCH':now-300,'LAST_CLOSE_KIND':'campaign'},want=True)
        for lo,hi,arg in item['bands']:
            for stamp in (lo,hi): test('band endpoint',want=True,stamp=stamp,command='test "$(pick_arg '+str(stamp)+')" = '+repr(arg))
        for stamp in (item['bands'][0][0]-1,item['bands'][1][1]+1,item['bands'][2][0]-1,item['bands'][-1][1]+1):
            test('outside band',stamp=stamp,command='test "$(pick_arg '+str(stamp)+')" != NONE')
        print('PASS',item['span'],shell)
print(checks,'synthetic hp-02 gate checks PASS')
