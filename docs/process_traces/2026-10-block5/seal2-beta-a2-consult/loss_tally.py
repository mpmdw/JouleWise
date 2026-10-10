# Prints tallies of (status word, admission word) per attempt, and the local start minute of each member
# whose status is not "succeeded". No ids, no energies, no durations.
import json,sys,collections,time,re
WORD=re.compile(r'^[A-Za-z_.\-]{1,48}$')
w=lambda s: s if isinstance(s,str) and WORD.match(s) else 'other'
for a in sys.argv[1:]:
    ms=json.load(open(a+'/withheld/member-assessments.json'))['members']
    c=collections.Counter((w(m.get('status')),w(m.get('admission_decision'))) for m in ms.values() if m.get('present'))
    print(a.rsplit('harvest-',1)[1]); 
    for k,v in sorted(c.items()): print('  ',k,v)
    lost=sorted((m.get('run_started_epoch_s') or 0, w(m.get('status')), w(m.get('admission_decision'))) for m in ms.values() if m.get('present') and m.get('status')!='succeeded')
    for t,s,ad in lost: print('   lost at', time.strftime('%H:%M',time.localtime(t)), s, ad)
