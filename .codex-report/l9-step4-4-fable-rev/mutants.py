"""Mutants on the L9-STEP4-4 delta. Each applies to the worktree in argv[1], runs the step-4 modules and r14, and resets."""
import json, os, subprocess, sys
W = sys.argv[1]
ENV = dict(os.environ, TMPDIR='/tmp/jwfab4tmp', JW_B5_SYNTHETIC_ONLY='1', PYTHONDONTWRITEBYTECODE='1')
TEST = W + '/tests/b5_analysis/test_step4_reason_table.py'
JSON = W + '/configs/analysis/b5/step4_reason_classes.json'
INPUTS = W + '/joulewise/analysis_engine/inputs.py'
STEPS = W + '/joulewise/b5_analysis/steps.py'
FE = W + '/joulewise/floor_extraction.py'
R14 = W + '/tests/b5_analysis/test_floor_kept_units.py'

def sub(path, old, new, count=1):
    text = open(path).read()
    assert text.count(old) >= count and (count == 1 or text.count(old) == count), (path, old[:60], text.count(old))
    open(path, 'w').write(text.replace(old, new, count))

def json_edit(fn):
    """Parse, edit r3 only, and dump in the registered format (json.dumps indent=1 plus newline)."""
    table = json.load(open(JSON))
    fn(table)
    open(JSON, 'w').write(json.dumps(table, indent=1) + '\n')

def json_drop(code):
    json_edit(lambda t: t['r3'].remove(code))

def json_add(after, code):
    json_edit(lambda t: t.__setitem__('r3', sorted(t['r3'] + [code])))

def M1():  # JSON only: drop window_evidence_precheck_missing from r3
    json_drop('window_evidence_precheck_missing')
def M2():  # RULING and JSON: drop idle_window_suspect (partial revert of the ruling)
    json_drop('idle_window_suspect')
    sub(TEST, "'clock_bound_exceeds_quarter_window', 'idle_window_suspect',", "'clock_bound_exceeds_quarter_window',")
    sub(TEST, "    'idle_window_suspect':\n        ('joulewise/analysis_engine/inputs.py', 'reasons.append(\"idle_window_suspect\")', MEMBER_RULE),\n", '')
    sub(TEST, "PLAN_NAMED = {'window_evidence_precheck_missing', 'campaign_cooldown_evidence_missing', 'idle_window_suspect'}",
        "PLAN_NAMED = {'window_evidence_precheck_missing', 'campaign_cooldown_evidence_missing'}")
def M3():  # over-widen: idle_window_suspect_unknown (not plan-named) into r3, pins and PLAN_NAMED
    json_add('idle_window_suspect', 'idle_window_suspect_unknown')
    sub(TEST, "'clock_bound_exceeds_quarter_window', 'idle_window_suspect',", "'clock_bound_exceeds_quarter_window', 'idle_window_suspect', 'idle_window_suspect_unknown',")
    sub(TEST, "    'idle_window_suspect':\n        ('joulewise/analysis_engine/inputs.py', 'reasons.append(\"idle_window_suspect\")', MEMBER_RULE),\n",
        "    'idle_window_suspect':\n        ('joulewise/analysis_engine/inputs.py', 'reasons.append(\"idle_window_suspect\")', MEMBER_RULE),\n    'idle_window_suspect_unknown':\n        ('joulewise/analysis_engine/inputs.py', 'reasons.append(\"idle_window_suspect_unknown\")', MEMBER_RULE),\n")
    sub(TEST, "PLAN_NAMED = {'window_evidence_precheck_missing', 'campaign_cooldown_evidence_missing', 'idle_window_suspect'}",
        "PLAN_NAMED = {'window_evidence_precheck_missing', 'campaign_cooldown_evidence_missing', 'idle_window_suspect', 'idle_window_suspect_unknown'}")
def M4():  # widen with the claim-gate code paired_block_incomplete, fully pinned
    json_add('kept_units_below_minimum', 'paired_block_incomplete')
    sub(TEST, "'insufficient_members_after_exclusion', 'kept_units_below_minimum',", "'insufficient_members_after_exclusion', 'kept_units_below_minimum', 'paired_block_incomplete',")
    sub(TEST, "    'idle_window_suspect':\n        ('joulewise/analysis_engine/inputs.py', 'reasons.append(\"idle_window_suspect\")', MEMBER_RULE),\n",
        "    'idle_window_suspect':\n        ('joulewise/analysis_engine/inputs.py', 'reasons.append(\"idle_window_suspect\")', MEMBER_RULE),\n    'paired_block_incomplete':\n        ('joulewise/analysis_engine/inputs.py', 'stop_if_member_code_on_kept_unit(cid, run_id, \"paired_block_incomplete\")', MEMBER_RULE),\n")
    sub(TEST, "PLAN_NAMED = {'window_evidence_precheck_missing', 'campaign_cooldown_evidence_missing', 'idle_window_suspect'}",
        "PLAN_NAMED = {'window_evidence_precheck_missing', 'campaign_cooldown_evidence_missing', 'idle_window_suspect', 'paired_block_incomplete'}")
