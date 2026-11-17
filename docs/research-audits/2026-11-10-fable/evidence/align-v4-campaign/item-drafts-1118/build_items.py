"""Render six unissued qualification items and the same-pin standing-F0 renewal.

python3 -B build_items.py [--dates qual-01=YYYY-MM-DD,qual-02=YYYY-MM-DD,qual-03=YYYY-MM-DD]
Only read-only pinned planners/validators run; no hardware/measurement command.
"""
import argparse
import datetime as dt
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0,str(Path(__file__).resolve().parent/'tools'))
from pinned import HERE, ROOT, PIN, SOURCE, W1, git, pinned, call
TZ=ZoneInfo('America/Los_Angeles')
DEFAULTS={'qual-01':'2026-11-19','qual-02':'2026-11-20','qual-03':'2026-11-21'}
QUEUE_EXPIRY='2026-11-23T00:00:00-08:00'  # <7 days after this Nov16 draft commit; gate verifies authenticated commit.
PREFIX=HERE.relative_to(ROOT).as_posix()

def write_json(path,obj): path.write_text(json.dumps(obj,indent=2)+'\n')
def epoch(date, hms='00:00:00'): return int(dt.datetime.fromisoformat(date+'T'+hms).replace(tzinfo=TZ).timestamp())

def standing():
    main=git('rev-parse','origin/main').decode().strip()
    text=git('show',main+':RUN_STATE.md').decode()
    original=re.search(r'^346\. .*?(?=^345\. )',text,re.S|re.M).group().rstrip()+'\n'
    old='b2e01464d6d4fbf2901ff4d4154df9455104a12a'
    head=git('rev-parse','origin/ops/2026-11-11-w1-presign').decode().strip()
    issued=re.search(r'ISSUED (2026-\d\d-\d\d \d\d:\d\d:\d\d) PST',original).group(1)
    start=dt.datetime.fromisoformat(issued).replace(tzinfo=TZ)+dt.timedelta(days=7)
    end=start+dt.timedelta(days=7)
    renewed=original.replace('346. **','TBD. **',1)
    renewed=renewed.replace('ISSUED '+issued+' PST','ISSUED <LEAD FILLS: actual issue at '+start.strftime('%Y-%m-%d %H:%M:%S')+' PST; if later, re-date the renewal>',1)
    renewed=renewed.replace('This issue replaces the one at `c3f4bacd8`', 'This renewal supersedes item 346 at its expiry; historically item 346 replaced the issue at `c3f4bacd8`')
    renewed=renewed.replace('2026-11-22 11:51:24 PST (epoch 1795377084)',end.strftime('%Y-%m-%d %H:%M:%S PST')+f' (epoch {int(end.timestamp())})')
    renewed=renewed.replace('deadline: 2026-11-22T11:51:24-08:00','deadline: '+end.isoformat())
    renewed=renewed.replace('EXPIRY_EPOCH=1795377084',f'EXPIRY_EPOCH={int(end.timestamp())}')
    assert f'EXPIRY_EPOCH={int(end.timestamp())}' in renewed
    gate=f'''# Renewal starts at item 346's seven-day expiry, never earlier (RL-165 §3 rule 2).
RENEWAL_ISSUED_EPOCH="<LEAD FILLS: actual issue epoch; planned {int(start.timestamp())}>"
RENEWAL_START_EPOCH={int(start.timestamp())}
renewal_gate() {{
  case "$RENEWAL_ISSUED_EPOCH" in ''|*[!0-9]*) echo 'WAIT: renewal not issued'; return 1;; esac
  test "$RENEWAL_ISSUED_EPOCH" = "$RENEWAL_START_EPOCH" \\
    || {{ echo 'VOID: actual renewal issue differs; lead re-dates seven-day window'; return 1; }}
  test "$(date +%s)" -ge "$RENEWAL_START_EPOCH" && test "$(date +%s)" -lt "$EXPIRY_EPOCH" \\
    || {{ echo 'WAIT/EXPIRED: outside renewal validity'; return 1; }}
}}
'''
    renewed=renewed.replace('f0_eligible() {\n','f0_eligible() {\n  renewal_gate || return 1\n',1)
    renewed=renewed.replace('# THE COMPLETE ELIGIBILITY CHECK',gate+'\n# THE COMPLETE ELIGIBILITY CHECK',1)
    note=f'''- **Renewal r2 (DRAFT, RL-165 §3 rule 2).** Item 346 was issued {issued} PST; its seven-day expiry is **{start.strftime('%a %d Nov %Y %H:%M:%S PST')}** (epoch {int(start.timestamp())}). This unissued renewal begins exactly then, with planned expiry {end.strftime('%a %d Nov %Y %H:%M:%S PST')} (epoch {int(end.timestamp())}). The lead must issue at that instant for these fixed bounds; a later actual issue needs a re-dated seven-day window. F0 spacing and daily counts continue across renewals; never reset its ledger. Fetched main `{main}` and W1 head `{head}` checked by builder: {'unchanged at item 346 pin; the 17 hashes, Mac-check and all rules carry as written' if head==old else 'MOVED: do not carry the old pin/hashes/qualification; lead re-pins under rule 2'}. Nothing is issued by this file.
- **Optional hold paragraph (item 374 form; inactive until the lead issues it):** MAGISTRATE: arm NO STANDING-F0 from <LEAD FILLS: hold issue instant> until the lead's RUN_STATE record "offload window closed" or <LEAD FILLS: hold end instant and epoch>, whichever is first. Counted items keep their own gates/windows; a running packer is a STOP at any arm. This does not carry forward item 374's Mon16-only hold, authorize offloading, or change F0's 02:35:00–22:40:00 launch window. Lead-owned hold records must be re-read before Start and Run.

'''
    renewed=renewed.replace('- **What this item is',note+'- **What this item is',1)
    if head!=old:
        renewed=renewed.replace(old,'<LEAD FILLS: W1_LINE_HEAD and fresh pin qualification under RL-165 §3 rule 2>')
        renewed=renewed.replace('b2e01464d','<LEAD FILLS: W1_LINE_SHORT>')
    (HERE/'STANDING-F0-r2.md').write_text(renewed)
    (HERE/'evidence/standing-f0-original.md').write_text(original)
    diff=''.join(difflib.unified_diff(original.splitlines(True),renewed.splitlines(True),fromfile=f'origin/main@{main}:RUN_STATE item 346',tofile='STANDING-F0-r2.md'))
    (HERE/'evidence/standing-f0-r2.diff').write_text(diff)
    return {'source_main':main,'original_issue':issued+' PST','renewal_start':start.isoformat(),'renewal_expiry':end.isoformat(),'w1_head':head,'pin_unchanged':head==old}

