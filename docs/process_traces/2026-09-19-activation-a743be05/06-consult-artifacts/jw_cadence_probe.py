"""PROPOSED BENCH DIAGNOSTIC. Live mode was NOT run by this consult.
Independent reader timestamps complete XML frames. Adapter hooks use the real
readiness/cursor/parser, plus diagnostic per-frame polling (not production).
--fixture reads retained bytes without launching powermetrics or sudo.
"""
import argparse,dataclasses,json,math,os,plistlib,re,select,signal,statistics,subprocess,sys,time
from pathlib import Path
REPO='/Users/edr/code/JouleWise-wt-consult-cadence'
sys.path.insert(0,REPO)
def stamp():
 a=time.monotonic_ns();w=time.time_ns();b=time.monotonic_ns()
 return {'mono_lo_ns':a,'wall_ns':w,'mono_hi_ns':b}
def emit(h,v): h.write(json.dumps(v)+'\n');h.flush()
def reader(out,mode):
 p=Path(out);buf=b'';i=0;f=None
 with (p/'arrivals.jsonl').open('x') as log:
  if mode=='stdout': f=(p/'raw.plist').open('xb',buffering=0)
  else:
   while not (p/'raw.plist').exists():
    if (p/'done').exists(): return
    time.sleep(.005)
   f=(p/'raw.plist').open('rb',buffering=0)
  try:
   while True:
    if mode=='stdout':
     chunk=os.read(0,65536)
     s=stamp()
     if chunk: f.write(chunk)
     elif not chunk: break
    else:
     chunk=f.read(65536);s=stamp()
     if not chunk:
      if (p/'done').exists(): break
      time.sleep(.005);continue
    buf+=chunk
    while b'</plist>' in buf:
     end=buf.index(b'</plist>')+len(b'</plist>');frame=buf[:end];buf=buf[end:]
     start=frame.find(b'<?xml');start=start if start>=0 else frame.find(b'<plist')
     doc=plistlib.loads(frame[start:]);i+=1
     emit(log,{'i':i,**s,'elapsed_ns':doc['elapsed_ns'],'native_timestamp':str(doc['timestamp']),'bytes':len(frame)})
   emit(log,{'reader_end':stamp(),'frames':i,'tail_bytes':len(buf)})
  finally:f.close()
def summarize(out):
 p=Path(out);r=[json.loads(x) for x in (p/'arrivals.jsonl').read_text().splitlines()];r=[x for x in r if 'i' in x]
 def d(v):
  if not v:return None
  v=sorted(v);return dict(zip(('min','median','p95','max'),[round(x,6) for x in (v[0],statistics.median(v),v[math.ceil(.95*len(v))-1],v[-1])]))
 e=[x['elapsed_ns']/1e6 for x in r];a=[(x['mono_lo_ns']+x['mono_hi_ns'])/2e6 for x in r]
 gaps=[y-x for x,y in zip(a,a[1:])]
 # Relative lag drift only: first complete-frame arrival is the reference,
 # not an absolute sample endpoint. Native plist dates have whole-second precision.
 drift=[0.];
 for gap,row in zip(gaps,r[1:]):drift.append(drift[-1]+gap-row['elapsed_ns']/1e6)
 value={'frames':len(r),'elapsed_ms':d(e),'arrival_gap_ms':d(gaps),'relative_lag_drift_ms':d(drift),'absolute_latency':'requires feasible clock-anchor endpoint interval; never subtract integer-second native dates as exact endpoints'}
 (p/'summary.json').write_text(json.dumps(value,indent=2));print(json.dumps(value))
