"""Portable runner: generate disposable pinned mocks, then test every draft.

Usage: bash tests/run_all_gates.sh /path/to/detached/2d347f721
No historical scratch fixtures, measurement roots or network are accessed.
"""
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parents[1]
PIN = Path(sys.argv[1]).resolve()
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=PIN, text=True).strip() == '2d347f721552fe03bdd19f113e7bad7a7c24908e'
LOGS = Path(os.environ.get('JW_DRAFT_EVIDENCE_DIR', HERE/'evidence/fix-2026-11-16'))
LOGS.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', JW_B5_SYNTHETIC_ONLY='1')


def check(log, *args, cwd=HERE):
    result = subprocess.run([sys.executable, '-B', *map(str, args)], cwd=cwd,
                            env=env, text=True, capture_output=True)
    (LOGS/log).write_text(result.stdout+result.stderr)
    assert result.returncode == 0, (args, result.stdout[-2000:], result.stderr[-2000:])
    print(log, result.stdout.strip().splitlines()[-1])


check('lint.log', 'tools/lint.py')
check('close-selection.log', 'tests/test_close_selection.py', HERE)
check('rl172-close-selection.log', 'tests/test_close_selection.py', HERE.parent/'item-drafts-rl172')
with tempfile.TemporaryDirectory(prefix='jw-1115-mocks-') as tmp:
    root = Path(tmp)
    env['TMPDIR'] = tmp
    for item in sorted(HERE.glob('ITEM-*.md')):
        text = item.read_text()
        pred, camp, roster = re.search(r'PRED_SPAN=([^;]+); PRED_CAMP=([^;]+); PRED_ROSTER=([^\n]+)', text).groups()
        source = {'cl-dev-02': 'b4b6aeb19', 'cl-dev-03': '9cbb365a6',
                  'cl-dev-04': 'fecaf73f3', 'cl-dev-05': 'fecaf73f3'}[camp]
        suffix = '.json' if camp == 'cl-dev-02' else '.v1.1.json'
        kit = root/(camp+suffix)
        kit.write_bytes(subprocess.check_output(['git', 'show', source+':docs/process/cadence/kits/'+kit.name], cwd=HERE))
        mock = root/item.stem
        check(item.stem+'-mock.log', 'scripts/cadence_legs_runner.py', 'mock',
              '--kit', kit, '--output', mock, '--legs', roster,
              '--t0-local', '2026-11-16T00:30:00', '--batch-window', '13:14-13:15', cwd=PIN)
        check(item.stem+'-gates.log', 'tests/test_rl173_gates.py', item, mock, camp, pred, roster)
print('PASS seven drafts: syntax, close/copy regressions, seven pinned mocks, 238 predecessor/expiry/watcher checks')
