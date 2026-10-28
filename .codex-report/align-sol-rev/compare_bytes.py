"""Compare the old and new item-H runner on the same synthetic inputs/paths."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts import bytes_h_session as current
from tests.test_bytes_h_session import SessionTests

OUT = Path(__file__).resolve().parent
WORK = Path(tempfile.mkdtemp(prefix='bytescompare-', dir='/private/tmp/jwreview'))
case = SessionTests()
with patch('tempfile.TemporaryDirectory', return_value=SimpleNamespace(name=str(WORK), cleanup=lambda: None)):
    case.setUp()
old = ModuleType('old_bytes_h')
old.__file__ = str(ROOT / 'scripts/bytes_h_session.py')
sys.modules[old.__name__] = old
raw = subprocess.check_output(['git', 'show', '991358f73:scripts/bytes_h_session.py'], cwd=ROOT)
exec(compile(raw, old.__file__, 'exec'), old.__dict__)

snapshots = {}
for label, runner in [('before', old), ('after', current)]:
    stdout = io.StringIO()
    with patch.object(current.plan, 'ledger_head_status', return_value={'blocking': []}), redirect_stdout(stdout):
        state = runner.prepare(case.measurement, case.session, run=case.producer,
            now=lambda: 1700000000,
            statvfs=lambda _: SimpleNamespace(f_bavail=10**12, f_frsize=1), capacity=lambda _: None)
    snapshot = {}
    def visit(directory):
        for path in sorted(directory.iterdir()):
            key = path.relative_to(case.session).as_posix()
            if path.is_symlink():
                snapshot[key] = {'symlink': str(path.readlink())}
            elif path.is_dir():
                visit(path)
            else:
                data = path.read_bytes()
                snapshot[key] = {'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    visit(case.session)
    snapshots[label] = snapshot
    (OUT / f'bytes-{label}-stdout.txt').write_text(stdout.getvalue())
    (OUT / f'bytes-{label}-state.json').write_text(json.dumps(state, sort_keys=True, indent=2) + '\n')
    (OUT / f'bytes-{label}-files.json').write_text(json.dumps(snapshot, sort_keys=True, indent=2) + '\n')
    shutil.rmtree(case.session)

changed = [key for key in sorted(snapshots['before'].keys() | snapshots['after'].keys())
           if snapshots['before'].get(key) != snapshots['after'].get(key)]
results = {'baseline': '991358f73', 'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
           'paths_compared': len(snapshots['before']), 'changed_generated_paths': changed}
for kind in ('stdout.txt', 'state.json', 'files.json'):
    result = subprocess.run(['diff', '-u', str(OUT / ('bytes-before-' + kind)),
                             str(OUT / ('bytes-after-' + kind))], capture_output=True, text=True)
    results[kind] = {'diff_exit': result.returncode, 'diff': result.stdout}
print(json.dumps(results, sort_keys=True, indent=2))
shutil.rmtree(WORK)
