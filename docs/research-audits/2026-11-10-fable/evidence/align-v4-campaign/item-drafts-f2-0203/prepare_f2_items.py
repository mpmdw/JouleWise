"""Derive the RL-174 drafts from the committed 1115-style F2 template.

The original 8da5c6d5e template includes 9ef385b9f's recorded-close/copy fix,
read by exact commit rather than from a mutable neighbour.
No item is issued here. Queue b is only generated in a disposable validation
directory; it is not committed before the owning piece-1 hand-read.
"""
import json
from pathlib import Path
import subprocess
import sys
import types

HERE=Path(__file__).resolve().parent
TEMPLATE='9ef385b9f589519cc14a9e6fc8769c8a6ed2304d'
BASE='docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2/'
OLD_SHA='651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b'
OLD_SOURCE='1f683fc634ed6b8722a3976af400920ee1f7dd7d'
QUEUE_EXPIRY='2026-11-23T00:00:00-08:00'

def source(path):
    return subprocess.check_output(['git','show',TEMPLATE+':'+BASE+path],cwd=HERE,text=True)

def main(pin):
    report=json.loads((HERE/'evidence/kit-build.json').read_text())
    maintenance=(HERE.parent/'item-drafts-f2'/'maintenance-check.md').read_text() + '\n'
    allitems=[]
    for index,record in enumerate(report['kits'][:2],2):
        name=record['name']; folder=HERE/name; sha=record['sha256']; dose=record['decode']
        expected=record['plans'][0]['plan']['expected_s']
        pred_camp='f2-inst-01' if index==2 else 'f2-inst-02'
        pred_span='f2-inst-p4' if index==2 else 'f2-inst-02-p4'
        pred_sha=OLD_SHA if index==2 else report['kits'][0]['sha256']
        qa=json.loads(source('queue-a.json'))
        qa['queue_id']='cq-'+name+'-a'; qa['expires_at']=QUEUE_EXPIRY
        qa['spans'][0].update(span_id=name+'-p1',block_id=name,not_before='2026-11-19')
        qa['spans'][0]['kit']={'path':name+'/'+name+'.v1.1.json','sha256':sha}
        (folder/'queue-a.json').write_text(json.dumps(qa,indent=1)+'\n')
        gates=source('gates.sh').replace('1795325340','1795420800')
        # F2 uses a genuinely separate root, included in the latest-close census.
        gates=gates.replace('root, camp, span, roster, kit_sha = sys.argv[1:]; roster = roster.split(\',\')',
                            "root, camp, span, roster, kit_sha = sys.argv[1:]; roster = roster.split(',')")
        gates=gates.replace('pred_gate() {\n', 'pred_gate() {\n  pred_root=/Users/edr/f2-out\n  if test "$PRED_CAMP" = f2-inst-01; then pred_root=/Users/edr/campaign-out; fi\n')
        gates=gates.replace('- /Users/edr/campaign-out "$PRED_CAMP"', '- "$pred_root" "$PRED_CAMP"')
        gates=gates.replace('- /Users/edr/campaign-out /Users/edr/code/jw-wt',
                            '- /Users/edr/campaign-out /Users/edr/code/jw-wt /Users/edr/f2-out')
        gates=gates.replace('copy_gate || return 1', 'copy_gate || return 1\n  test "${COPY_TYPED_OK:-}" = yes && test -n "${COPY_EVIDENCE:-}" || { echo "STOP: typed verified copy evidence required (RL-174 A.12)"; return 1; }')
        extra='''rl174_gate() {
  for proof in "INST01_HAND_READ:${INST01_HAND_READ:-}" "KIT_DELTA_OK:${KIT_DELTA_OK:-}" "HOST_STATE_RECORDED:${HOST_STATE_RECORDED:-}"; do
    case "$proof" in INST01_HAND_READ:PASS|KIT_DELTA_OK:yes|HOST_STATE_RECORDED:yes) ;; *) echo "WAIT: RL-174 B/C prerequisite $proof"; return 1;; esac
  done
  case "${KIT_ISSUED_EPOCH:-}" in ''|*[!0-9]*) echo 'WAIT: lead kit issue time required'; return 1;; esac
  now=$(date +%s)
  test "$now" -ge "$KIT_ISSUED_EPOCH" && test "$now" -lt $((KIT_ISSUED_EPOCH + 604800)) || { echo 'VOID: seven days after kit issue'; return 1; }
}
'''
        gates=gates.replace('all_gates() {',extra+'all_gates() {')
        gates=gates.replace('expiry_gate && watch_gate','rl174_gate && expiry_gate && watch_gate')
        (folder/'gates.sh').write_text(gates)
        code=source('build_items.py')
        code=code.replace("EVIDENCE = HERE / 'evidence/fix-2026-11-16'", "EVIDENCE = HERE / 'evidence'")
        code=code.replace('512',str(dose))
        code=code.replace("SOURCE = '"+OLD_SOURCE+"'", "SOURCE = 'RL174B'")
        code=code.replace("SHA = '"+OLD_SHA+"'", "SHA = '"+sha+"'")
        code=code.replace("kit_bytes = subprocess.check_output(['git', 'show', f'{SOURCE}:{KIT_PATH}'], cwd=pin_repo)",
                          "kit_bytes = (HERE / 'f2-inst-01.v1.1.json').read_bytes()")
        code=code.replace("    (HERE / 'queue-a.json').write_text(git('show', f'{SOURCE}:{QUEUE_PATH}'))\n",'')
        start=code.index('    specs = ['); end=code.index('    records = []',start)
        specs=([(1,20,'@PRED_CAMP@','@PRED_SPAN@',[10,11,12],'19:56:17'),
                (2,21,name,name+'-p1',[1,2,3],'17:55:00'),
                (3,21,name,name+'-p2',[4,5,6],'20:19:02'),
                (4,21,name,name+'-p3',[7,8,9],'22:43:04')] if index==2 else
               [(1,22,'@PRED_CAMP@','@PRED_SPAN@',[10,11,12],'13:15:00'),
                (2,22,name,name+'-p1',[1,2,3],'15:39:02'),
                (3,22,name,name+'-p2',[4,5,6],'18:03:04'),
                (4,22,name,name+'-p3',[7,8,9],'20:27:06')])
        code=code[:start]+'    specs = '+repr(specs)+'\n'+code[end:]
        code=code.replace("pred_sha = '0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b' if n == 1 else SHA",
                          "pred_sha = '"+pred_sha+"' if n == 1 else SHA")
        code=code.replace('f2-inst-01',name).replace('f2-inst-p',name+'-p')
        code=code.replace('@PRED_CAMP@',pred_camp).replace('@PRED_SPAN@',pred_span)
        code=code.replace('7442',str(expected)).replace('7,442',f'{expected:,}')
        code=code.replace('2026-11-21T21:29:00-08:00',QUEUE_EXPIRY)
        code=code.replace('QUEUE_SHA=ca61c3bc09d8a594a60ec058b86d378012a165b44334f4309b4cd7546e842892',
                          'QUEUE_SHA='+__import__('hashlib').sha256((folder/'queue-a.json').read_bytes()).hexdigest())
        code=code.replace('/Users/edr/campaign-out/'+name+'/', '/Users/edr/f2-out/'+name+'/')
        # Source/copy was deliberately removed: this module consumes built data.
        namespace={'__file__':str(folder/'build_items.py'),'__name__':'template'}
        (folder/'evidence').mkdir(exist_ok=True)
        exec(compile(code,str(folder/'template.py'),'exec'),namespace)
        namespace['render'](pin)
        items=json.loads((folder/'items.json').read_text())
        for item in items:
            item['kit_name']=name; item['kit_sha']=sha; item['decode']=dose
            item['predecessor_sha']=pred_sha if item['piece']==1 else sha
            path=folder/('ITEM-'+item['item']+'.md')
            text=path.read_text()
            check=text.index('**Check.**')
            first_block=text.index('```sh\n',check)
            text=text[:first_block]+maintenance+text[first_block:]
            text=text.replace('evidence/fix-2026-11-16/verify-','evidence/verify-')
            text=text.replace('stage_mbp_span.sh','python3 -B ../stage_mbp_span.py --commit <LEAD FILLS committed draft source> --admission <LEAD FILLS administrative admission JSON>')
            text=text.replace('/queues/'+name+'.v1.1.queue-a.json','/queues/'+name+'-queue-a.json')
            # The template's SOURCE labels are not purported commit ids.
            text=text.replace('The committed queue a at `1f683fc6` contains this piece only.',
                'The drafted queue a in this folder contains this piece only. The lead records its actual commit and SHA before staging.')
            text=text.replace('**Admission and authority (RL-169; RL-169a).**',
                '**Admission and authority (RL-174 B.2; RL-169; RL-169a).**')
            text=text.replace('**Exact ladder.**','**Exact ladder.** RL-174 B replaces the order with READY v4, counted work, F0, F2 inst-01 then inst-02 then inst-03, hp-02, DESIGN_QUEUE_LOW. hp-02 does not precede F2. The inherited HP_READY observation refers only to higher-priority counted hp-01, if any. ')
            text=text.replace('**Quiet and host event.**','**Quiet and host event.** RL-174 C settles the host event: no restart/visit is required. Print the four host lines at each arm: spotlightknowledged/updater present or absent, corespotlightd present, indexing / off, Time Machine destination none. From freeze 2 through qual-03 close no hygiene setting changes; an unplanned restart is recorded and does not hold the arm. HOST_STATE_RECORDED means this record, not a new restart gate. ')
            text=text.replace('host-event disposition/readback,', 'host-state print,')
            text=text.replace('service-stop readback or restart disposition is lead-owned, last point before freeze 2.', 'the four host lines are printed; RL-174 C has disposed the planned host event.')
            text=text.replace('**Blinding.**','**Blinding.** RL-174 B.2: the frozen lm-inst-01 manifest lists all THREE kits by identity/hash before ANY F2 energy is opened, and prints per kit. ')
            text=text.replace('**After (lead).**', '**After (lead).** Kit expiry is seven days after the lead\'s kit issue, independently of the 24-hour item expiry. Queue expiry Nov23 00:00 is a conservative upper bound; never issue before Nov16. Queue b is still uncommitted until THIS kit\'s first-piece PASS. The unchanged kit title/inclusion prose names inst-01/512/old expiry; this item and RL-174 B supersede those historical literals only. ')
            focused='''export TMPDIR="$(mktemp -d /tmp/jw-f2-preflight.XXXXXX)" JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=.:tests
for module in tests.cadence.test_kit_v11 tests.cadence.test_span_reference tests.cadence.test_legs_runner tests.cadence.test_kit tests.cadence.test_stops_desk tests.cadence.test_runner_guards tests.cadence.test_launch_cadence_span tests.align.test_r1_smoke_launcher; do
  python3.13 -B -m unittest "$module" || exit 1
done
'''
            text=text.replace('"$PY" -B scripts/cadence_queue.py validate-kit',focused+'"$PY" -B scripts/cadence_queue.py validate-kit')
            text=text.replace('one executing delta', 'one executing delta')
            # Each item contains the exact gates and is independently runnable.
            # The new constraints are in all_gates and are consequently checked twice.
            path.write_text(text)
        (folder/'items.json').write_text(json.dumps(items,indent=2)+'\n')
        allitems += [{**item,'folder':name} for item in items]
        test=source('tests/test_rl173_gates.py')
        test=test.replace('1795325340','1795420800').replace('1795325300','1795420790').replace('1795325400','1795420900')
        test=test.replace("'651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b'",repr(sha))
        test=test.replace("'0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b'",repr(pred_sha))
        test=test.replace("'f2-inst-01'",repr(name))
        test=test.replace("root=base/'campaign-out'", "root=base/'f2-out'")
        test=test.replace("gates = gates.replace('/Users/edr/campaign-out',str(root))", "gates = gates.replace('/Users/edr/f2-out',str(root)).replace('/Users/edr/campaign-out',str(root))")
        # The same synthetic root stands for both source roots; de-duplicate its census argument.
        test=test.replace("# close_gate's path discriminator", "gates = gates.replace(str(root)+' '+str(wt)+' '+str(root),str(root)+' '+str(wt))\n        # close_gate's path discriminator")
        test=test.replace("QUEUE_AUTHORIZED='yes',COPY_KEY_SAFE='yes'", "QUEUE_AUTHORIZED='yes',COPY_KEY_SAFE='yes',COPY_TYPED_OK='yes',COPY_EVIDENCE='synthetic typed receipt',INST01_HAND_READ='PASS',KIT_DELTA_OK='yes',HOST_STATE_RECORDED='yes',KIT_ISSUED_EPOCH=now-3600")
        test=test.replace("        check('clean complete path')", """        check('clean complete path')
        for key in ('INST01_HAND_READ','KIT_DELTA_OK','HOST_STATE_RECORDED','KIT_ISSUED_EPOCH','COPY_TYPED_OK','COPY_EVIDENCE'):
            check('RL174 missing '+key,overrides={key:None},want=False)
        check('RL174 kit exactly seven days',overrides={'KIT_ISSUED_EPOCH':now-604800},want=False)
        check('RL174 kit one second under seven days',overrides={'KIT_ISSUED_EPOCH':now-604799})
        check('RL174 kit future issue',overrides={'KIT_ISSUED_EPOCH':now+1},want=False)
""")
        (folder/'tests').mkdir(exist_ok=True)
        (folder/'tests/test_gates.py').write_text(test)
    (HERE/'items.json').write_text(json.dumps(allitems,indent=2)+'\n')
    print('Rendered eight F2 drafts and gate tests; NOT ISSUED; queue b absent')

if __name__=='__main__': main(Path(sys.argv[1]).resolve())
