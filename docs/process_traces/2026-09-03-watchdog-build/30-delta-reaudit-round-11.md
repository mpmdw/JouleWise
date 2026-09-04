```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Round 11 cures the reaper process-group defect, but step 0 still accepts an early digest mismatch because its test supplies undocumented zsh -e semantics.",
  "workspace": {
    "base_requested": "9b1424f5b4a895cfbb9d9353c4d336e679d5dd1b",
    "base_mode": "exact",
    "head_start": "8b2e11c824a3af265d6f09fb69eddce229671fa1",
    "head_end": "8b2e11c824a3af265d6f09fb69eddce229671fa1",
    "upstream_end": "8b2e11c824a3af265d6f09fb69eddce229671fa1",
    "branch": "feat/2026-09-03-magistrate-watchdog"
  },
  "pathspec": [
    "docs/process_traces/2026-09-03-watchdog-build/30-delta-reaudit-round-11.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "line": "RESIDUAL",
    "clauses": {
      "F1": "CURED",
      "F2": "RESIDUAL",
      "D-172": "COMPLIANT_VACUOUS_NO_GOVERNED_CHANGED_LINES"
    },
    "same_signature": "YES: the new digest test is green only because its harness adds zsh -e; the documented Terminal-hosted interactive block lacks that behavior and exits 0 after an early mismatch.",
    "findings": [
      {
        "id": "N1",
        "severity": "blocker",
        "title": "Step 0 continues after an early digest mismatch and returns success",
        "paths": [
          "docs/process/MAGISTRATE_WATCHDOG.md",
          "tests/test_magistrate_watchdog.py"
        ]
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_install_magistrate_watchdog tests.test_magistrate_watchdog_cli",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 74 tests in 8.422s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 74 tests in [0-9.]+s[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c \"$(sed -n '/^# V2-BEGIN$/,/^# V2-END$/p' docs/process_traces/2026-09-03-watchdog-build/30-delta-reaudit-round-11.md)\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["setsid-leader detached=True live_is_pid=True ladder=True detachment=already_process_group_leader", "plain-child detached=True live_is_pid=True ladder=True detachment=new_session", "REAPER_EXACT_BYTES_BOTH_SHAPES_PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "setsid-leader detached=True[\\s\\S]*plain-child detached=True[\\s\\S]*REAPER_EXACT_BYTES_BOTH_SHAPES_PASS"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c \"$(sed -n '/^# V3-BEGIN$/,/^# V3-END$/p' docs/process_traces/2026-09-03-watchdog-build/30-delta-reaudit-round-11.md)\"",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["clean_rc=0 clean_lines=10", "mismatch_rc=0 continued_lines=10 unequal_digests=True", "STEP0_EXACT_BLOCK_FAIL_OPEN"]},
      "expected": {"exit_code": 0, "tail_regex": "STEP0_MISMATCH_REFUSED"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "test -z \"$(git diff --name-only 9b1424f5..HEAD -- scripts/magistrate_watchdog.py scripts/install_magistrate_watchdog.sh 'configs/launchd/*.template')\" && echo D172_VACUOUS_NO_GOVERNED_CHANGED_LINES",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["D172_VACUOUS_NO_GOVERNED_CHANGED_LINES"]},
      "expected": {"exit_code": 0, "tail_regex": "^D172_VACUOUS_NO_GOVERNED_CHANGED_LINES$"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check 9b1424f5..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sandbox denied the exact reaper's /bin/ps subprocess, so V2 injects only a deterministic process-table subprocess shim; the exact reaper bytes and live os.getpgid detachment observations are retained.",
      "needs": "Lead retains installed-handoff and real-process-table verification."
    }
  ]
}
```

## Findings

N1 — blocker — `docs/process/MAGISTRATE_WATCHDOG.md:94-114` tells the Terminal-hosted interactive operator to run the shown commands, but the block neither enables `errexit` nor makes a failed per-file comparison terminate the loop. With a real two-parent merge on `main`, mutating the first pinned file made its two printed digests unequal; the exact block continued through all five files and returned 0 because the last comparison passed. The test at `tests/test_magistrate_watchdog.py:1597-1621` masks this by invoking the block as `/bin/zsh -eu -c`. Make failure local and explicit (for example, `test ... || return 1` in the interactive block), and execute the test without importing `-e`.

Same-signature statement: **YES**. A green test supplies safety semantics absent from the production checklist, so the trace-28 unit-green/production-path-broken signature recurs.

F1 is cured. The exact documented reaper bytes completed the TERM/KILL/snapshot ladder both when launched with `start_new_session=True` (a `setsid` process-group leader) and as a plain child. Live `os.getpgid(pid)` equaled the reaper PID and differed from the launching process group in both cases; the plain child recorded its launcher's PGID before calling `setsid()`.