def main():
 if len(sys.argv)>1 and sys.argv[1]=='_reader':reader(sys.argv[2],sys.argv[3]);return
 a=argparse.ArgumentParser();a.add_argument('--out',required=True);a.add_argument('--seconds',type=float,default=90);a.add_argument('--interval-ms',type=int,default=100);a.add_argument('--samplers',default='cpu_power,gpu_power,ane_power,thermal');a.add_argument('--mode',choices=['file','stdout'],default='file');a.add_argument('--adapter-hooks',action='store_true');a.add_argument('--hide-cpu-duty-cycle',action='store_true');a.add_argument('--load',choices=['idle','busy'],default='idle');a.add_argument('--binary',default='/usr/bin/powermetrics');a.add_argument('--fixture');args=a.parse_args()
 out=Path(args.out);assert out.resolve().is_relative_to(Path('/tmp').resolve()),'diagnostic output must be in /tmp';out.mkdir(exist_ok=False)
 from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter,parse_powermetrics_records
 from joulewise.clock import SystemClock
 raw=out/'raw.plist';command=['sudo','-n',args.binary,'-b','0','-i',str(args.interval_ms),'--samplers',args.samplers,'--format','plist']
 if args.hide_cpu_duty_cycle:command+=['--hide-cpu-duty-cycle']
 if args.mode=='file':command+=['-o',str(raw)]
 if args.fixture:
  command=[sys.executable,'-B','-c',"import pathlib,sys,time; fs=pathlib.Path(sys.argv[1]).read_bytes().split(b'\\0')[:12]; h=open(sys.argv[2],'wb',buffering=0) if sys.argv[2]!='-' else sys.stdout.buffer; [(h.write(f+b'\\0'),h.flush(),time.sleep(.025)) for f in fs]",args.fixture,str(raw) if args.mode=='file' else '-']
 meta={'argv':command,'args':vars(args),'fixture_only':bool(args.fixture),'spawn':stamp()};proc=None;watch=None;busy=None
 try:
  if args.load=='busy':
   busy=subprocess.Popen([sys.executable,'-B','-c','while True: pass'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(5)
  with (out/'stderr.txt').open('xb') as stderr:
   if args.mode=='file':watch=subprocess.Popen([sys.executable,'-B',__file__,'_reader',str(out),'file'])
   meta['spawn']=stamp()
   proc=subprocess.Popen(command,stdout=subprocess.PIPE if args.mode=='stdout' else subprocess.DEVNULL,stderr=stderr)
   if args.mode=='stdout':
    watch=subprocess.Popen([sys.executable,'-B',__file__,'_reader',str(out),'stdout'],stdin=proc.stdout);proc.stdout.close()
   deadline=time.monotonic()+args.seconds
   adapter=PowermetricsTelemetryAdapter(SystemClock());adapter._initialize_stream_cursor(raw);idx=0
   with (out/'adapter.jsonl').open('x') as log:
    if args.adapter_hooks:
     ready=adapter._wait_until_ready(proc,raw);meta['ready_ok']=ready.ok;meta['first_parse']=dataclasses.asdict(adapter._first_parse_stamp) if adapter._first_parse_stamp else None
     if ready.ok:meta['rollover_ok']=adapter._wait_for_native_rollover(proc,raw).ok
     meta['sampling_started']=dataclasses.asdict(adapter._clock.stamp())
    def poll():
     nonlocal idx
     if not raw.exists():return
     count=adapter._advance_stream_cursor(raw)
     while idx<count:
      start=stamp();frame=adapter._read_stream_frame_candidate(raw,index=idx)
      try: rs=parse_powermetrics_records(frame);error=None
      except ValueError as exc:rs=[];error=str(exc)
      emit(log,{'i':idx+1,'begin':start,'end':stamp(),'count':len(rs),'error':error});idx+=1
    while proc.poll() is None and time.monotonic()<deadline:
     if args.adapter_hooks:poll()
     time.sleep(.05)
    meta['sampling_stopped']=dataclasses.asdict(adapter._clock.stamp())
    if proc.poll() is None:proc.terminate()
    try:proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
     meta['cleanup']='sampler supervisor did not exit; bench must reconcile owned sampler';raise
    (out/'done').write_text('sampler_exited\n');watch.wait(timeout=10)
    if args.adapter_hooks:poll()
   meta['sampler_exit']=proc.returncode;meta['reader_exit']=watch.returncode
   if raw.exists():
    meta['offline_parse_start']=stamp()
    try:meta['offline_adapter_frames']=len(parse_powermetrics_records(raw.read_bytes()))
    except ValueError as exc:meta['offline_adapter_error']=str(exc)
    meta['offline_parse_end']=stamp()
    meta['post_parse']=dataclasses.asdict(adapter._clock.stamp())
  if watch.returncode==0:summarize(out)
 finally:
  if proc is not None and proc.poll() is None:proc.terminate()
  (out/'done').touch()
  if watch is not None and watch.poll() is None:
   try:watch.wait(timeout=5)
   except subprocess.TimeoutExpired:watch.terminate();watch.wait()
  if busy is not None:busy.terminate();busy.wait()
  meta['end']=stamp();(out/'meta.json').write_text(json.dumps(meta,indent=2))
if __name__=='__main__':main()
