"""Positive, reversed poll order; zero stamps are covered in independent.py."""
from pathlib import Path
src=Path(__file__).with_name('independent.py')
exec(compile(src.read_text().split('cases=[]')[0],str(src),'exec'))
n=0
for i,rec in enumerate(D['records']):
 paths=[('records',i,'harvest','idle',s,k) for s in ('pre','post') for k in ('meter','battery')]+[('records',i,'harvest','battery_samples')]
 for path in paths:
  rows=D
  for k in path:rows=rows[k]
  for j,row in enumerate(rows):
   d=cp(D);o=d
   for k in path:o=o[k]
   o[j]['stamp_ns']=rows[j-1]['stamp_ns']-1 if j else rows[1]['stamp_ns']+1
   out=read(d);assert len(out['calls'])==8 and out['input_records']==d['records']
   assert 'UNDETERMINED' in classes(out).values()
   assert any('stamp_ns invalid time order' in r for r in out['reasons'])
   for k,v in bounds(out).items():assert v>=BB[k],(path,j,k)
   n+=1
print('positive reversed native poll rows',n,'PASS')
