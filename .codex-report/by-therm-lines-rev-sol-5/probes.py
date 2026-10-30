"""Independent synthetic probes; run from repository root with Python 3.13."""
import contextlib, copy, hashlib, io, json, os, random, shutil, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts import bytes_thermal_lines as t
from tests.test_bytes_thermal_lines import TrustArchive, ACC, HULL, ROS
from tests.b6 import test_bytes_p2_thermal_window as fx
from tests import test_harvest_b5_window as w
from joulewise.b6.session import accept_archive
JW = Path(t.__file__).resolve().parents[1]

def emit(name, ok, detail=''):
    print(name, bool(ok), *([detail] if detail != '' else []), flush=True)
    assert ok, (name, detail)

def put(p, v):
    p.write_text(json.dumps(v))

def codes(a):
    result = {}
    for r in json.loads((a / ACC).read_text())['excluding']:
        if r['scope'] == 'member': result.setdefault(r['run_id'], set()).add(r['code'])
    return result

def lexical():
    rng = random.Random(5985)
    corpus = ['0', 'true', 'null', '"abc"', '[]', '{}', '[0,{"a":true}]', '{"a":[1,2],"b":"x"}']
    alphabet = '{}[]:,"\\0129eE+-. abc\t\r\n'
    mismatch = []
    deliberate = 0
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d: raise ValueError("repeated key")
            d[k]=v
        return d
    for i in range(40000):
        raw = rng.choice(corpus)
        pos = rng.randrange(len(raw)+1)
        raw = raw[:pos] + rng.choice(alphabet) + raw[pos + rng.randrange(2):]
        try: json.loads(raw, object_pairs_hook=unique); std = True
        except ValueError: std = False
        try: t.lex(raw); strict = True
        except ValueError: strict = False
        if std != strict: mismatch.append((repr(raw), std, strict))
        if not strict:
            try: json.loads(raw); deliberate += 1
            except ValueError: pass
    emit('LEX_MUTATIONS_40000', not mismatch, mismatch[:5])
    emit('JSON_LOADS_ACCEPTS_DUPLICATES_TOOL_REFUSES', deliberate>0, deliberate)
    for depth in (0, 1, 7, 1000):
        raw = '['*depth + r'{"a":1,"\u0061":2}' + ']'*depth
        try: t.lex(raw); refused=False
        except ValueError: refused=True
        emit('DECODED_DUPLICATE_DEPTH_'+str(depth), refused)
    raw = '{"x":'+'['*10**6+'0'+']'*10**6+'}'
    emit('MILLION_DEPTH', len(t.lex(raw)) == 2000005)
    for raw in ('01','.5','1.','+1','NaN','Infinity','0x10','"\x00"',r'"\x20"',r'"\u12xz"',r'"\ud800"','\ufeff{}','{}{}'):
        try: t.lex(raw); refused=False
        except ValueError: refused=True
        emit('BAD_LEXEME_'+repr(raw), refused)
    emit('PRODUCER_ESCAPED_UNICODE', bool(t.lex(json.dumps({'😀': '\u2028é😀', 'x': 10**100}))))

def exports_and_roots(root):
    a = TrustArchive(root/'export-case', 'hull-p2', False, True)
    exp = a.root/'export'; exp.mkdir()
    (exp/'s.runs.csv').write_text('run_id,exclusion_codes,excluded\r\nr,,False\r\n')
    store = a.a/'withheld/private.csv'; store.write_text('run_id,exclusion_codes,excluded\r\na,,False\r\n')
    linked = a.root/'elsewhere.csv'; linked.symlink_to(store)
    # Locator escapes export; the store itself is a symlink into the archive.
    put(exp/'s.session.json', {'blinding':{'withheld':{'path':'../elsewhere.csv'}}})
    before = {str(p): p.read_bytes() for p in a.a.rglob('*') if p.is_file()}
    out = a.root/'out'
    rec = t.transform('hull-p2', a.a, out, exp)
    copied = out/'export/withheld/s.withheld.csv'
    emit('ESCAPING_LOCATOR_SYMLINK_STORE', len(rec['changes'])==1 and copied.is_file() and not copied.is_symlink())
    emit('EXPORT_SOURCE_BYTES_INTACT', before == {str(p):p.read_bytes() for p in a.a.rglob('*') if p.is_file()})
    emit('EXPORT_VIEW_VERIFIES', t.verify(out)==[])
    record = out/'thermal_line.json'; record.chmod(0o644)
    data=json.loads(record.read_text()); data['source_sha256']={'/':'0'*64}; put(record,data)
    t.verify(out)
    emit('ROOT_SLASH_INVALID', json.loads(record.read_text())['records.thermal_view_changed'])

