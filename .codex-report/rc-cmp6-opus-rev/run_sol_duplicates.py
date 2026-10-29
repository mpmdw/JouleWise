import os
src=open('.codex-report/rc-cmp6-opus-rev/probes.py').read().replace('/private/tmp/jwrc3-tmp','/tmp/rcopus_tmp/sol'); os.makedirs('/tmp/rcopus_tmp/sol',exist_ok=True)
ns={'__name__':'sol_probes','__file__':os.path.abspath('.codex-report/rc-cmp6-opus-rev/probes.py')}; exec(compile(src,ns['__file__'],'exec'),ns)
for before, after, label in (('"estimate":-1.25','"estimate":999999.0,"estimate":-1.25','duplicate_json_estimate_bad_first'),
                             ('"estimate":-1.25','"estimate":-1.25,"estimate":999999.0','duplicate_json_estimate_bad_last'),
                             ('"estimate":-1.25','"estimate":NaN,"estimate":-1.25','duplicate_json_nan_discarded')):
    case=ns['fresh']()
    try: ns['raw_cli'](case, ns['FILL'], before, after, label)
    finally: case.tmp.cleanup()
