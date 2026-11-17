"""Run each embedded close/copy gate in both shells on synthetic receipts only.

The stale-marker counterexample keeps old receipt bytes unchanged and changes
only its filesystem mtime. Positive cases require the real latest span's marker.
Pass a draft directory to restrict the census; default covers all three sets.
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

BASE = Path(__file__).resolve().parents[2]
FOLDERS = [Path(sys.argv[1]).resolve()] if len(sys.argv) > 1 else [
    BASE / ('item-drafts-' + suffix) for suffix in ('1115', 'f2', '1118', 'rl172')]
checks = 0


def quote(value):
    return "'" + str(value).replace("'", "'\"'\"'") + "'"


def function(text, name):
    found = re.search(r'^' + name + r'\(\).*?\n[})][ \t]*(?:#.*)?$', text, re.M | re.S)
    return found.group() if found else ''


for folder in FOLDERS:
    items = sorted(folder.glob('ITEM-*.md')) + sorted(folder.glob('STANDING-*.md'))
    for item in items:
        text = item.read_text()
        program = '\n'.join(function(text, name) for name in
                            ('close_census', 'effective_close', 'copy_gate', 'filled'))
        assert function(text, 'effective_close') and function(text, 'copy_gate'), item
        for shell in ('bash', 'zsh'):
            assert shutil.which(shell), shell
            with tempfile.TemporaryDirectory(prefix='jw-close-selection-') as tmp:
                home = Path(tmp)
                root, wt, markers = (home / n for n in ('campaign-out', 'jw-wt', 'markers'))
                for p in (root, wt, markers): p.mkdir()
                old = root/'cl-dev-01'/'cq-dev-01-s04-a1-20261114T080000Z'/'runner_receipt.json'
                latest = root/'cl-dev-04'/'cq-dev-04-s02-a1-20261117T090000Z'/'runner_receipt.json'
                now = 1794960000

                def receipt(path, close, mtime):
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps({'synthetic_fixture': True, 'ended': {'epoch_s': close}}))
                    os.utime(path, (mtime, mtime))

                receipt(old, now-5000, now-5000)
                old_bytes = old.read_bytes()
                receipt(latest, now-400, now-400)
                old_marker = markers/'cq-dev-01-s04-a1.ok'
                old_marker.write_text('SYNTHETIC old verified copy\n')
                latest_marker = markers/'cq-dev-04-s02-a1.ok'
                # A restored old file acquires a new mtime without any receipt edit.
                os.utime(old, (now-300, now-300))
                assert old.read_bytes() == old_bytes
                rewritten = program.replace('/Users/edr/campaign-out', str(root)).replace(
                    '/Users/edr/code/jw-wt', str(wt)).replace('/Users/Shared/JouleWise/desk-copy', str(markers))

                def run(label, ok, contains, **overrides):
                    global checks
                    values = dict(OTHER_CLOSE_EPOCH=0, PRIOR_CLOSE_EPOCH=now-400,
                                  LAST_CLOSE_KIND='campaign')
                    values.update(overrides)
                    assignments = '\n'.join(k+'='+quote(v) for k, v in values.items())
                    script = ('PY='+quote(sys.executable)+'\n'+rewritten+'\n'+assignments+
                              '\neffective_close && copy_gate\n')
                    result = subprocess.run([shell], input=script, text=True, capture_output=True,
                                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
                    output = result.stdout + result.stderr
                    assert (result.returncode == 0) == ok and contains in output, (
                        item.name, shell, label, result.returncode, output)
                    checks += 1

                run('restored old receipt cannot authorize uncopied latest', False, 'WAIT')
                latest_marker.write_text('SYNTHETIC actual latest verified copy\n')
                run('actual latest marker accepted despite old mtime', True, 'cq-dev-04-s02-a1')
                # Equal file mtimes are irrelevant; unequal recorded closes still select latest.
                os.utime(old, (now-400, now-400))
                run('equal mtimes with distinct close epochs', True, 'cq-dev-04-s02-a1')
                receipt(old, now-400.25, now+500)
                run('identity selected before ceil rounds epochs equal', True, 'cq-dev-04-s02-a1')
                receipt(old, now-400, now-5000)
                run('equal latest recorded epochs fail closed', False, 'ambiguous newest')
                for value in (None, True, '1794959600', 0, -1, float('nan'), float('inf')):
                    receipt(old, value, now-5000)
                    run('invalid recorded close '+str(value), False, 'receipt close stamp')
                old.write_text('{')
                run('unreadable receipt fails closed', False, 'receipt close stamp')
                old.write_text('{"synthetic_fixture":true}')
                run('missing ended field fails closed', False, 'receipt close stamp')
                receipt(old, now-5000, now-300)
                # A real-style F0 path has no plan marker producer. Its exact Check covers copy.
                f0 = wt/'partc-pin'/'.desk'/'r1-partc-f0-20261117T100000Z'/'runner_receipt.json'
                receipt(f0, now-200, now-6000)
                proof = dict(LAST_CLOSE_KIND='other', NONCAMPAIGN_COPY_OK='yes',
                             NONCAMPAIGN_COPY_CLOSE_EPOCH=now-200,
                             NONCAMPAIGN_COPY_RECEIPT=str(f0),
                             NONCAMPAIGN_COPY_RECORD='SYNTHETIC F0 Check and verified copy')
                run('F0 handoff with Check and no F0 marker', True, 'copy', **proof)
                # The stronger proof inputs are part of F2/qualification; issued-style
                # counted/F0 copies retain their existing manual Check contract.
                if 'NONCAMPAIGN_COPY_OK' in program:
                    run('F0 missing Check rejected', False, 'WAIT', **{**proof, 'NONCAMPAIGN_COPY_OK': 'no'})
                    run('stale F0 Check rejected', False, 'WAIT', **{**proof, 'NONCAMPAIGN_COPY_CLOSE_EPOCH': now-5000})
                    run('wrong F0 identity rejected', False, 'WAIT', **{**proof, 'NONCAMPAIGN_COPY_RECEIPT': str(old)})
            print('PASS', item.name, shell, 'recorded close identity and copy regressions')
print(checks, 'close/copy regression checks; zero failures; bash and zsh; synthetic only')
