#!/usr/bin/env python3
"""Offline fixture checks. Never execute a bench shell step or a night payload."""
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import plistlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
sys.path.insert(0,str(REPO))
from joulewise.night_agent_install import Refused, evidence_probe_bindings, probe_label
from joulewise.night_gate import NightPlan, chain_literal
from scripts.gen_evidence_night import GenerationRefusal, generate


def blocks(name):
    text=(HERE/name).read_text()
    return [m.group(2) for m in re.finditer(r"<<'(PY|PYTHON)'[^\n]*\n(.*?)\n\1(?=\n|$)",text,re.S)]


def execute(code):
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(code,'<fixture heredoc>','exec'),{})


def must_refuse(call, error, match):
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            call()
    except error as exc:
        assert match in str(exc),repr(exc)
    else:
        raise AssertionError('expected refusal: '+match)


def main():
    for script in sorted(HERE.glob('*.zsh')):
        subprocess.run(['/bin/zsh','-n',str(script)],check=True)
        print('PASS zsh -n '+script.name)
    count=0
    for script in sorted(HERE.glob('*.zsh')):
        for code in blocks(script.name):
            ast.parse(code); count+=1
    for script in sorted(HERE.glob('*.py')):
        ast.parse(script.read_text())
    print(f'PASS Python syntax: {count} shell heredocs and 2 helper scripts')
    # Every mutation below stays in this explicitly requested /tmp fixture.
    with tempfile.TemporaryDirectory(prefix='qpe01-arm-fixture-',dir='/tmp') as td:
        temp=Path(td).resolve()
        assert temp.is_relative_to(Path('/tmp').resolve())
        t0=(int(time.time())//60+60)*60
        env_text=(HERE/'arm-env.zsh').read_text().replace('__YYYYMMDD__',time.strftime('%Y%m%d',time.localtime(t0))).replace('__T0_EPOCH_S__',str(t0))
        env_text=env_text.replace('/Users/edr/',str(temp)+'/')
        env_file=temp/'arm-env.zsh'; env_file.write_text(env_text)
        shell=subprocess.run(['/bin/zsh','-c','source "$1"; print -- "$PLAN_ID $INSTALL_CLOSE_EPOCH_S $REQUEST_EPOCH_S $TERM_EPOCH_S $KILL_EPOCH_S $ACQUISITION_END_EPOCH_S $COURIER_EPOCH_S $DEADMAN_EPOCH_S"','fixture',str(env_file)],capture_output=True,text=True,check=True)
        assert list(map(int,shell.stdout.split()[1:]))==[t0-600,t0-480,t0-360,t0-300,t0+9000,t0+9300,t0+12900]
        print('PASS filled environment: local date, minute alignment, all seven boundaries')
        bad_env=temp/'unfilled-env.zsh'; bad_env.write_text((HERE/'arm-env.zsh').read_text().replace('/Users/edr/',str(temp)+'/'))
        rejected=subprocess.run(['/bin/zsh',str(bad_env)],capture_output=True,text=True)
        assert rejected.returncode==3
        print('PASS unfilled environment refuses with exit 3')
        root=temp/'custody'; stage=temp/'stage'; attempt=stage/'arm-attempts'/'000001'
        root.mkdir(); attempt.mkdir(parents=True)
        e=dict(MEASUREMENT_ROOT=str(REPO),NIGHT_ROOT=str(root),STAGE=str(stage),
               STAGED_PLAN=str(stage/'night_plan.json'),PLAN=str(root/'night_plan.json'),
               PLAN_ID='qpe01-pilot-n1-fixture',H=re.search(r"^export H='([0-9a-f]{40})'",(HERE/'arm-env.zsh').read_text(),re.M).group(1),
               T0_EPOCH_S=str(t0),INSTALL_CLOSE_EPOCH_S=str(t0-600),DEADMAN_EPOCH_S=str(t0+12900),
               ARM_ATTEMPT='1',ATTEMPT_DIR=str(attempt),PY=sys.executable)
        with patch.dict(os.environ,e):
            spec=importlib.util.spec_from_file_location('arm_evidence_checks',HERE/'evidence-checks.py')
            checks=importlib.util.module_from_spec(spec); spec.loader.exec_module(checks)
            execute(blocks('step2-author.zsh')[0])
            staged=Path(e['STAGED_PLAN']); raw=staged.read_bytes()
            generate(staged)
            with contextlib.redirect_stdout(io.StringIO()):
                p=checks.candidate(staged)
            print('PASS actual authoring heredoc, generator, manifest, source-at-H and registration checks')
            subprocess.run(['/bin/zsh','-n',p.chain_path],check=True)
            print('PASS generated wrapper zsh -n (wrapper never executed)')
            must_refuse(lambda: generate(staged),GenerationRefusal,'chain already exists')
            print('PASS second render refuses existing chain')
            # PR #365 (EVIDENCE-PLAN-PATH-BINDING-01): the wrapper now seals the
            # PUBLISHED plan path, so the publication-safe guard must accept.
            with contextlib.redirect_stdout(io.StringIO()):
                checks.candidate(staged,True)
            guard=subprocess.run([sys.executable,'-B',str(HERE/'evidence-checks.py'),'candidate','--plan',str(staged),'--publication-safe'],capture_output=True,text=True)
            assert guard.returncode==0, guard.stderr
            print('PASS publication-safe guard accepts the staged wrapper (binds the published plan path)')
            wrapper=Path(p.chain_path); saved=wrapper.read_bytes(); wrapper.write_bytes(saved+b'# drift\n')
            must_refuse(lambda: checks.candidate(staged),ValueError,'wrapper SHA-256 equals sidecar')
            wrapper.write_bytes(saved)
            print('PASS wrapper byte drift refuses')
            (attempt/'plan.json').write_bytes(raw); (attempt/'attempts.json').write_text('[]\n')
            with contextlib.redirect_stdout(io.StringIO()) as body:
                exec(compile(blocks('step3-notice.zsh')[0],'<notice body>','exec'),{})
            text=body.getvalue(); (attempt/'notice-body.txt').write_text(text)
            for token in ('EVIDENCE','7,800','480-second','No-objection window','NO','no cutoff qualifies'):
                assert token in text,token
            execute(blocks('step3-notice.zsh')[1])
            notice_path=attempt/'notice.json'; notice=json.loads(notice_path.read_text())
            assert notice['accepted'] is False and notice['veto_clear'] is False
            print('PASS actual notice heredocs: evidence body, byte binding, unaccepted template')
            publication=blocks('step4-publish-install.zsh')[1]
            must_refuse(lambda: execute(publication),AssertionError,'unfilled notice template')
            notice.update(message_id='fixture-message',thread_id='fixture-thread',sent_epoch_s=time.time()-1,
                          accepted=True,prerequisites_clear=True,veto_clear=True)
            notice['latest_no_epoch_s']=time.time()-2; notice_path.write_text(json.dumps(notice))
            must_refuse(lambda: execute(publication),SystemExit,'3')
            assert staged.read_bytes()==raw and not Path(e['PLAN']).exists()
            notice['latest_no_epoch_s']=None; notice_path.write_text(json.dumps(notice))
            (attempt/'plan.json').write_bytes(raw+b' ')
            must_refuse(lambda: execute(publication),SystemExit,'3')
            (attempt/'plan.json').write_bytes(raw)
            print('PASS publication heredoc refuses unaccepted notice, owner NO and changed saved bytes')
            # os.replace in the fixture: after PR #365 the wrapper literal IS the
            # published path, so the real probe bindings accept the published plan.
            execute(publication)
            published=Path(e['PLAN'])
            assert published.read_bytes()==raw and not staged.exists()
            assert Path(chain_literal(wrapper.read_text(),'EVIDENCE_PLAN_PATH'))==published and published.exists()
            if (REPO/'.venv/bin/python').exists():
                bindings=evidence_probe_bindings(p,published,sys.executable)
                assert bindings['plan_sha256']==hashlib.sha256(raw).hexdigest()
                must_refuse(lambda: evidence_probe_bindings(p,staged,sys.executable),ValueError,'evidence plan not at its published path')
                print('PASS fixture publication preserves bytes; real probe bindings accept the published plan and refuse the staged path')
            else:
                # A development worktree has no measurement venv; the real clone does,
                # and step 4's verify-only probe exercises the real bindings there.
                print('PASS fixture publication preserves bytes; wrapper literal == published plan (real bindings need the clone venv: exercised at step 4)')
            # Receipt validation with synthetic bindings only; no launchd probe or chain execution.
            now=time.time(); bindings={'manifest_sha256':'f'*64}
            receipt=dict(schema='joulewise.night_evidence_probe_receipt.v1',outcome='ok',refusal_code=None,
                         started_epoch_s=now-2,finished_epoch_s=now-1,launchd_label=probe_label(p.plan_id),
                         verify_only=True,collect_started=False,load_started=False,cleanup_proven=True,
                         verify_stdout=['VERIFY_ONLY_OK manifest='+bindings['manifest_sha256']],**bindings)
            receipt_path=root/'night_probe_receipt.json'
            with patch('joulewise.night_agent_install.evidence_probe_bindings',return_value=bindings):
                receipt_path.write_text(json.dumps(receipt))
                with contextlib.redirect_stdout(io.StringIO()):
                    checks.receipt(published)
                for field,bad in [('schema','joulewise.night_probe_receipt.v1'),('verify_only',False),
                                  ('collect_started',True),('load_started',True),('cleanup_proven',False),
                                  ('finished_epoch_s',now-21601)]:
                    receipt_path.write_text(json.dumps({**receipt,field:bad}))
                    must_refuse(lambda: checks.receipt(published),Refused,'')
            print('PASS synthetic receipt validator: schema, verify-only, no collect/load, cleanup, <6 h freshness')
            from scripts.run_night import schedule
            home=temp/'home'; launch_dir=home/'Library'/'LaunchAgents'; launch_dir.mkdir(parents=True)
            rendered=stage/'rendered-agents'; rendered.mkdir()
            sched=schedule(p)
            values={}
            for label,key in [('com.joulewise.night','night_calendar'),('com.joulewise.night.deadman','deadman_calendar')]:
                value={'Label':label,'StartCalendarInterval':sched[key],
                       'ProgramArguments':[e['PY'],str(REPO/'scripts/run_night.py'),'--plan',str(published)],
                       'WorkingDirectory':str(REPO),'RunAtLoad':False}
                values[label]=value
                for directory in (launch_dir,rendered):
                    (directory/(label+'.plist')).write_bytes(plistlib.dumps(value))
            with patch('pathlib.Path.home',return_value=home), patch('subprocess.check_output',return_value='- 0 com.joulewise.night\n- 0 com.joulewise.night.deadman\n'):
                execute(blocks('step5-verify-and-exit.zsh')[0])
                for field,bad in [('StartCalendarInterval',{}),('ProgramArguments',['/wrong/python',str(published)]),('WorkingDirectory','/wrong/root'),('RunAtLoad',True)]:
                    value={**values['com.joulewise.night'],field:bad}
                    (launch_dir/'com.joulewise.night.plist').write_bytes(plistlib.dumps(value))
                    must_refuse(lambda: execute(blocks('step5-verify-and-exit.zsh')[0]),AssertionError,'')
            print('PASS actual step5 assertions on synthetic plists; wrong schedule/argv/root/RunAtLoad refuse')
    print('DRY CHECK COMPLETE: fixture checks passed; staging/publication binding holds')


if __name__=='__main__':
    os.environ['TZ']='America/Los_Angeles'; time.tzset()
    main()
