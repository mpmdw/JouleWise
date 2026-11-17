"""Emit an F2 remainder queue only after a kit-bound piece-1 PASS record.

This does not issue or commit it. Builder verification calls make_queue() in a
temporary directory. No queue b is published in this builder commit (RL-169a).
"""
import argparse
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def make_queue(name):
    if name not in ('f2-inst-02','f2-inst-03'): raise ValueError('unknown F2 kit')
    q=json.loads((HERE/name/'queue-a.json').read_text())
    q['queue_id']='cq-'+name+'-b'; q['spans']=[]
    for seq,item in enumerate(json.loads((HERE/name/'items.json').read_text())[1:],1):
        q['spans'].append({'seq':seq,'span_id':item['span'],'block_id':name,
            'kit':{'path':name+'/'+name+'.v1.1.json','sha256':item['kit_sha']},
            'legs':item['legs'],'attempt':1,'not_before':item['date'],'rerun_of':None})
    return q

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('kit',choices=['f2-inst-02','f2-inst-03'])
    p.add_argument('--hand-read-record',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); record=json.loads(a.hand_read_record.read_text())
    item=json.loads((HERE/a.kit/'items.json').read_text())[0]
    if record.get('verdict')!='PASS' or record.get('kit_sha256')!=item['kit_sha'] or record.get('span')!=item['span']:
        raise SystemExit('STOP: own kit-bound piece-1 PASS required; queue b stays uncommitted')
    with a.output.open('x') as f: f.write(json.dumps(make_queue(a.kit),indent=1)+'\n')
