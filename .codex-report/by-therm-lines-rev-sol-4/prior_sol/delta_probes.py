"""Independent fix-round fault repros; all data synthetic; no measurements printed."""
import sys, json, subprocess, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tests.test_bytes_thermal_lines import RecordedFaultTests
from scripts import bytes_thermal_lines as t

def fixture():
    f = RecordedFaultTests(); f.setUp(); return f

def cli(*args):
    return subprocess.run([sys.executable, 'scripts/bytes_thermal_lines.py', *map(str,args)], capture_output=True, text=True)

def codes(out):
    return [(r['run_id'], r['code']) for r in json.loads((out/'derived/b6-acceptance.json').read_bytes())['excluding']]

f=fixture()
try:
    f.put('derived/window_flags.json', {'hazards': {'thermal': {'continuous': {'journal': {'sha256': '0'*64}}}}})
    r=t.transform('request-end-p1', f.archive, f.root/'mismatch')
    print('MISMATCH', r['status'], 'changes', len(r['changes']))
    (f.archive/'derived/window_flags.json').unlink()
    r=t.transform('request-end-p1', f.archive, f.root/'missing-seal')
    print('MISSING_SEAL', r['status'], 'changes', len(r['changes']), 'codes', codes(f.root/'missing-seal'))
    # Re-use a supported existing output with a prior transformed export.
    exp=f.root/'exp'; exp.mkdir()
    (exp/'s.runs.csv').write_text('run_id,exclusion_codes,excluded\na,'+t.CODE+',True\nb,,False\n')
    out=f.root/'reuse'
    t.transform('request-end-p1', f.archive, out, exp)
    f.put('sources/repo/plan_tree.json', {'bytes_pass': 2})
    t.transform('request-end-p1', f.archive, out)
    print('REUSE_ARCHIVE', codes(out))
    print('REUSE_CSV', (out/'export/s.runs.csv').read_text().splitlines()[1:])
    print('REUSE_VERIFY', t.verify(out))
    # Manifest corruption must be recorded, not an exception.
    manifest=out/'view_manifest.json'; manifest.chmod(0o644)
    manifest.write_text('{"files":[{"path":7}]}')
    result=cli('verify',out)
    print('DAMAGED_MANIFEST', 'exit', result.returncode, 'tail', result.stderr.splitlines()[-1])
    print('DAMAGED_MANIFEST_FLAG', json.loads((out/'thermal_line.json').read_bytes())['records.thermal_view_changed'])
    # Source protection when a preexisting output export directory is a link.
    (f.archive/'sources/repo/plan_tree.json').unlink()
    out=f.root/'linked-output'; out.mkdir(); (out/'export').symlink_to(exp, target_is_directory=True)
    before=(exp/'s.runs.csv').read_bytes()
    t.transform('request-end-p1', f.archive, out, exp)
    print('SOURCE_EXPORT_CHANGED', before != (exp/'s.runs.csv').read_bytes())
finally: f.doCleanups()