```python
# V2-BEGIN
import json,os,re,subprocess,sys,tempfile,textwrap,time
from pathlib import Path
t=Path('docs/process/MAGISTRATE_WATCHDOG.md').read_text()
b=re.findall(r"<<'PY'.*?\n(.*?)\n\s*PY$",t,re.S|re.M)
code=textwrap.dedent(next(x for x in b if 'magistrate_handoff_receipt' in x))
with tempfile.TemporaryDirectory() as d:
 r=Path(d); s=r/'shadow'; (s/'scripts').mkdir(parents=True)
 (s/'scripts/magistrate_watchdog.py').write_text("STOP_COOPERATIVE_S=0\nclass C:\n empty=True\n def __init__(self): self.detail='empty'\ndef production_census(): return C()\n")
 (s/'subprocess.py').write_text("import os,time\nfrom pathlib import Path\nclass R: stdout=''\ndef run(*a,**k):\n p=Path(os.environ['MARK']); fresh=not p.exists(); p.write_text('x'); time.sleep(.4 if fresh else 0); return R()\n")
 inv=r/'i'; inv.write_text(json.dumps({'owned':[],'interactive_pid':999999})); parent=os.getpgid(0)
 for name,sns,label in [('setsid-leader',True,'already_process_group_leader'),('plain-child',False,'new_session')]:
  mark=r/name; env={**os.environ,'PYTHONPATH':str(s),'MARK':str(mark)}
  p=subprocess.Popen([sys.executable,'-',str(inv),str(s)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,cwd=r,env=env,start_new_session=sns)
  p.stdin.write(code); p.stdin.close()
  while not mark.exists(): time.sleep(.01)
  pg=os.getpgid(p.pid); p.wait(10); rec=json.loads(p.stdout.read())
  ladder=p.returncode==0 and rec['verdict']=='pass' and rec['after_term']=={} and rec['after_kill']=={}
  assert pg==p.pid and pg!=parent and ladder and rec['reaper_detachment']==label
  assert rec['initial_process_group_id']==(p.pid if sns else parent)
  print(f'{name} detached={pg!=parent} live_is_pid={pg==p.pid} ladder={ladder} detachment={label}')
print('REAPER_EXACT_BYTES_BOTH_SHAPES_PASS')
# V2-END
```

```python
# V3-BEGIN
import re,shlex,subprocess,tempfile
from pathlib import Path
t=Path('docs/process/MAGISTRATE_WATCHDOG.md').read_text(); gate=next(x for x in re.findall(r'```zsh\n(.*?)\n\s*```',t,re.S) if 'merge_sha="$(' in x)
with tempfile.TemporaryDirectory() as d:
 r=Path(d)/'r'; r.mkdir()
 def g(*a): return subprocess.run(('/usr/bin/git','-c','user.name=P','-c','user.email=p@invalid',*a),cwd=r,check=True,capture_output=True,text=True).stdout.strip()
 g('init','-b','main'); files=('scripts/magistrate_watchdog.py','scripts/install_magistrate_watchdog.sh','docs/process/MAGISTRATE_WATCHDOG.md','docs/process/MAGISTRATE_RELAUNCH_PROMPT.md','docs/process/NIGHT_HANDBACK.md')
 for i,x in enumerate(files): p=r/x; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(f'{i}\n')
 g('add','.'); g('commit','-m','base'); g('switch','-c','w'); (r/'marker').write_text('x'); g('add','.'); g('commit','-m','w'); g('switch','main'); g('merge','--no-ff','w','-m','merge')
 assert len(g('show','-s','--format=%P','HEAD').split())==2
 cmd=gate.replace('cd /Users/edr/code/JouleWise','cd '+shlex.quote(str(r)),1); clean=subprocess.run(('/bin/zsh','-c',cmd),capture_output=True,text=True)
 print(f'clean_rc={clean.returncode} clean_lines={len(clean.stdout.splitlines())}'); (r/files[0]).write_text('mismatch\n'); bad=subprocess.run(('/bin/zsh','-c',cmd),capture_output=True,text=True); lines=bad.stdout.splitlines(); unequal=lines[0].split()[0]!=lines[1].split()[0]
 print(f'mismatch_rc={bad.returncode} continued_lines={len(lines)} unequal_digests={unequal}')
 if bad.returncode==0: print('STEP0_EXACT_BLOCK_FAIL_OPEN'); raise SystemExit(1)
 print('STEP0_MISMATCH_REFUSED')
# V3-END
```

Verdict line: **RESIDUAL**.

## Residual risk

No LaunchAgent was installed or loaded, no default custody was accessed, and no production process was signalled. Sandbox policy denied `/bin/ps` from the exact reaper, so the ladder snapshots used a deterministic subprocess shim while process-group detachment itself was observed live with `os.getpgid`.
