import subprocess, sys, json, pathlib, os
W=pathlib.Path('/tmp/jwmut')
STEPS=W/'joulewise/b5_analysis/steps.py'; DRV=W/'joulewise/b5_analysis/dry_run.py'; TBL=W/'configs/analysis/b5/dry_run_refusal_classes.json'
FAST=['tests.b5_analysis.test_step4_exit_classes',
 'tests.b5_analysis.test_dry_run.DriverAcceptanceTests.test_T8_p42_only_exception_and_target_refusal',
 'tests.b5_analysis.test_dry_run.DriverAcceptanceTests.test_T8b_step4_exit_names_its_class',
 'tests.b5_analysis.test_dry_run.DriverPrimitiveTests.test_T18_class_table_is_sorted_disjoint_and_keeps_S7_split']
M=[
 ('C1 subset->equality', STEPS, 'if refused <= p42 else', 'if refused == p42 else'),
 ('C2 swap p42/outcome', STEPS, 'return STEP4_P42_FLOOR_CELLS_ONLY if refused <= p42 else STEP4_FLOOR_CELL_NOT_EXTRACTABLE', 'return STEP4_FLOOR_CELL_NOT_EXTRACTABLE if refused <= p42 else STEP4_P42_FLOOR_CELLS_ONLY'),
 ('C3 drop empty-refused check', STEPS, '    if not refused:\n        return STEP4_EXIT_WITHOUT_REFUSED_CELL\n', ''),
 ('C4 drop membership check', STEPS, '    if omitted:\n        return STEP4_SPEC_MEMBERSHIP_REFUSED\n', ''),
 ('C5 dup ids -> cell-set code', STEPS, '        return STEP4_CELL_IDS_DUPLICATED\n    if set(ids)', '        return STEP4_CELL_SET_DIFFERS\n    if set(ids)'),
 ('C6 p42 = every spec cell (ignore family)', STEPS, 'and "p42" in cell["condition_family_id"].split("-")}', '}'),
 ('C7 drop kind filter', STEPS, 'if cell["kind"] in ("absolute", "comparative")\n           and "p42"', 'if "p42"'),
 ('C8 substring family match', STEPS, '"p42" in cell["condition_family_id"].split("-")', '"p42" in cell["condition_family_id"]'),
 ('C9 non-bool extractable -> report_malformed', STEPS, '        return STEP4_EXTRACTABLE_NOT_BOOLEAN', '        return STEP4_REPORT_MALFORMED'),
 ('C10 spec malformed -> report malformed', STEPS, '        return STEP4_SPEC_MALFORMED', '        return STEP4_REPORT_MALFORMED'),
 ('C11 exit!=1 -> report_malformed', STEPS, '    if exit_status != 1:\n        return "refused"', '    if exit_status != 1:\n        return STEP4_REPORT_MALFORMED'),
 ('C12 p42 from report cells (truthy any)', STEPS, 'refused <= p42 else', 'refused <= set(ids) else'),
 ('C13 refused uses truthiness', STEPS, 'if cell["extractable"] is False}', 'if not cell["extractable"]}'),
 ('C14 membership check after p42 test', STEPS, '    if omitted:\n        return STEP4_SPEC_MEMBERSHIP_REFUSED\n', '') ,
 ('D1 drop driver elif', DRV, '            elif exit_status==1 and classification!=\'refused\': code=classification\n', ''),
 ('D2 driver registers every exit-1 as p42', DRV, "elif exit_status==1 and classification!='refused': code=classification", "elif exit_status==1 and classification!='refused': code,registered=None,'p42_floor_cells_only'"),
 ('D3 driver passes code for p42 too', DRV, "if classification=='p42_floor_cells_only': code,registered=None,classification", "if classification=='p42_floor_cells_only': code,registered=classification,classification"),
 ('D4 driver drops dead exit-0 branch', DRV, "            elif classification=='refused' and exit_status==0: exit_status=2\n", ''),
 ('D5 driver no break after step-4 refusal', DRV, "        if records[-1].status!='ok': break\n    return records\n\n\ndef step_5", "    return records\n\n\ndef step_5"),
 ('T1 outcome code moved to tooling', TBL, '    "extraction_spec_membership_refused",\n', '    "extraction_spec_membership_refused",\n    "floor_cell_not_extractable",\n'),
 ('T1b (with T1) remove from outcome', TBL, ',\n    "floor_cell_not_extractable"\n  ]', '\n  ]'),
 ('T2 drop exit_without_refused_cell from table', TBL, '    "extraction_exit_without_refused_cell",\n', ''),
]
env=dict(os.environ,JW_B5_SYNTHETIC_ONLY='1',PYTHONDONTWRITEBYTECODE='1',TMPDIR='/tmp/jwtmp')
def restore(): subprocess.run(['git','-C',str(W),'checkout','--','.'],check=True)
def run():
    p=subprocess.run([sys.executable,'-m','unittest',*FAST],cwd=W,env=env,capture_output=True,text=True)
    last=[l for l in p.stderr.splitlines() if l.startswith(('OK','FAILED','Ran'))]
    return p.returncode,' | '.join(last[-2:])
restore(); print('baseline', run())
rows=[]
i=0
while i<len(M):
    name,path,old,new=M[i]; group=[M[i]]; i+=1
    while i<len(M) and M[i][0].startswith(name.split()[0]+'b'): group.append(M[i]); i+=1
    for n,p,o,nw in group:
        t=p.read_text(); assert t.count(o)==1,(n,t.count(o)); p.write_text(t.replace(o,nw))
    rc,summary=run(); restore()
    rows.append((name,'KILLED' if rc else 'SURVIVED',summary)); print(rows[-1],flush=True)
json.dump(rows,open(sys.argv[1],'w'),indent=1)
