"""L9-STEP4-5: rerun every L9-STEP4-4 reviewer mutant (Opus O*, Fable F*) plus new ones (N*) on the -5 head.

Usage: python3.13 mutants.py <worktree> [names...]. Each mutant is applied to the
worktree, the four step-4 targets run, and the worktree is reset.
"""
import json, os, re, subprocess, sys
W = sys.argv[1]
ENV = dict(os.environ, TMPDIR='/tmp/l9s5tmp', JW_B5_SYNTHETIC_ONLY='1', PYTHONDONTWRITEBYTECODE='1')
T = 'tests/b5_analysis/test_step4_reason_table.py'
J = 'configs/analysis/b5/step4_reason_classes.json'
ST = 'joulewise/b5_analysis/steps.py'
INP = 'joulewise/analysis_engine/inputs.py'
FE = 'joulewise/floor_extraction.py'
CB = 'joulewise/calibration_bracketing.py'
DC = 'joulewise/dominance_closeout.py'
R14 = 'tests/b5_analysis/test_floor_kept_units.py'
CLI = 'scripts/extract_detection_floors.py'
TESTS = ['tests.b5_analysis.test_step4_reason_table', 'tests.b5_analysis.test_step4_exit_classes',
         'tests.b5_analysis.test_step4_member_codes',
         'tests.b5_analysis.test_floor_kept_units.IndexedCliTests.test_r14_real_index_context_composition_with_registered_p42_exit']


def sub(path, old, new, count=1, first=False):
    """Replace all `count` occurrences, or with first=True only the first (as Opus M11 did)."""
    def f():
        p = os.path.join(W, path); s = open(p).read()
        assert first and s.count(old) >= 1 or s.count(old) == count, (path, old[:70], s.count(old))
        open(p, 'w').write(s.replace(old, new, 1) if first else s.replace(old, new))
    return f

def append(path, text):
    def f():
        with open(os.path.join(W, path), 'a') as fh: fh.write(text)
    return f

def jr3(fn):
    def f():
        p = os.path.join(W, J); t = json.load(open(p)); t['r3'] = sorted(fn(set(t['r3'])))
        open(p, 'w').write(json.dumps(t, indent=1) + '\n')
    return f

def both(*fs):
    def f():
        for g in fs: g()
    return f

