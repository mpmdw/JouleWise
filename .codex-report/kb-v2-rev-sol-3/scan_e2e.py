"""Real stream -> disk receipts -> real scan CLI, with 125/3-ns endpoint clocks."""
import json,math,random,subprocess,sys,tempfile
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts import bytes_stream_test as p
from tests.test_bytes_stream_test import worked5,dram_only,synthetic_clock
ref,ver=p.registered_stack();stack={**ref,**ver}
def late(s):
 return worked5(2**26)+(s-2**26)/1e12 if 2**26<s<=2**27 else worked5(s)
class MX:
 uint8='uint8'
 def __init__(self,td,phase,epoch,mode):self.td,self.phase,self.epoch,self.mode,self.n=td,phase,epoch,mode,0
 def ones(self,shape,dtype):return object()
 def sum(self,data):self.n+=1;return object()
 def eval(self,v):pass
 def synchronize(self):pass
 def clock(self):
  ticks=self.epoch+math.floor(self.phase+self.n*self.td*1e9/(125/3))
  return ticks*125//3 if self.mode=='floor' else (ticks*125+1)//3
for mode in ('floor','nearest'):
 for name,model in [('worked',worked5),('dram',dram_only),('late',late)]:
  rng=random.Random(8);calls=[]
  with tempfile.TemporaryDirectory() as tmp:
   for size in (2**k for k in range(14,36)):
    td=model(size);n=math.floor(2/td)
    for j in range(3):
     mx=MX(td,rng.random(),rng.randrange(24_000_000_000,48_000_000_000),mode)
     metadata={**synthetic_clock(),'clock_ns_conversion':mode}
     with patch.object(p,'collect_stack',return_value=stack),patch.object(p,'clock_metadata',return_value=metadata):
      r=p.stream(size,n,device='synthetic',idle_s=0,settle_s=0,mx=mx,clock_ns=mx.clock,sleep=lambda _:None)
     path=Path(tmp)/f'{size}-{j}.json';path.write_text(json.dumps(r,allow_nan=False));calls.append(json.loads(path.read_text()))
   path=Path(tmp)/'scan.json';path.write_text(json.dumps(calls,allow_nan=False))
   cli=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/bytes_stream_test.py'),'scan',str(path)],check=True,capture_output=True,text=True)
   out=json.loads(cli.stdout)
   print(mode,name,'calls',len(out['receipts']),'pairs',len(out['pairs']),'status',out['status'],'K',out['K'],'candidate',out['candidate_K'],'reason',out.get('reason'),'checks',out['arm_checks'])
   assert out['K']==(2**26 if name=='worked' else None)
   if name=='late':assert out['candidate_K']==2**28
