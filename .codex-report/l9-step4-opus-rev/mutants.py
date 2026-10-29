"""Mutation run for L9-STEP4-OPUS-REV. Applies one textual mutant at a time to a
scratch worktree (argv[1]) and runs the step-4 class tests plus the driver
acceptance tests. Synthetic data only."""
import os, subprocess, sys
from pathlib import Path
WT = Path(sys.argv[1])
S, D, J = 'joulewise/b5_analysis/steps.py', 'joulewise/b5_analysis/dry_run.py', 'configs/analysis/b5/dry_run_refusal_classes.json'
MUTANTS = {
 'C1 subset->equality (base rule)': (S, 'if refused <= p42 else', 'if refused == p42 else'),
 'C2 drop empty-refused guard': (S, '    if not refused:\n        return STEP4_EXIT_WITHOUT_REFUSED_CELL\n', ''),
 'C3 drop membership-refusal branch': (S, '    if omitted:\n        return STEP4_SPEC_MEMBERSHIP_REFUSED\n', ''),
 'C4 p42 ignores kind': (S, 'if cell["kind"] in ("absolute", "comparative")\n           and', 'if'),
 'C5 p42 by substring': (S, '"p42" in cell["condition_family_id"].split("-")', '"p42" in cell["condition_family_id"]'),
 'C6 p42 taken from report cells': (S, 'p42 = {cell["cell_id"] for cell in wanted if', 'p42 = {cell["cell_id"] for cell in cells if "p42" in cell["cell_id"] or'),
 'C7 drop exit!=1 guard': (S, '    if exit_status != 1:\n        return "refused"\n', ''),
 'C8 non-bool check removed': (S, '    if any(type(cell.get("extractable")) is not bool for cell in cells):\n        return STEP4_EXTRACTABLE_NOT_BOOLEAN\n', ''),
 'C9 superset instead of subset': (S, 'if refused <= p42 else', 'if refused >= p42 else'),
 'C10 dup check only report': (S, 'if len(ids) != len(set(ids)) or len(spec_ids) != len(set(spec_ids)):', 'if len(ids) != len(set(ids)):'),
 'C11 malformed spec -> refused': (S, '        return STEP4_SPEC_MALFORMED', '        return "refused"'),
 'T1 outcome code registered as tooling': (J, '    "dominance_ratio_zero_denominator",\n    "floor_cell_not_extractable"\n', '    "dominance_ratio_zero_denominator"\n'),
 'D1 drop driver pass-through': (D, "            elif exit_status==1 and classification!='refused': code=classification\n", ''),
 'D2 pass-through ignores exit status': (D, "elif exit_status==1 and classification!='refused': code=classification", "elif classification!='refused': code=classification"),
 'D3 pass-through includes refused': (D, "elif exit_status==1 and classification!='refused': code=classification", "elif exit_status==1: code=classification"),
 'D4 no break after non-ok window': (D, "        if records[-1].status!='ok': break\n    return records\n\n\ndef step_5", "    return records\n\n\ndef step_5"),
 'D5 p42 keeps stderr code': (D, "if classification=='p42_floor_cells_only': code,registered=None,classification", "if classification=='p42_floor_cells_only': registered=classification"),
 'D6 outcome treated as p42 exit': (D, "if classification=='p42_floor_cells_only': code,registered=None,classification", "if classification in ('p42_floor_cells_only','floor_cell_not_extractable'): code,registered=None,'p42_floor_cells_only'"),
}
TESTS = ['tests.b5_analysis.test_step4_exit_classes', 'tests.b5_analysis.test_dry_run.DriverAcceptanceTests',
         'tests.b5_analysis.test_dry_run.DriverPrimitiveTests.test_T18_class_table_is_sorted_disjoint_and_keeps_S7_split']
env = dict(os.environ, JW_B5_SYNTHETIC_ONLY='1', PYTHONDONTWRITEBYTECODE='1')
survivors = 0
for name, (rel, old, new) in MUTANTS.items():
    path = WT/rel; original = path.read_text()
    assert original.count(old) == 1, (name, original.count(old))
    path.write_text(original.replace(old, new))
    try:
        p = subprocess.run([sys.executable, '-m', 'unittest', *TESTS], cwd=WT, env=env, capture_output=True, text=True, timeout=1200)
    finally:
        path.write_text(original)
    tail = [l for l in p.stderr.splitlines() if l.startswith(('Ran ', 'OK', 'FAILED'))]
    killed = p.returncode != 0; survivors += not killed
    print(f"{'KILLED ' if killed else 'SURVIVED'} {name}: {' '.join(tail)}", flush=True)
print('survivors:', survivors)