def M5():  # producer: the precheck appends the claim-gate code into a cell's reasons
    sub(INPUTS, '    if not isinstance(candidate, Mapping):\n        reasons.append("window_evidence_precheck_missing")\n',
        '    if not isinstance(candidate, Mapping):\n        reasons.append("window_evidence_precheck_missing")\n        reasons.append("paired_block_incomplete")\n')
def M6():  # producer: first stop site passes the code by keyword (still a stop; the guard cannot see it)
    sub(INPUTS, 'kept_units.stop_if_member_code_on_kept_unit(cid, run_id, "paired_block_incomplete")',
        'kept_units.stop_if_member_code_on_kept_unit(cid, run_id, code="paired_block_incomplete")', 1)
def M7():  # classifier drops the three plan-named codes at runtime
    sub(STEPS, 'return frozenset(json.loads(_STEP4_REASON_TABLE.read_bytes())["r3"])',
        'return frozenset(json.loads(_STEP4_REASON_TABLE.read_bytes())["r3"]) - {"window_evidence_precheck_missing", "campaign_cooldown_evidence_missing", "idle_window_suspect"}')
def M8():  # pin weakness: idle_window_suspect pinned to the _unknown emission site
    sub(TEST, "'reasons.append(\"idle_window_suspect\")', MEMBER_RULE", "'reasons.append(\"idle_window_suspect_unknown\")', MEMBER_RULE")
def M9():  # behavioral: the precheck forwards non-reducer raw reasons (data could carry a claim-gate code into a cell)
    sub(INPUTS, '        elif any(reason not in REDUCER_REASON_CODES for reason in raw_reasons):\n            reasons.append("window_evidence_precheck_missing")\n',
        '        elif False:\n            reasons.append("window_evidence_precheck_missing")\n')
def M10():  # outside the delta: the extractor stops filtering cooldown_cap_hit out of the forwarded precheck reasons
    sub(FE, '                if reason != "cooldown_cap_hit"\n', '                if True\n')
def M11():  # r14 expectation reverted to tooling for the precheck seam
    sub(R14, '(True, "window_evidence_precheck_missing", "extraction_cell_r3_refusal")', '(True, "window_evidence_precheck_missing", "extraction_cell_tooling_refusal")')
def M12():  # both kept-unit stop sites for paired_block_incomplete deleted (is the static proof vacuous?)
    sub(INPUTS, '                    try:\n                        kept_units.stop_if_member_code_on_kept_unit(cid, run_id, "paired_block_incomplete")\n                    except ValueError as exc:\n                        raise AnalysisInputError("member_code_on_kept_unit") from exc\n',
        '                    pass\n', 2)

MUTANTS = [M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, M12]
EXTRA = {'M9': ['tests.test_analysis_claims']}

def run(mods, timeout=900):
    p = subprocess.run([sys.executable, '-m', 'unittest'] + mods, cwd=W, env=ENV, capture_output=True, text=True, timeout=timeout)
    tail = [l for l in p.stdout.splitlines() + p.stderr.splitlines() if l.startswith(('Ran ', 'OK', 'FAILED'))]
    fails = [l for l in (p.stdout + p.stderr).splitlines() if l.startswith(('FAIL:', 'ERROR:'))]
    return p.returncode, tail, fails

def reset():
    subprocess.run(['git', 'checkout', '--', '.'], cwd=W, check=True)
    subprocess.run(['git', 'clean', '-fdq'], cwd=W, check=True)

only = sys.argv[2:] 
for m in MUTANTS:
    if only and m.__name__ not in only:
        continue
    reset(); m()
    diff = subprocess.run(['git', 'diff', '--stat'], cwd=W, capture_output=True, text=True).stdout.strip().splitlines()[-1]
    print('=== %s: %s' % (m.__name__, m.__doc__ or ''), flush=True)
    print('    diff:', diff, flush=True)
    rc, tail, fails = run(['tests.b5_analysis.test_step4_reason_table', 'tests.b5_analysis.test_step4_exit_classes'])
    print('    step4 modules: rc=%d %s' % (rc, ' | '.join(tail)), flush=True)
    for f in fails: print('      ', f, flush=True)
    rc2, tail2, fails2 = run(['tests.b5_analysis.test_floor_kept_units', '-k', 'r14'])
    print('    r14: rc=%d %s' % (rc2, ' | '.join(tail2)), flush=True)
    for f in fails2: print('      ', f, flush=True)
    for mod in EXTRA.get(m.__name__, []):
        rc3, tail3, fails3 = run([mod], timeout=1800)
        print('    %s: rc=%d %s' % (mod, rc3, ' | '.join(tail3)), flush=True)
        for f in fails3[:10]: print('      ', f, flush=True)
    print('    VERDICT:', 'KILLED' if (rc or rc2) else 'SURVIVED (step-4 modules + r14)', flush=True)
reset()
