"""Supplement independent CLI walk with explicit affected-boundary assertions."""
from pathlib import Path
import sys,copy
P=Path(__file__).resolve().parent;sys.path.insert(0,'/workspace/JouleWise')
from scripts import bytes_stream_test as p
# Reuse only our independent raw-data setup/walk, not its CLI mutation loop.
ns={'__file__':str(P/'walk.py')}
exec(compile((P/'walk.py').read_text().split('jobs=')[0],str(P/'walk.py'),'exec'),ns)
base,paths=ns['base'],ns['paths'];n=0
for path,value in paths:
 if path[0]=='scan' or path[2]=='receipt':expected=('rails','gpu','dc','rest')
 else:
  key=path[3]
  if key=='energy_j':stream=path[4];expected={'rails':('rails','rest'),'gpu':('gpu',),'meter':('dc','rest'),'battery':('dc','rest')}[stream]
  elif key=='idle':expected={'rails':('rails','rest'),'gpu':('gpu',),'meter':('dc','rest'),'battery':('dc','rest')}[path[5]]
  elif key=='capture_stack':expected=('rails','rest')
  elif key=='anchor_shift_j':expected=('rails','gpu','rest')
  elif key=='tau_s':expected=('rails','gpu','dc','rest')
  else:expected=('dc','rest')
 for mode in (['delete','null','type','nan'] if type(value) in (int,float) else ['delete','null','type']):
  d=copy.deepcopy(base);parent=d
  for key in path[:-1]:parent=parent[key]
  key=path[-1]
  if mode=='delete':del parent[key]
  else:parent[key]={'null':None,'type':{},'nan':float('nan')}[mode]
  o=p.read_known_bytes(d['records'],d['scan'])
  assert set(o['boundaries'])=={'rails','gpu','dc','rest'}
  for beta in expected:assert o['boundaries'][beta]['class']=='UNDETERMINED',(path,mode,beta)
  n+=1
print('explicit affected-class checks',n,'PASS')