def render(dates):
    assert set(dates)==set(DEFAULTS)
    for value in dates.values(): dt.date.fromisoformat(value)
    # Invalid date plans can be rendered for gate refusal tests; normal builder refuses known development dates.
    if len(set(dates.values()))<2 or any('2026-11-14'<=d<='2026-11-18' for d in dates.values()):
        raise SystemExit('REFUSE: RL-172 (a): at least two dates disjoint from development Sat14-Wed18')
    if max(epoch(d) for d in dates.values())>=dt.datetime.fromisoformat(QUEUE_EXPIRY).timestamp():
        raise SystemExit('REFUSE: re-dating exceeds finite queue expiry; lead needs a new queue commit/window')
    for sub in ('kits','queues','evidence'): (HERE/sub).mkdir(exist_ok=True)
    base=HERE.parent/'item-drafts-1115/ITEM-dev05-s01.md'
    old=base.read_text()
    q1=re.search(r'"\$PY" -I -B - "\$OUT" "\$LEGS" <<\'PY\'\nimport json, statistics.*?\nPY',old,re.S).group()
    maintenance=re.search(r'START_UTC=.*?\| sort\n',old,re.S).group()
    maintenance=maintenance.replace('"mobileassetd"','"mobileassetd","bird","cloudd","fileproviderd"')
    template=(HERE/'tools/item-template.md').read_text(); gates=(HERE/'gates.sh').read_text()
    meta={'source':SOURCE,'pin':PIN,'merged_w1':W1,'source_audit':git('rev-parse','HEAD').decode().strip(),
          'queue_scan':git('ls-tree','-r','--name-only',SOURCE,'docs/process/cadence').decode().splitlines(),
          'dates':dates,'queue_expiry':QUEUE_EXPIRY,'items':[],'standing':standing()}
    assert not any('qual' in p.lower() and 'queue' in Path(p).name.lower() for p in meta['queue_scan']),meta['queue_scan']
    with pinned() as repo:
        previous=('dev-05-s02','cl-dev-05',[f'L{i:03d}' for i in range(7,13)],'2747381bf1169471d929d1e91510f7d272ff9cbc973da2c99f11673bea53ca1a','2d347f721552fe03bdd19f113e7bad7a7c24908e')
        for n in range(1,4):
            block=f'qual-{n:02d}'; camp='cl-'+block; kp=f'docs/process/cadence/kits/{camp}.v1.1.json'
            raw=git('show',SOURCE+':'+kp); sha=hashlib.sha256(raw).hexdigest(); kit=json.loads(raw)
            assert kit['frozen']['commit']==PIN and kit['runner']['kind']=='cadence-legs-v1.1'
            local=HERE/'kits'/Path(kp).name; local.write_bytes(raw)
            staged=repo/kp; staged.parent.mkdir(parents=True,exist_ok=True); staged.write_bytes(raw)
            queue={'schema':'joulewise.cadence_queue.v1','queue_id':'cq-'+camp,'expires_at':QUEUE_EXPIRY,'halt':None,'standing_notice':None,'spans':[]}
            for s in range(1,3):
                ids=[x['leg_id'] for x in kit['legs'][(s-1)*6:s*6]]
                queue['spans'].append({'seq':s,'span_id':f'{block}-s{s:02d}','block_id':block,
                    'kit':{'path':kp,'sha256':sha},'legs':ids,'attempt':1,'not_before':dates[block]})
            qp=HERE/'queues'/f'{camp}.queue.json'; write_json(qp,queue)
            qsha=hashlib.sha256(qp.read_bytes()).hexdigest()
            for s, entry in enumerate(queue['spans'],1):
                name=f'qual{n:02d}-s{s:02d}'; span=entry['span_id']; ids=entry['legs']; legs=','.join(ids); t0=epoch(dates[block],'12:00:00' if n==1 else '00:00:00')
                result=call(repo,'scripts/cadence_legs_runner.py','plan','--kit',local,'--legs',legs,'--t0',t0)
                (HERE/'evidence'/f'plan-{name}.json').write_text(result.stdout)
                plan=json.loads(result.stdout); assert plan['batch_windows']==[] and plan['blackout_clear'] and plan['runner_kind']=='cadence-legs-v1.1'
                short=[x for x in kit['legs'] if x['leg_id'] in ids and x['decode_tokens']<4096]
                assert len(short)==1
                config=f'''SPAN={span}; CAMP={camp}; LEGS={legs}
PRED_SPAN={previous[0]}; PRED_CAMP={previous[1]}; PRED_ROSTER={','.join(previous[2])}
PRED_KIT_SHA={previous[3]}; PRED_PIN={previous[4]}
T0_DATE={dates[block]}; WINDOW_START={epoch(dates[block])}; WINDOW_END={epoch(dates[block],'23:59:59')}
QUAL_DATES={','.join(k+'='+v for k,v in dates.items())}'''
                extra=plan['launch_deadline_epoch_s']-plan['t0_epoch_s']; assert extra==plan['worst_case_s']+1950+560
                values=dict(PRED_NOTE=('<LEAD FILLS: confirm dev-05-s02 is latest counted campaign span, or update the complete PRED_* identity and machine-order record>.' if n==s==1 else 'The qualification predecessor chain is fixed; no automatic skip or override.'),ORDINAL='FIRST' if s==1 else 'SECOND',BLOCK=block,SPAN=span,CAMP=camp,LEGS=legs,KIT_SHA=sha,PIN=PIN,FIRST=ids[0],SHORT=f"{short[0]['leg_id']} cap {short[0]['decode_tokens']:,}",EXPECTED=plan['expected_s'],WORST=plan['worst_case_s'],DATE=dates[block],START=epoch(dates[block]),END=epoch(dates[block],'23:59:59'),POINTER_DEADLINE=dt.datetime.fromtimestamp(epoch(dates[block],'23:59:59')+extra+900+3600,TZ).isoformat(),PRED=previous[0],PRED_CAMP=previous[1],PRED_LEGS=','.join(previous[2]),DATES=', '.join(k+'='+v for k,v in dates.items()),QUEUE_PATH=PREFIX+'/queues/'+qp.name,QUEUE_SHA=qsha,CONFIG=config,GATES=gates,MAINTENANCE=maintenance,Q1=q1,DEADLINE_SECONDS=int(extra+900),NEXT=f'Next: `{block}-s02` after its own gates.' if s==1 else ('Next block under its own dated item.' if n<3 else 'All 36 qualification legs collected; the lead owns look readiness.'),HAND_NOTE='After the first span only, RL-172a F1 requires the soak comparison before s02; this draft conservatively waits to issue later spans until that record exists.' if n==s==1 else 'Not issuable before qual-01-s01\'s soak hand-read record (RL-172a F1; conservative issue ordering).')
                text=template
                for key,value in values.items(): text=text.replace('@@'+key+'@@',str(value))
                assert not re.search(r'@@[A-Z_]+@@',text)
                (HERE/f'ITEM-{name}.md').write_text(text)
                meta['items'].append(dict(item=name,span=span,block=block,camp=camp,date=dates[block],legs=ids,kit_path=kp,kit_file=str(local.relative_to(HERE)),kit_sha=sha,seed=kit['seed_law']['master_seed'],queue_file=str(qp.relative_to(HERE)),queue_path=values['QUEUE_PATH'],queue_sha=qsha,predecessor=previous[0],predecessor_camp=previous[1],predecessor_legs=previous[2],predecessor_kit_sha=previous[3],predecessor_pin=previous[4],short_leg=short[0],expected_s=plan['expected_s'],worst_case_s=plan['worst_case_s'],launch_minimum_s=extra))
                previous=(span,camp,ids,sha,PIN)
    write_json(HERE/'items.json',meta)
    print('Rendered six items and STANDING-F0 r2; six pinned plan outputs; queues local to draft folder')
    for i in meta['items']: print(i['span'],i['kit_sha'],','.join(i['legs']),i['expected_s'],i['worst_case_s'],i['short_leg']['leg_id'],i['short_leg']['decode_tokens'])

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--dates')
    args=parser.parse_args(); dates=DEFAULTS.copy()
    if args.dates: dates.update(dict(x.split('=') for x in args.dates.split(',')))
    render(dates)
