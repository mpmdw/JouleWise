#!/usr/bin/env python3
"""Offline fixture checks. Real render-only installer and verify-only night supervisor; no collection."""
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
import shutil
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
sys.path.insert(0,str(REPO))
from joulewise.night_agent_install import Refused, evidence_probe_bindings, probe_label, validate_probe_receipt
from joulewise.night_gate import chain_literal
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


def fixture_directory():
    # EvidenceFixture avoids accidental matches in the agent-census path filter.
    while True:
        temp=tempfile.TemporaryDirectory(prefix='qpe01-arm-fixture-',dir='/tmp')
        if not any(token in temp.name.lower() for token in ('codex','claude','t3')):
            return temp
        temp.cleanup()


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
    arm_env=(HERE/'arm-env.zsh').read_text()
    arm_head=re.search(r"^export H='([0-9a-f]{40})'",arm_env,re.M).group(1)
    subprocess.run(['git','-C',str(REPO),'merge-base','--is-ancestor',arm_head,'origin/main'],check=True)
    print('PASS arm-env H is an ancestor of local origin/main (no fetch)')
    head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
    # Every mutation below stays in this explicitly requested /tmp fixture.
    with fixture_directory() as td:
        temp=Path(td).resolve()
        assert temp.is_relative_to(Path('/tmp').resolve())
        repo=temp/'measurement'
        subprocess.run(['git','-c','advice.detachedHead=false','clone','--quiet','--no-local','--depth','1',str(REPO),str(repo)],check=True)
        assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==head
        (repo/'.venv/bin').mkdir(parents=True)
        python=repo/'.venv/bin/python'; python.symlink_to(sys.executable)
        # Installer requires a courier executable; render-only must never call it.
        bin_dir=temp/'bin'; bin_dir.mkdir()
        courier=bin_dir/'claude'; courier.write_text('#!/bin/sh\nexit 99\n'); courier.chmod(0o755)
        print('PASS fixture checkout HEAD equals fixture H (worktree HEAD)')
        t0=(int(time.time())//60+60)*60
        template=re.sub(r"^export NIGHT_DATE=.*$","export NIGHT_DATE='__YYYYMMDD__'",arm_env,flags=re.M)
        template=re.sub(r"^export T0_EPOCH_S=.*$","export T0_EPOCH_S='__T0_EPOCH_S__'",template,flags=re.M)
        env_text=template.replace('__YYYYMMDD__',time.strftime('%Y%m%d',time.localtime(t0))).replace('__T0_EPOCH_S__',str(t0))
        env_text=env_text.replace('/Users/edr/',str(temp)+'/')
        env_file=temp/'arm-env.zsh'; env_file.write_text(env_text)
        shell=subprocess.run(['/bin/zsh','-c','source "$1"; print -- "$PLAN_ID $INSTALL_CLOSE_EPOCH_S $REQUEST_EPOCH_S $TERM_EPOCH_S $KILL_EPOCH_S $ACQUISITION_END_EPOCH_S $COURIER_EPOCH_S $DEADMAN_EPOCH_S"','fixture',str(env_file)],capture_output=True,text=True,check=True)
        assert list(map(int,shell.stdout.split()[1:]))==[t0-600,t0-480,t0-360,t0-300,t0+9000,t0+9300,t0+12900]
        print('PASS filled environment: local date, minute alignment, all seven boundaries')
        bad_env=temp/'unfilled-env.zsh'; bad_env.write_text(template.replace('/Users/edr/',str(temp)+'/'))
        rejected=subprocess.run(['/bin/zsh',str(bad_env)],capture_output=True,text=True)
        assert rejected.returncode==3
        print('PASS unfilled environment refuses with exit 3')
        root=temp/'custody'; stage=temp/'stage'; attempt=stage/'arm-attempts'/'000001'
        root.mkdir(); attempt.mkdir(parents=True)
        e=dict(MEASUREMENT_ROOT=str(repo),NIGHT_ROOT=str(root),STAGE=str(stage),
               STAGED_PLAN=str(stage/'night_plan.json'),PLAN=str(root/'night_plan.json'),
               PLAN_ID='qpe01-pilot-n1-fixture',H=head,
               T0_EPOCH_S=str(t0),INSTALL_CLOSE_EPOCH_S=str(t0-600),DEADMAN_EPOCH_S=str(t0+12900),
               ARM_ATTEMPT='1',ATTEMPT_DIR=str(attempt),PY=str(python),PYTHONDONTWRITEBYTECODE='1',
               PATH=str(bin_dir)+os.pathsep+os.environ.get('PATH',''))
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
            print('PASS generated wrapper zsh -n (execution deferred to verify-only probe)')
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
            rendered=stage/'rendered-agents'
            sealed={path:path.read_bytes() for path in (wrapper,Path(p.chain_sha256_path),
                    root/'evidence_manifest.json',Path(str(wrapper)+'.chain-source.sha256'))}

            def render(plan_path,render_dir):
                assert not render_dir.exists()
                result=subprocess.run([str(repo/'scripts/install_night_agent.sh'),
                    '--plan',str(plan_path),'--python',e['PY'],'--render-only',str(render_dir)],
                    cwd=repo,capture_output=True,text=True)
                if result.returncode:
                    print(result.stdout,end='',flush=True)
                    print(result.stderr,end='',file=sys.stderr,flush=True)
                result.check_returncode()
                records=[json.loads(line) for line in result.stdout.splitlines() if line.startswith('{')]
                record=next(record for record in records if 'payload_kind' in record)
                assert record['payload_kind']=='quiet_predicate_evidence'
                print(json.dumps(record,sort_keys=True))
                assert {path.name for path in render_dir.glob('*.plist')}=={
                    'com.joulewise.night.plist','com.joulewise.night.deadman.plist',
                    probe_label(p.plan_id)+'.plist'}
                assert {path:path.read_bytes() for path in sealed}==sealed
                assert plan_path.read_bytes()==raw
                assert list((root/'night').iterdir())==[]
                return {path.name:path.read_bytes() for path in render_dir.glob('*.plist')}

            assert not Path(e['PLAN']).exists()
            staged_plists=render(staged,stage/'staged-rendered-agents')
            assert not Path(e['PLAN']).exists()
            print('PASS real installer render-only on STAGED plan: evidence payload JSON and three plists')
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
            published_plists=render(published,rendered)
            for label in ('com.joulewise.night','com.joulewise.night.deadman'):
                assert staged_plists[label+'.plist']==published_plists[label+'.plist']
            print('PASS real installer render-only on PUBLISHED plan: three plists; night/dead-man byte-identical')
            bindings=evidence_probe_bindings(p,published,e['PY'])
            assert bindings['plan_sha256']==hashlib.sha256(raw).hexdigest()
            must_refuse(lambda: evidence_probe_bindings(p,staged,e['PY']),ValueError,'evidence plan not at its published path')
            print('PASS fixture publication preserves bytes; real probe bindings accept the published plan and refuse the staged path')
            for command in ('preflight','schedule'):
                subprocess.run([e['PY'],'-B',str(repo/'scripts/run_night.py'),command,
                                '--plan',str(published)],cwd=repo,check=True,capture_output=True,text=True)
            print('PASS real run_night.py preflight and schedule on published fixture')
            receipt_path=root/'night_probe_receipt.json'
            # Same sole supervisor seam as test_evidence_arm_sequence.py: census
            # is fixture-only; real stop/kill/reap logic derives cleanup_proven.
            probe_code="""from pathlib import Path
import sys
from unittest.mock import patch
from scripts import run_night
with patch.object(run_night, '_probe_group_absent', return_value=True):
    raise SystemExit(run_night.probe_night(Path(sys.argv[1]), Path(sys.argv[2]), timeout_s=30))
"""
            probe_env=dict(os.environ,JOULEWISE_LAUNCHD_LABEL=probe_label(p.plan_id))
            with subprocess.Popen([e['PY'],'-B','-c',probe_code,str(published),str(receipt_path)],
                    cwd=repo,env=probe_env,stdout=subprocess.PIPE,stderr=subprocess.PIPE) as supervisor:
                stdout,stderr=supervisor.communicate(timeout=40)
            assert supervisor.returncode==0,(stdout,stderr,receipt_path.read_text())
            receipt=json.loads(receipt_path.read_text())
            assert receipt['driver_pid']==supervisor.pid
            assert receipt['chain_pgid']>0 and receipt['chain_pgid']!=receipt['driver_pid']
            identity=json.loads(receipt_path.with_name(receipt_path.name+'.process.json').read_text())
            assert identity['chain_pgid']==receipt['chain_pgid']
            assert receipt['verify_only'] and receipt['cleanup_proven']
            assert receipt['collect_started'] is False and receipt['load_started'] is False
            assert validate_probe_receipt(SimpleNamespace(plan=p,plan_path=published,python=e['PY']))==receipt
            with contextlib.redirect_stdout(io.StringIO()):
                checks.receipt(published)
            print('PASS real probe_night supervisor, verify-only chain, process identity and validate_probe_receipt')
            now=time.time()
            for field,bad in [('schema','joulewise.night_probe_receipt.v1'),('verify_only',False),
                              ('collect_started',True),('load_started',True),('cleanup_proven',False),
                              ('finished_epoch_s',now-21601)]:
                receipt_path.write_text(json.dumps({**receipt,field:bad}))
                must_refuse(lambda: checks.receipt(published),Refused,'')
            receipt_path.write_text(json.dumps(receipt))
            print('PASS real receipt validator: schema, verify-only, no collect/load, cleanup, <6 h freshness')
            assert {path:path.read_bytes() for path in sealed}==sealed
            assert published.read_bytes()==raw
            home=temp/'home'; launch_dir=home/'Library'/'LaunchAgents'; launch_dir.mkdir(parents=True)
            values={}
            for source in rendered.glob('*.plist'):
                shutil.copyfile(source,launch_dir/source.name)
                values[source.stem]=plistlib.loads(source.read_bytes())
            # Only launchctl list is simulated; plist bytes come from the installer.
            real_check_output=subprocess.check_output
            def loaded_labels(argv,*args,**kwargs):
                if argv==['launchctl','list']:
                    return '- 0 com.joulewise.night\n- 0 com.joulewise.night.deadman\n'
                return real_check_output(argv,*args,**kwargs)
            with patch('pathlib.Path.home',return_value=home), patch('subprocess.check_output',side_effect=loaded_labels):
                execute(blocks('step5-verify-and-exit.zsh')[0])
                for field,bad in [('StartCalendarInterval',{}),('ProgramArguments',['/wrong/python',str(published)]),('WorkingDirectory','/wrong/root'),('RunAtLoad',True)]:
                    value={**values['com.joulewise.night'],field:bad}
                    (launch_dir/'com.joulewise.night.plist').write_bytes(plistlib.dumps(value))
                    must_refuse(lambda: execute(blocks('step5-verify-and-exit.zsh')[0]),AssertionError,'')
            print('PASS actual step5 assertions on installer-produced plists; wrong schedule/argv/root/RunAtLoad refuse')
    print('DRY CHECK COMPLETE')


if __name__=='__main__':
    os.environ['TZ']='America/Los_Angeles'; time.tzset()
    main()
