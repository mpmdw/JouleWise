import sys,importlib.util,json
from pathlib import Path
R=Path(__file__).resolve().parent
sys.argv=['leafwalk',str(R.parents[1]),str(R/'e2e-literal'),str(R/'unused.json')]
s=importlib.util.spec_from_file_location('lw',R/'opus/leafwalk.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
for base,path,mode,value in [
 ('base',('records',0,'harvest','r_max_s'),'zero',0),
 ('base',('records',0,'harvest','anchor_shift_j'),'zero',0),
 ('base',('records',0,'harvest','battery_edge_j',0),'negative',-1),
 ('gaps',('records',3,'harvest','meter_gaps',0,'missing_samples'),'zero',0),
 ('gaps',('records',3,'harvest','meter_gaps'),'short',m.GAPS['records'][3]['harvest']['meter_gaps'][:1]),
 ('base',('records',0),'deleted',None)]:
 print(json.dumps(m.job((1,base,path,mode,value))))
