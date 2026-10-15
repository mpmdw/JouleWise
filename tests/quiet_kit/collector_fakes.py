"""Hardware-only in-process fakes that run the real segment executor."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
from types import SimpleNamespace

from joulewise.quiet_kit.paths import atomic_json, append, read_json
from joulewise.quiet_kit.collectors import collect
from .fakes import FakeHardware
from .fixtures import EPOCH, RAW, plist_stream, meter_stream, ps_bytes, synthetic_capture


class CollectorHardware(FakeHardware):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.repo=Path(__file__).resolve().parents[2]
        self.model_python='/fake/model-python'
        self.processes=FakeProcesses(self)
        self.events=[]
        self.captures=None
        self.sample_active=False

    def stamp(self):
        return {'epoch_s':EPOCH+self.time,'raw_s':RAW+self.time,'skew_s':0.}

    def ctx(self,directory=None):
        from joulewise.hazards.base import Context, Completed, Stamp
        hw=self
        class Clock:
            def stamp(self):
                return Stamp(round((EPOCH+hw.time)*1e9),round((RAW+hw.time)*1e9),round((RAW+hw.time)*1e9))
        def run(argv,timeout):
            # ps TIME has 10 ms resolution. At a tiny time scale a single
            # rounded tick would look like a whole busy core, so the quiet
            # hardware fake uses an exactly constant outside counter.
            return Completed(tuple(argv),0,ps_bytes(10.),b'')
        return Context(run=run,clocks=Clock(),raw_dir=directory)

    def sampler(self,directory,control):
        return FakeSampler(self,directory)

    def host_cpu(self):
        return [[0,0,1000,0]]

    def power(self,t):
        cpu=gpu=0.
        for event in self.events:
            if event['start'] <= t < event['end']:
                if event['kind']=='cpu': cpu+=event['duty']*5.
                if event['kind']=='gpu': gpu+=event['duty']*10.
        return .05+cpu,gpu

    def run_probe(self,argv,timeout):
        from joulewise.hazards.base import Completed
        server=argv[-1]
        return Completed(tuple(argv),0,f'+0.012 +/- 0.001 {server}\n'.encode(),b'')

    def collect(self,plan,attempt,scale,control,kind):
        self.collected.append(plan.test_id)
        self.control=control
        try:
            return collect(self,plan,attempt,scale,control,kind)
        finally:
            self.control=None

    def cleanup(self):
        self.cleanup_calls+=1
        return self.processes.cleanup()


class FakeSampler:
    def __init__(self,hw,directory):
        directory.mkdir(parents=True,exist_ok=True)
        self.hw,self.directory,self.start=hw,directory,hw.time
        self.closed=False
        assert not hw.sample_active,'sampler overlap'
        hw.sample_active=True

    def close(self):
        if self.closed:return read_json(self.directory/'sampler.json')
        hw=self.hw
        n=max(1,math.ceil((hw.time-self.start)/(.1*hw.scale)))
        dt=(hw.time-self.start)/n
        records=[]
        for i in range(n):
            t=self.start+(i+.5)*dt
            cpu,gpu=hw.power(t)
            records.append({'start_s':EPOCH+self.start+i*dt,'end_s':EPOCH+self.start+(i+1)*dt,
                            'cpu_power':cpu,'gpu_power':gpu,'ane_power':0.})
        (self.directory/'powermetrics.plist').write_bytes(plist_stream(records))
        doc={'first_record_endpoint_s':EPOCH+self.start+dt,'start':{'epoch_s':EPOCH+self.start,'raw_s':RAW+self.start},
             'span_s':hw.time-self.start,'cadence_median_ms':100.}
        atomic_json(self.directory/'sampler.json',doc)
        self.closed=True
        hw.sample_active=False
        return doc


class FakeChild:
    def __init__(self,manager,pid,argv,directory):
        self.manager,self.pid,self.argv,self.directory=manager,pid,argv,directory
        self.returncode=None
        self.start=manager.hw.time
        self.end=self.start
        self.event=None
        self.meter=None
        self.quiet_kit_stdout=directory/f'fake-child-{pid}.stdout'
        self.quiet_kit_stderr=directory/f'fake-child-{pid}.stderr'
        self.quiet_kit_stdout.write_bytes(b'')
        self.quiet_kit_stderr.write_bytes(b'')
        hw=manager.hw
        if 'joulewise.quiet_kit.loads' in argv:
            i=argv.index('joulewise.quiet_kit.loads')
            kind=argv[i+1]
            duty=float(argv[argv.index('--duty')+1])
            duration=float(argv[argv.index('--duration-s')+1])
            self.end+=duration
            self.event={'kind':kind,'duty':duty,'start':self.start,'end':self.end}
            hw.events.append(self.event)
        elif 'joulewise.quiet_kit.capture' in argv:
            self.end+=264*hw.scale
            out=Path(argv[argv.index('--out')+1])
            if hw.captures is None:hw.captures=synthetic_capture()
            raw,events,anchor,protocol=hw.captures
            (out/'raw').mkdir(parents=True,exist_ok=True)
            (out/'raw/powermetrics.plist').write_bytes(raw)
            (out/'events.jsonl').write_bytes(events)
            atomic_json(out/'raw/sampler.json',{'clock_anchor':anchor,'start':{'epoch_s':EPOCH,'raw_s':RAW}})
            atomic_json(out/'capture.json',{'protocol_id':protocol,'scale':1.,'cadence_median_ms':248. if '-c' in argv else 100.,
                                          'sampler_span_s':200.})
        elif 'joulewise' in argv and 'run' in argv:
            assert not hw.sample_active,'kit stream overlapped model stream'
            path=Path(argv[argv.index('run')+1])
            config=read_json(path)
            root=Path(argv[argv.index('--runs-dir')+1])/config['run_id']
            root.mkdir(parents=True,exist_ok=True)
            energy=10. if '1.5B' in config['model']['name'] else 20. if '1.7B' in config['model']['name'] else 40.
            atomic_json(root/'summary_metrics.json',{'status':'ok','phase_energy_j':{'prefill':energy,'decode':energy*2},
                'ttft_s':1.,'decode_latency_s':2.,'throughput_tokens_s':24.})
            self.end+=150*hw.scale
        elif any(a.endswith('km003c_monitor.py') for a in argv):
            self.meter=(Path(argv[argv.index('--out')+1]),Path(argv[argv.index('--stop-file')+1]))
            self.end=float('inf')

    def poll(self):
        hw=self.manager.hw
        if self.meter and self.meter[1].exists():
            path,_=self.meter
            n=max(2,round((hw.time-self.start)/.02))
            powers=[28.+sum(hw.power(self.start+i*.02)) for i in range(n)]
            path.write_bytes(meter_stream(powers,start_raw=RAW+self.start,start_epoch=EPOCH+self.start))
            self.end=hw.time
            self.meter=None
        if hw.time >= self.end and self.returncode is None:
            self.returncode=0
            if self.event:
                duration=self.end-self.start
                self.quiet_kit_stdout.write_text(json.dumps({'cpu_seconds':duration*self.event['duty']*(.01 if self.event['kind']=='gpu' else 1),
                                                             'elapsed_s':duration})+'\n')
        return self.returncode


class FakeProcesses:
    def __init__(self,hw):
        self.hw=hw
        self.children=[]

    def spawn(self,argv,directory,**kw):
        directory=Path(directory)
        directory.mkdir(parents=True,exist_ok=True)
        child=FakeChild(self,50000+len(self.children),list(argv),directory)
        self.children.append(child)
        append(directory/'children.jsonl',{'argv':list(argv),'pid':child.pid,'in_process_fake':True})
        return child

    def wait(self,child,control,timeout=3600):
        while child.poll() is None:
            control.wait(min(.1,max(.00001,child.end-self.hw.time)))
        return child.returncode

    def stop(self,child,**kw):
        child.poll()
        if child.returncode is None:
            child.returncode=-15
            if child.event:child.event['end']=self.hw.time
        return [{'pgid':child.pid,'gone':True,'in_process_fake':True}]

    def cleanup(self):
        return [r for c in self.children if c.returncode is None for r in self.stop(c)]
