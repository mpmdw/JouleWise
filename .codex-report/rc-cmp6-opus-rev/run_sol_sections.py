import sys, runpy, traceback, io
sys.argv=['probes.py']
src=open('.codex-report/rc-cmp6-opus-rev/probes.py').read().replace('/private/tmp/jwrc3-tmp','/tmp/rcopus_tmp/sol'); import os; os.makedirs('/tmp/rcopus_tmp/sol',exist_ok=True); ns={'__name__':'sol_probes','__file__':os.path.abspath('.codex-report/rc-cmp6-opus-rev/probes.py')}; exec(compile(src,ns['__file__'],'exec'),ns)
for name in ('attack_shapes','attack_nested_identity','attack_duplicates','attack_collections_and_ast','ast_guard_scope','ast_counterfactuals','clean_variants','clean_alias_and_null'):
    print('\nSECTION', name, flush=True)
    try: ns[name]()
    except BaseException as e: print('SECTION_STOPPED', name, type(e).__name__, str(e)[:300], flush=True); traceback.print_exc(limit=2, file=sys.stdout)
