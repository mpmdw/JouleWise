#!/usr/bin/env python3.13
"""RC-CMP-SOL-REV-3. Synthetic only; all review probes are orchestrated here.
Run: TMPDIR=/private/tmp/jwrc3-tmp JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 .codex-report/rc-cmp-sol-rev-3/probes.py
Prior review folders are git-archived only beneath TMPDIR, never into the checkout.
"""
import ast
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import traceback
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRATCH = Path('/private/tmp/jwrc3-tmp') / 'rc-cmp-sol-rev-3-prior'
os.environ.update(TMPDIR='/private/tmp/jwrc3-tmp', JW_B5_SYNTHETIC_ONLY='1', PYTHONDONTWRITEBYTECODE='1')
tempfile.tempdir = os.environ['TMPDIR']
sys.dont_write_bytecode = True
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]


def prior():
    """Rerun every .py from the four earlier review folders in isolated processes."""
    env = dict(os.environ, PYTHONPATH=str(ROOT) + ':' + str(ROOT / 'tests'))
    for seat in ('sol-rev', 'sol-rev-2', 'opus-rev', 'opus-rev-2'):
        folder = '.codex-report/rc-cmp-' + seat
        dest = SCRATCH / seat
        dest.mkdir(parents=True, exist_ok=True)
        raw = subprocess.check_output(['git', 'archive', 'origin/review/2026-10-28-rc-cmp-' + seat, folder], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
            archive.extractall(dest, filter='data')
        for path in sorted((dest / folder).glob('*.py')):
            print('\nPRIOR', seat, path.name, 'sha256=' + hashlib.sha256(path.read_bytes()).hexdigest(), flush=True)
            command = [sys.executable, str(path)]
            if path.name == 'probe_streams.py':
                # The archive is intentionally outside the checkout. Restore only this
                # old probe's checkout locator, so its isolated children execute HEAD.
                source = path.read_text().replace('ROOT = Path(__file__).resolve().parents[2]',
                                                 'ROOT = Path(' + repr(str(ROOT)) + ')')
                command = [sys.executable, '-c', source]
                print('ADAPTATION checkout ROOT only; probe logic unchanged', flush=True)
            result = subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True)
            print(result.stdout, end='')
            print('PROCESS_EXIT', result.returncode, flush=True)
            if seat == 'sol-rev' and path.name == 'probe_comparator.py':
                # Original aborts at the newly correct bars_invalid refusal. Guard just that
                # call, as the round-2 review did, to execute the remaining original probes.
                source = path.read_text()
                old = '''    result = tc.cmp.run(case.custody(), ours, path, tc.RULES)
    row = next(r for r in result["comparisons"] if r["key"] == tc.DECODE + "/dbar_j")
    print("infinite_override", failures(result), row["verdict"], row["bar"])'''
                new = '''    try:
        result = tc.cmp.run(case.custody(), ours, path, tc.RULES)
        row = next(r for r in result["comparisons"] if r["key"] == tc.DECODE + "/dbar_j")
        print("infinite_override", failures(result), row["verdict"], row["bar"])
    except tc.cmp.Refusal as exc:
        print("infinite_override REFUSED", str(exc))'''
                assert old in source
                print('PRIOR sol-rev probe_comparator.py guarded continuation', flush=True)
                result = subprocess.run([sys.executable, '-c', source.replace(old, new)], cwd=ROOT, env=env,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                print(result.stdout, end='')
                print('GUARDED_PROCESS_EXIT', result.returncode, flush=True)


from tests.independent_recompute import test_review_fixes as t
from tests.independent_recompute import test_structural_rules as structural
cmp, FILL, DISC, VERD = t.cmp, t.FILL, t.DISCLOSURE, t.VERDICTS


def fresh():
    case = t.Case(); case.setUp()
    return case


def show(label, case):
    code, error, result = case.exit_code(t.BARS['recompute_coded_7e322b76'])
    cover = result.get('coverage', {})
    fails = case.fails(result) if 'counts' in result else None
    print('NEW', label, json.dumps({'exit': code, 'stderr': error.strip(), 'fails': fails,
          'unmapped': cover.get('unmapped'), 'unbound': cover.get('unbound'),
          'named': cover.get('uncovered_numeric'), 'refused': result.get('refused')}, sort_keys=True), flush=True)
    return code, result


def attack_shapes():
    for value in (999.0, '999.0', True, None, [999.0], [['999.0']], [[999.0]], [], {}):
        case = fresh()
        try:
            case.files[FILL]['campaigns'] = {'alpha': {'gross_energy_j': value}}
            show('unknown_energy_shape=' + repr(value), case)
        finally: case.tmp.cleanup()
    # Values that look numeric still cannot replace a registered numeric leaf.
    for value in ('-1.25', True, [-1.25], [[-1.25]], {}, []):
        case = fresh()
        try:
            case.files[FILL]['gamma']['contrasts'][0]['estimate'] = value
            show('registered_estimate_shape=' + repr(value), case)
        finally: case.tmp.cleanup()
    for field, value in (('point_floor_diagnostics', {'active_floor_j': 999999.0}),
                         ('single_count_discipline', {'estimate': 999999.0})):
        case = fresh()
        try:
            case.files[FILL]['gamma']['contrasts'][0]['floor'] = {field: value}
            show('named_broad_subtree=' + field, case)
        finally: case.tmp.cleanup()
    for value in (None, 999.0, {'estimate': 999.0}, [999.0]):
        case = fresh()
        try:
            case.files[FILL]['gamma']['contrasts'][0]['j_per_token'] = value
            show('registered_null_shape=' + repr(value), case)
        finally: case.tmp.cleanup()


def attack_nested_identity():
    case = fresh()
    try:
        next(r for r in case.files[VERD]['contrasts'] if r['contrast_id'] == t.PREFILL)['estimator']['estimate'] = -2.5
        case.ours['contrasts'][t.PREFILL]['dbar_j'] = -2.5
        case.files[FILL]['gamma']['contrasts'][1]['estimate'] = -2.5
        outer = {'line': 'primary_contrast', 'contrast_id': t.DECODE,
                 'estimator': {'estimate': -2.5}}
        case.files[DISC]['contrasts'].append(outer)
        code, _ = show('wrong_decode_disclosure_estimate_control', case)
        assert code == 2
        outer['estimator']['contrast_id'] = t.PREFILL
        code, result = show('nested_estimator_contrast_id_redirects_wrong_decode_estimate', case)
        print('NESTED_ID_COVERAGE', {p: f for p, f in result['coverage']['leaves'].items() if 'primary_contrast' in p})
        assert code == 0, 'Candidate false agreement no longer reproduces'
        # A narrow read-only counterfactual: preserve the contrast container identity.
        original = cmp.leaves
        def no_shadow(value, path='', context=None):
            if path.endswith('/estimator') and isinstance(value, dict):
                value = {k: v for k, v in value.items() if k != 'contrast_id'}
            yield from original(value, path, context)
        with mock.patch.object(cmp, 'leaves', no_shadow):
            assert show('nested_identity_counterfactual_no_shadow', case)[0] == 2
    finally: case.tmp.cleanup()


def raw_cli(case, source, before, after, label):
    """Rewrite one synthetic input's raw bytes and rebind its authentic digest."""
    custody = case.custody()
    target = custody / cmp.RESTRICTED / source
    raw = target.read_text(); assert before in raw
    target.write_text(raw.replace(before, after, 1))
    record_path = custody / cmp.RECORD
    record = json.loads(record_path.read_text())
    for step in record['steps']:
        for row in step['outputs']:
            if row['name'] == source:
                row['sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
    record_path.write_text(json.dumps(record))
    own = case.root / 'raw-ours.json'; own.write_text(json.dumps(case.ours))
    output = case.root / (label + '.json')
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as error:
        code = cmp.main(['--l9-custody', str(custody), '--recompute', str(own), '--bars',
                         str(t.BARS['recompute_coded_7e322b76']), '--restricted-out', str(output)])
    result = json.loads(output.read_text())
    print('RAW', label, 'exit', code, 'stderr', error.getvalue().strip(), 'fails',
          case.fails(result) if 'counts' in result else result, 'unmapped', result.get('coverage', {}).get('unmapped'), flush=True)
    return code


def attack_duplicates():
    case = fresh()
    try:
        assert raw_cli(case, FILL, '"estimate": -1.25', '"estimate": 999999.0, "estimate": -1.25',
                       'duplicate_json_estimate_bad_first') == 0
        assert raw_cli(case, FILL, '"estimate": -1.25', '"estimate": -1.25, "estimate": 999999.0',
                       'duplicate_json_estimate_bad_last') == 2
        assert raw_cli(case, FILL, '"estimate": -1.25', '"estimate": NaN, "estimate": -1.25',
                       'duplicate_json_nan_discarded') == 0
    finally: case.tmp.cleanup()
    c = cmp.Comparison(cmp.load_bars(t.BARS['recompute_coded_7e322b76']))
    c.numeric('contrast_j', 'same-key', 1.0, 1.0)
    c.numeric('floor_j', 'same-key', 2.0, 2.0)
    print('KEY_SPACE cross_family', [(r['family'], r['key'], r['verdict']) for r in c.rows])
    try: c.numeric('floor_j', 'same-key', 2.0, 2.0)
    except cmp.Refusal as exc: print('KEY_SPACE same_family_refusal', str(exc))


def attack_collections_and_ast():
    case = fresh()
    try:
        projection = f'outputs/{t.SHA}-projection-alpha.json'
        case.files[projection]['refused_cells'] = [{'cell_id': 'd117-reported-mean-ph-prefill-p42-qwen3-1p7b'}]
        show('projection_p42_present', case)
        case.files[projection]['refused_cells'] = []
        show('projection_p42_omitted', case)
        before = case.shipped()['counts']['p42_status']
        case.files[projection]['refused_cells'] = [{'cell_id': 'd117-reported-mean-ph-prefill-p42-qwen3-1p7b'}]
        after = case.shipped()['counts']['p42_status']
        print('ONE_SIDED_P42 row_counts', before, after)
    finally: case.tmp.cleanup()
    structural.StructureTests.setUpClass()


def ast_counterfactuals():
    """Both structural AST tests miss a one-sided while loop and helper-side filtering."""
    structural.StructureTests.setUpClass()
    base = ast.parse((ROOT / 'scripts/compare_b5_recompute.py').read_text())
    for label, replacement in (
        ('one_sided_while', '''def compare_exclusions(c, ours):
    cursor = iter(ours.get('exclusions_rederivation', {}).items())
    while True:
        try:
            pack, row = next(cursor)
        except StopIteration:
            break
        c.exact('exclusions_rederivation', pack, 'agrees', row.get('status'))
'''),
        ('helper_drops_all_selected_runs', '''def selected_runs(members):
    return {}
''')):
        tree = copy.deepcopy(base)
        altered = ast.parse(replacement).body[0]
        tree.body = [altered if isinstance(n, ast.FunctionDef) and n.name == altered.name else n for n in tree.body]
        ast.fix_missing_locations(tree)
        structural.StructureTests.tree = tree
        structural.StructureTests.functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        for method in ('test_family_functions_iterate_only_through_the_union_helper',
                       'test_rows_are_built_only_in_family_functions'):
            getattr(structural.StructureTests(method), method)()
        print('AST_MUTANT', label, 'both_AST_gates=PASS')
        namespace = {'__file__': str(ROOT / 'scripts/compare_b5_recompute.py'), '__name__': 'review_mutant'}
        exec(compile(tree, '<read-only AST counterfactual>', 'exec'), namespace)
        if label == 'one_sided_while':
            c = namespace['Comparison'](namespace['load_bars'](t.BARS['recompute_coded_7e322b76']))
            namespace['compare_exclusions'](c, {'exclusions_rederivation': {'ALPHA': {'status': 'agrees'}}})
            print('AST_MUTANT_ROWS', label, [(r['key'], r['verdict']) for r in c.rows], 'BETA/GAMMA absent')
        else:
            print('AST_MUTANT_ROWS', label, namespace['selected_runs']({'ALPHA': {'run-a': {'selected': True}}}))
    structural.StructureTests.setUpClass()


def ast_guard_scope():
    structural.StructureTests.setUpClass()
    constants = structural.StructureTests.constants
    for source in ("[(k, v) for k, v in a.items()]", "c.pairs('x/', a, b)",
                   "zip(('only',), a.values())", "[('x', row.get('items'))]"):
        node = ast.parse(source, mode='eval').body
        print('AST iterable_allowed', source, structural.iterable_allowed(node, constants))
    tree = ast.parse((ROOT / 'scripts/compare_b5_recompute.py').read_text())
    print('AST helpers_uninspected', [n.name for n in tree.body if isinstance(n, ast.FunctionDef)
           and not n.name.startswith('compare_') and any(isinstance(s, (ast.For, ast.comprehension)) for s in ast.walk(n))])
    # Execute the two AST gates against an in-memory one-sided comprehension hidden in
    # the first item of a "constant" field-table tuple. No production file is changed.
    mutated = copy.deepcopy(tree)
    function = next(n for n in mutated.body if isinstance(n, ast.FunctionDef) and n.name == 'compare_exclusions')
    injected = ast.parse("for field, values in [('hidden', [c.numeric('count', 'hidden/' + key, value, value) for key, value in ours.get('hidden', {}).items()])]:\n    pass").body[0]
    # The checker also visits the comprehension: direct comprehension is correctly caught.
    function.body.append(injected)
    structural.StructureTests.tree = mutated
    structural.StructureTests.functions = {n.name: n for n in mutated.body if isinstance(n, ast.FunctionDef)}
    check = structural.StructureTests('test_family_functions_iterate_only_through_the_union_helper')
    try: check.test_family_functions_iterate_only_through_the_union_helper()
    except AssertionError: print('AST direct_hidden_comprehension caught')
    else: print('AST direct_hidden_comprehension MISSED')
    structural.StructureTests.setUpClass()


def clean_variants():
    case = fresh()
    try:
        show('clean_baseline', case)
        case.files[FILL]['gamma']['contrasts'].reverse()
        case.files[VERD]['contrasts'].reverse()
        show('clean_keyed_lists_reordered', case)
        case.files[FILL]['gamma']['contrasts'][0]['j_per_token'] = None
        show('clean_registered_null', case)
    finally: case.tmp.cleanup()


def clean_alias_and_null():
    case = fresh()
    try:
        case.files[FILL]['gamma']['contrasts'][0]['claim_evaluation'] = {'direction': None}
        assert show('clean_registered_null_direction', case)[0] == 0
    finally: case.tmp.cleanup()
    t.MeterCase.setUpClass()
    case = t.MeterCase(); case.setUp()
    try:
        summary = next(row for row in case.lines() if row['line'] == 'machine_summary')
        for spelling in ('qwen3-1p7b', 'Qwen3-1.7B-4bit'):
            summary['model'] = spelling
            result = case.compare()
            print('CLEAN_MODEL_ALIAS', spelling, 'fails', case.fails(result),
                  'unbound', result['coverage']['unbound'],
                  'routing', [(r['key'], r['verdict']) for r in result['comparisons']
                              if r['family'] == 'routing_id' and 'machine_summary' in r['key']], flush=True)
    finally:
        case.case.tmp.cleanup()
        t.MeterCase.tearDownClass()
    case = fresh()
    try:
        verdict, fill = structural.v3_floor(case)
        show('clean_v3_arms', case)
        verdict['arm_gates'].reverse(); fill['arm_gates'].reverse()
        show('v3_arms_reordered', case)
    finally: case.tmp.cleanup()
    case = fresh()
    try:
        case.files[DISC]['floors'] = [{'line': 'floor_composition',
             'cell_id': 'd117-df-ph-decode-qwen3-1p7b-absolute', 'guarded_j': 42.0}]
        show('clean_raw_floor_cell_id', case)
        case.files[DISC]['floors'] = [{'line': 'floor_composition',
             'cell_id': 'd117-df-ph-decode-qwen3-1p7b-absolute-TYPO', 'guarded_j': 42.0}]
        show('bad_raw_floor_cell_id', case)
        # Suffix must still name a kind; a spurious prefix survives canonicalization.
        case.files[DISC]['floors'][0]['cell_id'] = 'TYPO-d117-df-ph-decode-qwen3-1p7b-absolute'
        _, result = show('bad_raw_floor_cell_id_prefix', case)
        print('RAW_ID_COVERAGE', result['coverage']['leaves'].get('disclosure:floors/floor_composition/cell_id'))
    finally: case.tmp.cleanup()


def structural_old_head_counterfactual():
    """Re-execute RC-CMP-5's named old-head test counterfactual without checkout writes."""
    source = subprocess.check_output(['git', 'show', 'e5ccf720b:scripts/compare_b5_recompute.py'], cwd=ROOT, text=True)
    old = types.ModuleType('rc_cmp5_old_subject')
    old.__file__ = str(ROOT / 'scripts/compare_b5_recompute.py')
    exec(compile(source, '<e5ccf720b comparator>', 'exec'), old.__dict__)
    from tests.independent_recompute import test_comparator, test_comparator_meter
    modules = (test_comparator, test_comparator_meter, t, structural)
    originals = [m.cmp for m in modules]
    class OldScript:
        def read_text(self): return source
    try:
        for module in modules: module.cmp = old
        with mock.patch.object(structural, 'SCRIPT', OldScript()):
            output = io.StringIO()
            result = unittest.TextTestRunner(stream=output, verbosity=1).run(
                unittest.defaultTestLoader.loadTestsFromModule(structural))
        print('RC_CMP5_NAMED_COUNTERFACTUAL e5ccf720b',
              json.dumps({'tests': result.testsRun, 'failures': len(result.failures),
                          'errors': len(result.errors), 'skipped': len(result.skipped)}), flush=True)
        print('COUNTERFACTUAL_NONPASS_TESTS', [test.id() for test, _ in result.failures + result.errors], flush=True)
        assert result.testsRun == 27 and not result.wasSuccessful()
    finally:
        for module, original in zip(modules, originals): module.cmp = original
        structural.StructureTests.setUpClass()


def main():
    print('HEAD', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), flush=True)
    manifest = json.loads((ROOT / '.codex-bridge/baselines/rc-cmp-sol-rev-3.json').read_text())
    payload = {k: v for k, v in manifest.items() if k != 'manifest_sha256'}
    digest = 'sha256:' + hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()
    assert digest == manifest['manifest_sha256'] == 'sha256:9ca78d5fc5cc68fa267ad513aeedf69d299d77da3d8425f739378eca0592ee86'
    print('BASELINE_DIGEST_VERIFIED', digest, flush=True)
    prior()
    structural_old_head_counterfactual()
    for function in (attack_shapes, attack_nested_identity, attack_duplicates, attack_collections_and_ast,
                     ast_guard_scope, ast_counterfactuals, clean_variants, clean_alias_and_null):
        print('\nSECTION', function.__name__, flush=True)
        try: function()
        except Exception: traceback.print_exc(); raise
    print('ALL_PROBES_COMPLETED', flush=True)

if __name__ == '__main__':
    if '--extra' in sys.argv:
        clean_alias_and_null()
        print('EXTRA_COMPLETED', flush=True)
    elif '--counterfactual' in sys.argv:
        structural_old_head_counterfactual()
        print('COUNTERFACTUAL_COMPLETED', flush=True)
    else:
        main()
