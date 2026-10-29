import sys,json,subprocess
from pathlib import Path
from copy import deepcopy
R=Path(__file__).resolve().parent;ROOT=R.parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(R/'sol/sol3/adapted'))
from scripts import bytes_stream_test as p
from scan_cases import receipts,worked5
base=receipts(worked5,True);n=0
for i in range(len(base)):
 for key in ('bytes_per_read','repeats','start_ns','end_ns','clock_resolution_s','clock_tick_num_ns','clock_tick_den'):
  d=deepcopy(base);d[i][key]=10**400;o=p.knee_scan(d)
  assert len(o['receipts'])==66 and o['status']=='knee not found' and key in o['reason'];n+=1
 for key in ('start_ns','end_ns'):
  d=deepcopy(base);d[i][key]=d[i]['end_ns'] if key=='start_ns' else d[i]['start_ns']
  o=p.knee_scan(d);assert len(o['receipts'])==66 and o['status']=='knee not found';n+=1
print('scan huge integers / nonpositive intervals',n,'PASS')
