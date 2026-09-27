# The exact script run at item 7 (cwd = <NIGHT_ROOT>/runs/instrument_validation), output in manual-battery-crosscheck.txt.
import json,glob,hashlib,os
rows=[];bad=0
for f in sorted(glob.glob('d079-epoch-25g83-derivation-w2-20260927-d*/instrument_evidence.json')):
    b=json.load(open(f))['battery_float']
    for ph in ('pre','post'):
        r=b[ph]; ok=(r['probe_error'] is False and r['passed'] is True and r['is_charging'] is False and r['external_connected'] is True and abs(r['instant_amperage_ma'])<=200 and r['exit_code']==0 and r['timed_out'] is False)
        raw=os.path.join(os.path.dirname(f),r['raw_path']); h=hashlib.sha256(open(raw,'rb').read()).hexdigest()
        ok = ok and h==r['raw_stdout_sha256']
        bad+= not ok
        print(r['slot'],ph,'probe_error=',r['probe_error'],'passed=',r['passed'],'charging=',r['is_charging'],'ext=',r['external_connected'],'inst_mA=',r['instant_amperage_ma'],'raw_sha_match=',h==r['raw_stdout_sha256'],'OK' if ok else 'FAIL')
print('readings',sum(1 for _ in glob.glob('d079-epoch-25g83-derivation-w2-20260927-d*/instrument_evidence.json'))*2,'failures',bad)