PIN_IDLE = "    'idle_window_suspect':\n        ('joulewise/analysis_engine/inputs.py', 'reasons.append(\"idle_window_suspect\")', MEMBER_RULE),\n"
PLAN = "PLAN_NAMED = {'window_evidence_precheck_missing', 'campaign_cooldown_evidence_missing', 'idle_window_suspect'}"
STOP = 'kept_units.stop_if_member_code_on_kept_unit(cid, run_id, "paired_block_incomplete")'
FILTER = '                if reason != "cooldown_cap_hit"\n'
M = {
 # Opus L9-STEP4-4-OPUS-REV mutants_run.py
 'O1 JSON drops idle_window_suspect (RULING kept)': jr3(lambda s: s - {'idle_window_suspect'}),
 'O2 JSON+RULING drop idle_window_suspect': both(jr3(lambda s: s - {'idle_window_suspect'}),
     sub(T, "'clock_bound_exceeds_quarter_window', 'idle_window_suspect',\n           'instrument_calibration_stale'",
         "'clock_bound_exceeds_quarter_window',\n           'instrument_calibration_stale'")),
 'O3 JSON+RULING add paired_block_incomplete': both(jr3(lambda s: s | {'paired_block_incomplete'}),
     sub(T, "'window_evidence_precheck_missing'],", "'paired_block_incomplete', 'window_evidence_precheck_missing'],")),
 'O4 JSON+RULING+pin add cooldown_cap_hit': both(jr3(lambda s: s | {'cooldown_cap_hit'}),
     sub(T, "'calibration_acceptance_bound_stale', 'campaign_cooldown_evidence_missing',",
         "'calibration_acceptance_bound_stale', 'campaign_cooldown_evidence_missing', 'cooldown_cap_hit',"),
     sub(T, "    'idle_window_suspect':\n", "    'cooldown_cap_hit':\n        ('joulewise/analysis_engine/inputs.py', 'reasons.append(\"cooldown_cap_hit\")', MEMBER_RULE),\n    'idle_window_suspect':\n")),
 'O5 JSON+RULING add idle_window_suspect_unknown': both(jr3(lambda s: s | {'idle_window_suspect_unknown'}),
     sub(T, "'window_evidence_precheck_missing'],", "'idle_window_suspect_unknown', 'window_evidence_precheck_missing'],")),
 'O6 classifier checks r3 before the p42 exit': sub(ST,
     "    targets = [cell for cell in refused if cell[\"cell_id\"] not in p42]\n",
     "    if any(reason in step4_r3_reasons() for cell in refused for reason in cell[\"refusal_reasons\"]):\n        return STEP4_CELL_R3_REFUSAL\n    targets = [cell for cell in refused if cell[\"cell_id\"] not in p42]\n"),
 'O7 classifier checks only the first reason': sub(ST,
     "if any(reason in r3 for cell in targets for reason in cell[\"refusal_reasons\"])",
     "if any(cell[\"refusal_reasons\"][0] in r3 for cell in targets)"),
 'O8 precheck appends paired_block_incomplete': sub(INP,
     "            reasons.append(\"idle_window_suspect\")\n", "            reasons.append(\"idle_window_suspect\")\n            reasons.append(\"paired_block_incomplete\")\n"),
 'O9 fixed_n_plan_incomplete as a stop argument': sub(INP, STOP, STOP.replace('paired_block_incomplete', 'fixed_n_plan_incomplete'), 2),
 'O10 campaign_cooldown_evidence_missing emission made indirect': sub(INP,
     'reasons.append("campaign_cooldown_evidence_missing")', 'reasons.append(_CCEM)'),
 'O11 calibration_bracketing.py emits paired_block_incomplete beside its pinned code': sub(CB,
     'return finish(("calibration_acceptance_bound_stale",))', 'return finish(("calibration_acceptance_bound_stale", "paired_block_incomplete"))', first=True),
 'O12 forwarding filter also drops window_evidence_precheck_missing': sub(FE,
     'if reason != "cooldown_cap_hit"', 'if reason not in ("cooldown_cap_hit", "window_evidence_precheck_missing")'),
 'O12b forwarding filter also drops idle_window_suspect': sub(FE,
     'if reason != "cooldown_cap_hit"', 'if reason not in ("cooldown_cap_hit", "idle_window_suspect")'),
 'O12c forwarding filter also drops campaign_cooldown_evidence_missing': sub(FE,
     'if reason != "cooldown_cap_hit"', 'if reason not in ("cooldown_cap_hit", "campaign_cooldown_evidence_missing")'),
 # Fable L9-STEP4-4-FABLE-REV mutants.py
 'F1 JSON only drops window_evidence_precheck_missing': jr3(lambda s: s - {'window_evidence_precheck_missing'}),
 'F2 RULING, JSON, pin and PLAN_NAMED drop idle_window_suspect': both(jr3(lambda s: s - {'idle_window_suspect'}),
     sub(T, "'clock_bound_exceeds_quarter_window', 'idle_window_suspect',", "'clock_bound_exceeds_quarter_window',"),
     sub(T, PIN_IDLE, ''), sub(T, PLAN, PLAN.replace(", 'idle_window_suspect'", ''))),
 'F3 idle_window_suspect_unknown into RULING, JSON, pins and PLAN_NAMED': both(jr3(lambda s: s | {'idle_window_suspect_unknown'}),
     sub(T, "'clock_bound_exceeds_quarter_window', 'idle_window_suspect',", "'clock_bound_exceeds_quarter_window', 'idle_window_suspect', 'idle_window_suspect_unknown',"),
     sub(T, PIN_IDLE, PIN_IDLE + PIN_IDLE.replace('idle_window_suspect', 'idle_window_suspect_unknown')),
     sub(T, PLAN, PLAN[:-1] + ", 'idle_window_suspect_unknown'}")),
 'F4 paired_block_incomplete into RULING, JSON, pins and PLAN_NAMED': both(jr3(lambda s: s | {'paired_block_incomplete'}),
     sub(T, "'insufficient_members_after_exclusion', 'kept_units_below_minimum',", "'insufficient_members_after_exclusion', 'kept_units_below_minimum', 'paired_block_incomplete',"),
     sub(T, PIN_IDLE, PIN_IDLE + "    'paired_block_incomplete':\n        ('joulewise/analysis_engine/inputs.py', 'kept_units.stop_if_member_code_on_kept_unit(cid, run_id, \"paired_block_incomplete\")', MEMBER_RULE),\n"),
     sub(T, PLAN, PLAN[:-1] + ", 'paired_block_incomplete'}")),
 'F5 precheck appends paired_block_incomplete when the candidate is missing': sub(INP,
     '    if not isinstance(candidate, Mapping):\n        reasons.append("window_evidence_precheck_missing")\n',
     '    if not isinstance(candidate, Mapping):\n        reasons.append("window_evidence_precheck_missing")\n        reasons.append("paired_block_incomplete")\n'),
 'F6 first stop site passes the code by keyword': sub(INP, STOP, STOP.replace('"paired', 'code="paired'), 2),
 'F7 classifier drops the three plan-named codes at runtime': sub(ST,
     'return frozenset(json.loads(_STEP4_REASON_TABLE.read_bytes())["r3"])',
     'return frozenset(json.loads(_STEP4_REASON_TABLE.read_bytes())["r3"]) - {"window_evidence_precheck_missing", "campaign_cooldown_evidence_missing", "idle_window_suspect"}'),
 'F8 pin idle_window_suspect to the _unknown emission site': sub(T,
     "'reasons.append(\"idle_window_suspect\")', MEMBER_RULE", "'reasons.append(\"idle_window_suspect_unknown\")', MEMBER_RULE"),
 'F9 precheck forwards non-reducer stored reasons': sub(INP,
     '        elif any(reason not in REDUCER_REASON_CODES for reason in raw_reasons):\n',
     '        elif False:\n'),
 'F10 extractor stops filtering cooldown_cap_hit': sub(FE, FILTER, '                if True\n'),
 'F11 r14 expects tooling again for the precheck subcase': sub(R14,
     '(True, "window_evidence_precheck_missing", "extraction_cell_r3_refusal")',
     '(True, "window_evidence_precheck_missing", "extraction_cell_tooling_refusal")'),
 'F12 both kept-unit stop sites for paired_block_incomplete deleted': sub(INP,
     '                    try:\n                        ' + STOP + '\n                    except ValueError as exc:\n                        raise AnalysisInputError("member_code_on_kept_unit") from exc\n',
     '                    pass\n', 2),
 # New in L9-STEP4-5
 'N1 claim-gate literal in a module outside the eleven, not at a pinned site': append(DC,
     '\n_SYN_L9_STEP4_5 = ("fixed_n_plan_incomplete",)\n'),
 'N2 claim-gate literal in the extractor CLI': append(CLI, '\n_SYN_L9_STEP4_5 = "paired_block_incomplete"\n'),
 'N3 pin campaign_cooldown_evidence_missing to the window_evidence_precheck_missing site': sub(T,
     "'reasons.append(\"campaign_cooldown_evidence_missing\")', MEMBER_RULE", "'reasons.append(\"window_evidence_precheck_missing\")', MEMBER_RULE"),
 'N4 pin text is a fragment of the real statement': sub(T,
     "'refusals.append(\"kept_units_below_minimum\")'", "'append(\"kept_units_below_minimum\")'"),
 'N5 precheck missing-root case emits idle_window_suspect_unknown instead': sub(INP,
     '    if not isinstance(candidate, Mapping):\n        reasons.append("window_evidence_precheck_missing")\n',
     '    if not isinstance(candidate, Mapping):\n        reasons.append("idle_window_suspect_unknown")\n'),
}

def reset():
    subprocess.run(['git', 'checkout', '--', '.'], cwd=W, check=True)
    subprocess.run(['git', 'clean', '-fdq'], cwd=W, check=True)

sel = sys.argv[2:]
for name, apply in M.items():
    if sel and name.split()[0] not in sel:
        continue
    reset(); apply()
    r = subprocess.run([sys.executable, '-m', 'unittest', *TESTS], cwd=W, env=ENV, capture_output=True, text=True, timeout=1800)
    fails = sorted(set(re.findall(r'^(?:FAIL|ERROR): (\S+) \(([^)]+)\)', r.stderr, re.M)))
    tail = [l for l in r.stderr.splitlines() if l.startswith(('Ran ', 'OK', 'FAILED'))]
    print('## %s\n   rc=%d %s -> %s' % (name, r.returncode, ' | '.join(tail), 'KILLED' if r.returncode else 'SURVIVED'), flush=True)
    for test, where in fails:
        print('     %s (%s)' % (test, where.rsplit('.', 1)[0]), flush=True)
reset()
