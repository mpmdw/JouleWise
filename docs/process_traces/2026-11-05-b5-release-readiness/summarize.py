"""Summarize only this task's generated synthetic evidence; never a study-root tool."""
import collections
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path.cwd()
OUT = ROOT / '.scratch-b5-release-readiness/r2/.scratch-s10f/tmp/readiness-on'
TRACE = ROOT / 'docs/process_traces/2026-11-05-b5-release-readiness'
assert (OUT / 'progress.jsonl').is_file()
driver = json.loads((OUT / 'driver-summary.json').read_text())
assert driver['r2_commit'] == '929fc65c9ce3ff82f0311d28acf76a682edd466f'
assert driver['completed_without_tooling_refusal'] is True, 'incomplete driver is not acceptance'
assert {'0','1','2','3','3b','4','5','8','6','9','9b','10','11'} <= {r['step'] for r in driver['steps']}
assert all(r['status'] == 'ok' or (r['step'] == '9b' and r['status'] == 'outcome_class') for r in driver['steps'])
assert all(r['status'] == 'ok' for r in driver['steps'] if r['step'] in ('10','11'))

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

runs = {}
for name, script, bars in [
    ('rc-cmp-1-coded', OUT / 'compare_b5_recompute_RC_CMP_1.py', ROOT / 'tests/independent_recompute/bar_sets/recompute_coded_7e322b76.json'),
    ('rc-cmp-1-s13', OUT / 'compare_b5_recompute_RC_CMP_1.py', ROOT / 'tests/independent_recompute/bar_sets/s13_block6.json')]:
    argv = [sys.executable, '-B', str(script), '--l9-custody', str(OUT / 'synthetic-custody'),
            '--recompute', str(OUT / 'recompute.json'), '--bars', str(bars), '--restricted-out', str(OUT / (name + '.json'))]
    meta = OUT / (name + '-invocation.json')
    if meta.exists():
        runs[name] = json.loads(meta.read_text())
        assert runs[name]['argv'] == argv
    else:
        with (OUT / (name + '.stdout')).open('x') as stdout, (OUT / (name + '.stderr')).open('x') as stderr:
            rc = subprocess.run(argv, stdout=stdout, stderr=stderr).returncode
        runs[name] = {'argv': argv, 'exit': rc, 'script_sha256': sha(script), 'bars_sha256': sha(bars)}
        meta.write_text(json.dumps(runs[name], sort_keys=True, indent=2) + '\n')

runs['current'] = {'argv': json.loads((OUT / 'comparator-command.json').read_text()),
                   'exit': [r['rc'] for r in map(json.loads, (OUT / 'progress.jsonl').read_text().splitlines()) if r['event'] == 'comparison_done'][0],
                   'script_sha256': sha(ROOT / 'scripts/compare_b5_recompute.py'),
                   'bars_sha256': sha(ROOT / 'configs/analysis/b5/recompute_bars.json')}
coverage = {'data_class': 'SYNTHETIC_ONLY', 'note': 'Normalized leaf paths; list stars collapse positions. No study values.'}
for name, filename in [('current', 'comparison-initial.json'), ('rc-cmp-1-coded', 'rc-cmp-1-coded.json'), ('rc-cmp-1-s13', 'rc-cmp-1-s13.json')]:
    p = OUT / filename
    r = json.loads(p.read_text())
    c = r.get('coverage', {})
    leaves = c.get('leaves', {})
    uncovered = {k: v for k, v in leaves.items() if v.startswith('uncovered')}
    compared = {k: v for k, v in leaves.items() if not v.startswith('uncovered')}
    runs[name].update({'counts': r.get('counts'), 'comparisons': len(r.get('comparisons', [])),
                       'disagreements': sum(x['verdict'] != 'AGREE' for x in r.get('comparisons', [])),
                       'leaf_paths': len(set(leaves) | set(c.get('unmapped', []))),
                       'compared_leaf_paths': len(compared), 'uncovered_leaf_paths': len(uncovered),
                       'unmapped_leaf_paths': len(c.get('unmapped', [])),
                       'uncovered_numeric_paths': len(c.get('uncovered_numeric', [])),
                       'nonfinite': len(c.get('nonfinite', [])), 'absent_sources': c.get('absent_sources', []),
                       'refused': r.get('refused'), 'output_sha256': sha(p)})
    coverage[name] = {'compared': compared, 'uncovered': uncovered,
                      'unmapped': c.get('unmapped', []), 'unbound': c.get('unbound', []),
                      'uncovered_numeric': c.get('uncovered_numeric', []), 'named_exemptions': c.get('named_exemptions', {})}
if coverage['rc-cmp-1-s13'] == coverage['rc-cmp-1-coded']:
    coverage['rc-cmp-1-s13'] = {'identical_to': 'rc-cmp-1-coded'}
record = json.loads((OUT / 'synthetic-custody/dry-run/B5-BLIND-DRY-RUN-RECORD.json').read_text())
assert sha(OUT / 'synthetic-custody/dry-run/B5-BLIND-DRY-RUN-RECORD.json') == driver['record_sha256']
driver.update(record_analysis_commit=record['analysis_commit'], mode=record['mode'], window_index_sha256=record['window_index_sha256'])
recompute = json.loads((OUT / 'recompute.json').read_text())
summary = {'data_class': 'SYNTHETIC_ONLY',
           'comparator_checkout_commit': subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
           'legacy_comparator_commit': subprocess.check_output(['git','rev-parse','234fbb127'],text=True).strip(),
           'interrupted_shadow_attempt': json.loads((ROOT / '.scratch-b5-release-readiness/tmp/driver-summary.json').read_text()), 'driver': driver,
           'comparators': runs,
           'recompute': {'argv': json.loads((OUT / 'recompute-command.json').read_text()),
                         'sha256': sha(OUT / 'recompute.json'),
                         'script_sha256': sha(ROOT / 'scripts/independent_recompute_b5.py'),
                         'interpreter': recompute.get('interpreter'),
                         'exit': [r['rc'] for r in map(json.loads, (OUT / 'progress.jsonl').read_text().splitlines()) if r['event'] == 'recompute_done'][0],
                         'flags_by_code': dict(collections.Counter(f['code'] for f in recompute.get('flags', [])))},
           'fixtures': {pack: {'members': json.loads((ROOT / '.scratch-b5-release-readiness/r2/tests/fixtures/b5_analysis/s10' / pack / 'STRUCTURE.json').read_text())['member_count'],
                              'archive_sha256': sha(ROOT / '.scratch-b5-release-readiness/r2/tests/fixtures/b5_analysis/s10' / pack / 'archive.tar.xz')}
                        for pack in ['alpha', 'beta', 'gamma']}}
for name, value in [('synthetic-summary.json', summary), ('synthetic-coverage.json', coverage)]:
    (TRACE / name).write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')
for name, result in runs.items():
    print(name, json.dumps({k: result[k] for k in ['exit','comparisons','disagreements','leaf_paths','compared_leaf_paths','uncovered_leaf_paths','unmapped_leaf_paths','uncovered_numeric_paths','nonfinite','absent_sources','refused']}, sort_keys=True))
print('flags', json.dumps(summary['recompute']['flags_by_code'], sort_keys=True))
