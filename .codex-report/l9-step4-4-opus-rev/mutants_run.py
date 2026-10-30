import json, subprocess, sys, os, re
W = sys.argv[1]; OUT = sys.argv[2]
T = 'tests/b5_analysis/test_step4_reason_table.py'; E = 'tests/b5_analysis/test_step4_exit_classes.py'
J = 'configs/analysis/b5/step4_reason_classes.json'; ST = 'joulewise/b5_analysis/steps.py'
INP = 'joulewise/analysis_engine/inputs.py'; FE = 'joulewise/floor_extraction.py'; CB = 'joulewise/calibration_bracketing.py'
def jr3(fn):
    def f():
        p = os.path.join(W, J); t = json.load(open(p)); t['r3'] = sorted(fn(set(t['r3'])))
        open(p, 'w').write(json.dumps(t, indent=1) + '\n')
    return f
def sub(path, old, new, count=1):
    def f():
        p = os.path.join(W, path); s = open(p).read(); assert old in s, (path, old); open(p, 'w').write(s.replace(old, new, count))
    return f
def both(*fs):
    def f():
        for g in fs: g()
    return f
RULING_IDLE = ("'clock_bound_exceeds_quarter_window', 'idle_window_suspect',\n           'instrument_calibration_stale'",
               "'clock_bound_exceeds_quarter_window',\n           'instrument_calibration_stale'")
M = {
 'M1 JSON drops idle_window_suspect (RULING kept)': jr3(lambda s: s - {'idle_window_suspect'}),
 'M2 JSON+RULING drop idle_window_suspect consistently': both(jr3(lambda s: s - {'idle_window_suspect'}), sub(T, *RULING_IDLE)),
 'M3 JSON+RULING add paired_block_incomplete': both(jr3(lambda s: s | {'paired_block_incomplete'}),
     sub(T, "'window_evidence_precheck_missing'],", "'paired_block_incomplete', 'window_evidence_precheck_missing'],")),
 'M4 JSON+RULING+pin add cooldown_cap_hit (widen a forwarded reducer code)': both(jr3(lambda s: s | {'cooldown_cap_hit'}),
     sub(T, "'calibration_acceptance_bound_stale', 'campaign_cooldown_evidence_missing',", "'calibration_acceptance_bound_stale', 'campaign_cooldown_evidence_missing', 'cooldown_cap_hit',"),
     sub(T, "    'idle_window_suspect':\n", "    'cooldown_cap_hit':\n        ('joulewise/analysis_engine/inputs.py', 'reasons.append(\"cooldown_cap_hit\")', MEMBER_RULE),\n    'idle_window_suspect':\n")),
 'M5 JSON+RULING add idle_window_suspect_unknown': both(jr3(lambda s: s | {'idle_window_suspect_unknown'}),
     sub(T, "'window_evidence_precheck_missing'],", "'idle_window_suspect_unknown', 'window_evidence_precheck_missing'],")),
 'M6 classifier: r3 scan over all refused cells (p42 incl.) before p42 exit': sub(ST,
     "    targets = [cell for cell in refused if cell[\"cell_id\"] not in p42]\n",
     "    if any(reason in step4_r3_reasons() for cell in refused for reason in cell[\"refusal_reasons\"]):\n        return STEP4_CELL_R3_REFUSAL\n    targets = [cell for cell in refused if cell[\"cell_id\"] not in p42]\n"),
 'M7 classifier: r3 only checks first reason of each cell': sub(ST,
     "if any(reason in r3 for cell in targets for reason in cell[\"refusal_reasons\"])",
     "if any(cell[\"refusal_reasons\"][0] in r3 for cell in targets)"),
 'M8 inputs.py: paired_block_incomplete appended to precheck reasons': sub(INP,
     "            reasons.append(\"idle_window_suspect\")\n", "            reasons.append(\"idle_window_suspect\")\n            reasons.append(\"paired_block_incomplete\")\n"),
 'M9 inputs.py: fixed_n_plan_incomplete as a stop argument': sub(INP,
     'kept_units.stop_if_member_code_on_kept_unit(cid, run_id, "paired_block_incomplete")',
     'kept_units.stop_if_member_code_on_kept_unit(cid, run_id, "fixed_n_plan_incomplete")'),
 'M10 inputs.py: emission literal for campaign_cooldown_evidence_missing renamed via variable': sub(INP,
     'reasons.append("campaign_cooldown_evidence_missing")', 'reasons.append(_CCEM)'),
 'M11 calibration_bracketing.py (outside 11 modules, a cell-reason producer): emits paired_block_incomplete': sub(CB,
     'return finish(("calibration_acceptance_bound_stale",))', 'return finish(("calibration_acceptance_bound_stale", "paired_block_incomplete"))'),
 'M12 floor_extraction.py: forwarded precheck filter also drops window_evidence_precheck_missing': sub(FE,
     'if reason != "cooldown_cap_hit"', 'if reason not in ("cooldown_cap_hit", "window_evidence_precheck_missing")'),
}
TESTS = ['tests.b5_analysis.test_step4_reason_table', 'tests.b5_analysis.test_step4_exit_classes',
         'tests.b5_analysis.test_floor_kept_units.IndexedCliTests.test_r14_real_index_context_composition_with_registered_p42_exit']
env = dict(os.environ, TMPDIR='/tmp/l9rev_tmp', JW_B5_SYNTHETIC_ONLY='1', PYTHONDONTWRITEBYTECODE='1')
sel = sys.argv[3:] or list(M)
with open(OUT, 'a') as out:
    for name in M:
        if not any(name.startswith(k + ' ') for k in sel) and sel != list(M): continue
        subprocess.run(['git', 'checkout', '--', '.'], cwd=W, check=True)
        M[name]()
        r = subprocess.run([sys.executable, '-m', 'unittest', *TESTS], cwd=W, env=env, capture_output=True, text=True)
        fails = sorted(set(re.findall(r'^(?:FAIL|ERROR): (\S+) \((\S+)\)', r.stderr, re.M)))
        tail = r.stderr.strip().splitlines()[-1]
        out.write(f'## {name}\nrc={r.returncode} tail={tail}\n' + ''.join(f'  {a} ({b})\n' for a, b in fails) + '\n'); out.flush()
        print(name, r.returncode, tail, len(fails), flush=True)
    subprocess.run(['git', 'checkout', '--', '.'], cwd=W, check=True)
