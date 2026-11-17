"""Read issued forms from Git, reproducing the stale selection on synthetic bytes.

No current measurement/custody root or RUN_STATE worktree file is opened/edited.
Exit 0 means all expected vulnerability/control observations reproduced, not
that the issued gates are correct. No issuance or live hardware claim is made.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ref = sys.argv[1] if len(sys.argv) > 1 else 'origin/main'
head = subprocess.check_output(['git', 'rev-parse', ref], text=True).strip()
source = subprocess.check_output(['git', 'show', head+':RUN_STATE.md'], text=True)
print('Issued source', head, '; synthetic counterexamples only')
checks = 0


def quote(value):
    return "'"+str(value).replace("'", "'\"'\"'")+"'"


for number in (354, 355, 366, 367, 372):
    text = re.search(r'^'+str(number)+r'\. .*?(?=^\d+\. \*\*|\Z)', source, re.M | re.S).group()
    funcs = []
    for name in ('close_census', 'effective_close', 'copy_gate'):
        funcs.append(re.search(r'^'+name+r'\(\).*?\n[})][ \t]*(?:#.*)?$', text, re.M | re.S).group())
    program = '\n'.join(funcs)
    assert 'st_mtime' in program, number
    for shell in ('bash', 'zsh'):
        with tempfile.TemporaryDirectory(prefix='jw-issued-close-') as tmp:
            home = Path(tmp); root, wt, markers = (home/n for n in ('campaign-out', 'jw-wt', 'markers'))
            for p in (root, wt, markers): p.mkdir()
            now = 1794960000
            old = root/'cl-dev-01'/'cq-dev-01-s04-a1-20261114T080000Z'/'runner_receipt.json'
            latest = root/'cl-dev-04'/'cq-dev-04-s02-a1-20261117T090000Z'/'runner_receipt.json'
            for path, age in ((old, 5000), (latest, 400)):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({'synthetic_fixture': True, 'ended': {'epoch_s': now-age}}))
                os.utime(path, (now-age, now-age))
            old_bytes = old.read_bytes()
            (markers/'cq-dev-01-s04-a1.ok').write_text('SYNTHETIC verified old copy\n')
            rewritten = program.replace('/Users/edr/campaign-out', str(root)).replace(
                '/Users/edr/code/jw-wt', str(wt)).replace('/Users/Shared/JouleWise/desk-copy', str(markers))
            script = ('PY='+quote(sys.executable)+'\n'+rewritten+'\nLAST_CLOSE_KIND=campaign\n'
                      'OTHER_CLOSE_EPOCH=0\nPRIOR_CLOSE_EPOCH='+str(now-400)+
                      '\neffective_close && copy_gate\n')

            def run(label, ok, contains):
                global checks
                result = subprocess.run([shell], input=script, text=True, capture_output=True)
                output = result.stdout+result.stderr
                assert (result.returncode == 0) == ok and contains in output, (number, shell, label, output)
                checks += 1
                print(number, shell, label, '| rc', result.returncode, '|', contains)

            run('NORMAL ORDER: uncopied latest holds', False, 'WAIT')
            marker = markers/'cq-dev-04-s02-a1.ok'
            marker.write_text('SYNTHETIC verified latest copy\n')
            run('NORMAL ORDER: latest copy admits', True, 'journal copy of cq-dev-04-s02-a1')
            marker.unlink()
            os.utime(old, (now-300, now-300))
            assert old.read_bytes() == old_bytes
            run('DEFECT: restored old mtime accepts old marker', True, 'journal copy of cq-dev-01-s04-a1')
print(checks, 'expected observations reproduced; all five issued items carry the defect in both shells')