def native(root):
    b=fx.HarvestEntryTests(); b.root=root
    win=b.window(1,name='mixed-native')
    jp=win.custody/'hazards/monitor/thermal.jsonl'
    rows=[json.loads(s) for s in jp.read_text().splitlines()]
    # New production-shaped case: clean first run, alternating inside/tail level 2,
    # and an error-marked level-9 read that must never count.
    for row in rows: row['values']['level']=0
    for idx,(run,*_) in enumerate(w.MEMBERS):
        if idx==0: continue
        rs,re=w.request_span_ns(run)
        stamp=(rs+re)//2 if idx%2 else re+15*fx.NS
        hit=copy.deepcopy(rows[0]); hit['finished']['monotonic_ns']=stamp; hit['started']['monotonic_ns']=stamp-1000
        hit['values']['level']=2; rows.append(hit)
    error=copy.deepcopy(rows[0]); error['values']['level']=9; error['error']={'type':'read_failed'}
    rs,re=w.request_span_ns(w.MEMBERS[0][0]); error['finished']['monotonic_ns']=(rs+re)//2; error['started']['monotonic_ns']=(rs+re)//2-1000; rows.append(error)
    rows.sort(key=lambda r:r['finished']['monotonic_ns'])
    for idx,row in enumerate(rows,1): row['seq']=idx
    jp.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    b.harvest(win)
    accept_archive(win.archive,json.loads(win.plan_path.read_text()),JW/'configs/b6/registration',plan_path=win.plan_path,replace_existing=True)
    rec=t.transform('request-end-p1',win.archive,root/'native-out')
    emit('NEW_NATIVE_ZERO_UNTRUSTED', all(not m['status'].startswith('not defined') for m in rec['member_statuses']),len(rec['member_statuses']))
    emit('NEW_NATIVE_ZERO_REPLAY_DISAGREEMENT', not any(n['code']=='records.thermal_hull_replay_disagrees' for n in rec['notices']))
    emit('NEW_NATIVE_VIEW_VERIFIES',t.verify(root/'native-out')==[])
    source_codes=codes(win.archive)
    # Choose a tail-only member whose request-end code is removed.
    target=next(c['run_id'] for c in rec['changes'] if c['action']=='removed')
    for kind in ('append-unsealed','mutate-reseal','remove-row'):
        a=root/kind; shutil.copytree(win.archive,a)
        j=a/'sources/night-custody/hazards/monitor/thermal.jsonl'
        if kind=='append-unsealed':
            row=copy.deepcopy(rows[-1]); row['values']['level']=0
            j.write_text(j.read_text()+json.dumps(row)+'\n')
        elif kind=='mutate-reseal':
            member=json.loads((a/'withheld/spans.json').read_text())['spans'][target]['member']
            rr=[json.loads(s) for s in j.read_text().splitlines()]
            hits=[r for r in rr if member[0]<=r['finished']['monotonic_ns']<=member[1] and r['values']['level']==2]
            emit('ONE_IN_HULL_NONZERO',len(hits)==1,target)
            hits[0]['values']['level']=0
            j.write_text(''.join(json.dumps(r)+'\n' for r in rr))
            seal=a/'derived/window_flags.json'; data=json.loads(seal.read_text())
            data['hazards']['thermal']['continuous']['journal']['sha256']=hashlib.sha256(j.read_bytes()).hexdigest(); put(seal,data)
        else:
            data=json.loads((a/ACC).read_text()); data['excluding']=[r for r in data['excluding'] if not(r.get('run_id')==target and r.get('code')==t.CODE)]; put(a/ACC,data)
        result=t.transform('request-end-p1',a,root/(kind+'-out'))
        status=next(m['status'] for m in result['member_statuses'] if m['run_id']==target)
        expected='equals registered line' if kind=='remove-row' else ('not defined (journal differs from the harvest\'s)' if kind=='append-unsealed' else 'not defined (journal does not reproduce the registered hull decision)')
        emit('REAL_CHAIN_'+kind,status==expected,status)
        if kind!='append-unsealed': emit('REAL_CHAIN_REPLAY_NOTICE_'+kind,any(n.get('run_id')==target and n['code']=='records.thermal_hull_replay_disagrees' for n in result['notices']))

if __name__=='__main__':
    lexical()
    with tempfile.TemporaryDirectory(prefix='sol5-probes-') as tmp:
        exports_and_roots(Path(tmp)); native(Path(tmp))
    w.tearDownModule()
    print('SUMMARY independent probes passed',flush=True)
