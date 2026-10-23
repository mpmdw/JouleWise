"""Production controller/reducer over synthetic hardware and a model launch.

Only collection observers, the runtime launch and the child telemetry source
are replaced. Consumers and all evidence derivation/authentication are real.
"""
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import sys
import subprocess
import time
import zlib
import shutil
import csv
import plistlib
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

from joulewise import adapters
from joulewise.adapters.mock_runtime import MockRuntimeAdapter
from joulewise.controller import run_benchmark
from joulewise.reduce import reduce_bundle
from joulewise.schemas import BenchmarkConfig, CampaignPolicy
from tests.test_p2038_production_path import (
    RateFitFixtureClock, CampaignPositiveTelemetryAdapter, LogicalDrainTimer,
    claim_admission_fixture, load_v3_production_fixture,
)
from tests.b5_analysis.support_s10.calibration import self_consistent_calibration
from joulewise.powermetrics_fiducial import PROTOCOL_ID
from joulewise.clock import ClockStamp
from joulewise.interfaces import RuntimeEvent
from joulewise.uncertainty_evidence import resolve_clock_evidence_deriver, stamp_from_mapping
from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter, parse_powermetrics_records, anchor_records_from_powermetrics, samples_from_records, decode_rich_telemetry
from joulewise.uncertainty_evidence import derive_idle_drift_evidence
from joulewise.idle_admission import evaluate_cpu_idle_admission

PROCESS = Path(__file__).with_name("fake_powermetrics_process.py")
PHYSICS_CACHE={}
EPOCH_ORIGIN=1791600000.


def collect_job(job):
    """One foreground process-pool task, using the real controller/reducer."""
    global PROCESS
    root,config,base,policy,calibration_dir,config_path,process=job
    PROCESS=Path(process)
    started=time.monotonic()
    bundle,summary=collect(root,config,base_s=base,policy_path=policy,
        calibration_dir=calibration_dir,config_path=config_path)
    if summary.status.value!='succeeded':
        raise ValueError('synthetic collection failed: '+config['run_id']+'; '+str(summary.to_dict()))
    summary=coarsen_member(bundle)
    return str(bundle),time.monotonic()-started


def clone_job(job):
    source,target,config,shift,power=job
    started=time.monotonic()
    bundle,summary=clone_member(source,target,config,shift_s=shift,power_w=power)
    if summary.status.value!='succeeded':raise ValueError('cloned member failed: '+config['run_id'])
    return str(bundle),time.monotonic()-started


def coarsen_idle(bundle,metadata):
    """Persist short synthetic idle captures and rederive every admission fact."""
    from joulewise.adapters.powermetrics import idle_window_gpu_quality
    from joulewise.idle_dependence import duration_weighted_mean_and_sample_variance
    names=('powermetrics_idle.plist','powermetrics_idle_post.plist')
    parsed={}
    for name in names:
        path=bundle/'raw'/name
        if not path.exists():continue
        original=[plistlib.loads(r) for r in path.read_bytes().split(b'\0') if r.strip()]
        kept=[];elapsed=0
        for n,row in enumerate(original):
            elapsed+=row['elapsed_ns']
            if n==0 or n==len(original)-1 or (n+1)%10==0:
                row['elapsed_ns']=elapsed;elapsed=0
                for rail in ('cpu','gpu','ane'):
                    row['processor'][rail+'_energy']=round(row['processor'][rail+'_power']*row['elapsed_ns']/1e9)
                kept.append(row)
        raw=b'\0'.join(plistlib.dumps(r) for r in kept);path.write_bytes(raw)
        parsed[name]=(raw,parse_powermetrics_records(raw))
    if names[0] not in parsed:return
    admission=metadata['environment_admission'];attempt=admission['attempts'][-1]
    raw,records=parsed[names[0]]
    rich=decode_rich_telemetry(raw,timestamp_anchor_s=attempt['start_s'])
    (bundle/'rich_telemetry_idle.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rich))
    mean,variance=duration_weighted_mean_and_sample_variance(
        [r.combined_power_w for r in records],[r.elapsed_ns/1e9 for r in records])
    quality=idle_window_gpu_quality(rich)
    baseline=metadata['idle_baseline']
    baseline.update(duration_s=sum(r.elapsed_ns for r in records)/1e9,sample_count=len(records),
        power_w_mean=mean,power_w_stddev=variance**.5,**quality)
    attempt['baseline']=dict(baseline)
    policy=CampaignPolicy.from_mapping(json.loads(Path(metadata['campaign_policy']['source']).read_bytes()))
    attempt['cpu_admission']=evaluate_cpu_idle_admission(rich,policy.idle_admission_extension.cpu_criteria,
        gpu_admitted=attempt['gpu_admitted'])
    if names[1] in parsed:
        post_raw,post=parsed[names[1]]
        idle,guard,bound=derive_idle_drift_evidence(pre_power_w=[r.combined_power_w for r in records],
            post_power_w=[r.combined_power_w for r in post],pre_power_w_mean=mean,
            pre_idle_window_suspect=quality['idle_window_suspect'],
            post_idle_window_suspect=idle_window_gpu_quality(decode_rich_telemetry(post_raw))['idle_window_suspect'],
            calibration_guard=metadata['uncertainty_evidence']['idle_drift_guard'])
        metadata['uncertainty_evidence'].update(idle_drift=idle,idle_drift_guard=guard)
        if bound is None:metadata.pop('idle_drift_bound_w',None)
        else:metadata['idle_drift_bound_w']=bound


def coarsen_member(bundle, *, anchor_method=None):
    """Coalesce synthetic idle frames; retain the separate admission capture.

    The continuous stream has the same elapsed intervals and power. All clock
    evidence, CSV samples, rich rows and the summary are then derived afresh.
    No retained admission frame or configuration is edited.
    """
    bundle=Path(bundle);path=bundle/'raw/powermetrics.plist'
    rows=[plistlib.loads(r) for r in path.read_bytes().split(b'\0') if r.strip()]
    retained=[];elapsed=0
    for n,row in enumerate(rows):
        elapsed+=row['elapsed_ns']
        # The harvest's cadence and per-phase sample gates require these
        # one-second bins. Keep native one-second measured records intact.
        if n==0 or n==len(rows)-1 or row['elapsed_ns']==1000000000 or (n+1)%10==0:
            row['elapsed_ns']=elapsed;elapsed=0
            for rail in ('cpu','gpu','ane'):
                row['processor'][rail+'_energy']=round(row['processor'][rail+'_power']*row['elapsed_ns']/1e9)
            retained.append(row)
    raw=b'\0'.join(plistlib.dumps(r) for r in retained);path.write_bytes(raw)
    metadata=json.loads((bundle/'metadata.json').read_bytes())
    coarsen_idle(bundle,metadata)
    old=metadata['uncertainty_evidence']
    evidence,point=resolve_clock_evidence_deriver(anchor_method or old['clock_anchor']['method'])(
        stamps={k:stamp_from_mapping(v) for k,v in old['clock_anchor']['clock_stamps'].items()},
        records=anchor_records_from_powermetrics(parse_powermetrics_records(raw)))
    if point is None:raise ValueError('coalesced synthetic stream clock unresolved')
    old['schema_version']=evidence['schema_version']
    old['clock_anchor']=evidence['clock_anchor'];old['sample_phase']=evidence['sample_phase']
    metadata['clock_anchor_bound_s']=evidence['clock_anchor']['effective_clock_anchor_bound_s']
    for key in ('marker_to_first_sample_phase_bound_s','marker_to_last_sample_phase_bound_s'):
        metadata[key]=evidence['sample_phase'][key]
    put(bundle/'metadata.json',metadata)
    with (bundle/'power_trace.csv').open('w',newline='') as handle:
        writer=csv.writer(handle);writer.writerow(['timestamp_s','power_w','source','rail','interval_start_s','interval_end_s'])
        for s in samples_from_records(parse_powermetrics_records(raw,first_record_endpoint_s=point)):
            writer.writerow([s.timestamp_s,s.power_w,s.source,s.rail,s.interval_start_s,s.interval_end_s])
    (bundle/'rich_telemetry.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n'
        for r in decode_rich_telemetry(raw,first_record_endpoint_s=point)))
    summary=reduce_bundle(bundle,reducer_version='0.5.2',_instrument_calibration_physics_cache=PHYSICS_CACHE)
    put(bundle/'summary_metrics.json',summary.to_dict())
    return summary


def put(path, value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")


def clone_member(source, target, config, *, shift_s, power_w):
    """Synthesize hardware primary bytes, then use the real reducer.

    A controller-produced seed supplies lifecycle structure. All changed
    primary traces, clock evidence, rich telemetry, and summaries are rebuilt;
    no consumer function or authentication result is replaced.
    """
    source=Path(source);target=Path(target);shutil.copytree(source,target)
    source_id=source.name;run_id=config['run_id']
    def shift(value,key=''):
        if isinstance(value,dict):return {k:shift(v,k) for k,v in value.items()}
        if isinstance(value,list):return [shift(v,key) for v in value]
        if isinstance(value,str):return value.replace(source_id,run_id)
        if type(value) in (int,float):
            if key in ('timestamp_s','epoch_s','wall_time_s','captured_at_s','start_s','end_s','capture_start_s','capture_end_s',
                       'monotonic_before_s','monotonic_after_s'):
                return value+shift_s
            if key in ('monotonic_ns','monotonic_before_ns','monotonic_after_ns'):return value+int(shift_s*1e9)
        return value
    raw_config=(json.dumps(BenchmarkConfig.from_mapping(config).to_dict(),indent=2,sort_keys=True)+'\n').encode()
    (target/'config.json').write_bytes(raw_config)
    metadata=json.loads((target/'metadata.json').read_bytes())
    instrument=metadata.pop('instrument_calibration')
    metadata=shift(metadata);metadata['instrument_calibration']=instrument
    metadata['run_id']=run_id;metadata['config_sha256']=hashlib.sha256(raw_config).hexdigest()
    for name in ('events.jsonl','outputs/tokens.jsonl','outputs/suite_items.jsonl'):
        path=target/name
        if path.exists():
            rows=[shift(json.loads(r)) for r in path.read_bytes().splitlines() if r.strip()]
            path.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows))
    for path in (target/'raw').glob('*.ioreg'):
        import re
        path.write_bytes(re.sub(rb'("UpdateTime" = )([0-9]+)',
            lambda m:m[1]+str(int(m[2])+int(shift_s)).encode(),path.read_bytes()))
    for path in (target/'raw').glob('*.plist'):
        documents=[plistlib.loads(r) for r in path.read_bytes().split(b'\0') if r.strip()]
        for document in documents:
            document['timestamp']+=timedelta(seconds=shift_s)
            if path.name=='powermetrics.plist' and document['processor']['cpu_power']>1000:
                processor=document['processor'];processor['cpu_power']=power_w*1000.;processor['combined_power']=power_w*1000.
                processor['cpu_energy']=round(power_w*1000.*document['elapsed_ns']/1e9)
        path.write_bytes(b'\0'.join(plistlib.dumps(d) for d in documents))
    raw=(target/'raw/powermetrics.plist').read_bytes()
    records=parse_powermetrics_records(raw)
    previous=metadata['uncertainty_evidence']
    stamps={k:stamp_from_mapping(v) for k,v in previous['clock_anchor']['clock_stamps'].items()}
    evidence,point=resolve_clock_evidence_deriver(previous['clock_anchor']['method'])(
        stamps=stamps,records=anchor_records_from_powermetrics(records))
    if point is None:raise ValueError('cloned primary clock is unresolved')
    previous['clock_anchor']=evidence['clock_anchor'];previous['sample_phase']=evidence['sample_phase']
    metadata['clock_anchor_bound_s']=evidence['clock_anchor']['effective_clock_anchor_bound_s']
    for key in ('marker_to_first_sample_phase_bound_s','marker_to_last_sample_phase_bound_s'):
        metadata[key]=evidence['sample_phase'][key]
    corrected=parse_powermetrics_records(raw,first_record_endpoint_s=point)
    samples=samples_from_records(corrected)
    with (target/'power_trace.csv').open('w',newline='') as handle:
        writer=csv.writer(handle);writer.writerow(['timestamp_s','power_w','source','rail','interval_start_s','interval_end_s'])
        for sample in samples:writer.writerow([sample.timestamp_s,sample.power_w,sample.source,sample.rail,sample.interval_start_s,sample.interval_end_s])
    for path in target.glob('rich_telemetry*.jsonl'):
        if path.name=='rich_telemetry.jsonl':
            rows=decode_rich_telemetry(raw,first_record_endpoint_s=point)
        else:rows=[shift(json.loads(r)) for r in path.read_bytes().splitlines() if r.strip()]
        path.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows))
    put(target/'metadata.json',metadata)
    summary=reduce_bundle(target,reducer_version='0.5.2',_instrument_calibration_physics_cache=PHYSICS_CACHE)
    put(target/'summary_metrics.json',summary.to_dict())
    return target,summary


def calibration(directory, base_s, lag_s, *, os_build="25G83"):
    evidence, raw, events = self_consistent_calibration(
        first_endpoint_s=base_s+.05, protocol_id=PROTOCOL_ID, signal_lag_s=lag_s,os_build=os_build)
    evidence['bindings']['powermetrics_sha256']=hashlib.sha256(PROCESS.read_bytes()).hexdigest()
    evidence['validation_id']=Path(directory).name
    evidence['binding_evidence']={
        'schema_version':'joulewise.instrument_binding_evidence.v1',
        'binding_vector_sha256':hashlib.sha256(json.dumps(evidence['bindings'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'powermetrics_binary':{'path':str(PROCESS),'sha256':evidence['bindings']['powermetrics_sha256']},
        'power_policy':{'id':'ac_high_power'},
    }
    directory=Path(directory);(directory/'raw').mkdir(parents=True)
    (directory/'raw/powermetrics.plist').write_bytes(raw)
    (directory/'events.jsonl').write_bytes(events)
    (directory/'power_trace.csv').write_bytes(b'timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n')
    put(directory/'instrument_evidence.json',evidence)
    put(directory/'manifest.json',{'schema_version':'joulewise.instrument_validation_manifest.v1',
        'validation_id':evidence['validation_id'],'protocol_id':PROTOCOL_ID,'pulse_count':evidence['pulse_count'],
        'artifacts':{n:hashlib.sha256((directory/n).read_bytes()).hexdigest() for n in (
            'raw/powermetrics.plist','events.jsonl','power_trace.csv','instrument_evidence.json')}})
    return evidence


class FixtureClock(RateFitFixtureClock):
    def now(self):return self._now

    def stamp(self):
        value=super().stamp()
        offset=self._base_s-EPOCH_ORIGIN
        return replace(value,monotonic_before_s=value.monotonic_before_s+offset,
                       monotonic_after_s=value.monotonic_after_s+offset)


class BatteryClock:
    def __init__(self,base_s):self.base=base_s;self.calls=0;self.current=base_s
    def stamp(self):
        self.current=self.base+(0. if self.calls<3 else 120.)+self.calls*.000001
        self.calls+=1
        return ClockStamp(epoch_s=self.current,monotonic_before_s=self.current-EPOCH_ORIGIN+100.,
            monotonic_after_s=self.current-EPOCH_ORIGIN+100.000001,wall_resolution_s=1e-6,monotonic_resolution_s=1e-6)
    def now(self):return self.current


class Runtime(MockRuntimeAdapter):
    name='mlx'

    def run_workload(self, config, context=None):
        expectation=config.workload_profile.prompt_token_expectation
        self.ids=None
        if expectation is not None:
            pack='d117_floor_qwen3-8b_v5' if '8B' in config.model.name else 'd117_floor_qwen3-1p7b_v5'
            pin=Path(__file__).resolve().parents[3]/'configs/campaigns'/pack/'prefill_pin/prefill_prompt_pin.json'
            self.ids=json.loads(pin.read_bytes())['prompt_token_ids']
        result=super().run_workload(config,context)
        count=self._prompt_tokens(config)
        events=list(result.events)
        start=events[0].timestamp_s
        events=[RuntimeEvent(start,'phase_start','tokenize','synthetic tokenization started',{}),
            RuntimeEvent(start,'phase_end','tokenize','synthetic tokenization completed',{'prompt_tokens':count}),
            *[replace(event,metadata={**event.metadata,'prompt_tokens':count})
              if event.event_type=='phase_start' and event.phase=='prefill' else event for event in events]]
        return replace(result,events=events,workload_provenance={**result.workload_provenance,'sampler':{'name':'greedy','temperature':0.0}})

    def _prompt_tokens(self, config):
        return len(self.ids) if self.ids is not None else super()._prompt_tokens(config)

    def _prompt_token_ids(self, count):
        return self.ids if self.ids is not None else super()._prompt_token_ids(count)

    def run_suite(self, *args, **kwargs):
        result=super().run_suite(*args,**kwargs)
        return replace(result,workload_provenance={**result.workload_provenance,'sampler':{'name':'greedy','temperature':0.0}})


class Registry:
    def resolve_runtime(self, config, clock):
        return Runtime(clock), None
    def resolve_transport(self, config):
        return adapters.resolve_transport(config)
    def resolve_telemetry(self, config, clock):
        timer=LogicalDrainTimer()
        return TimedTelemetry(clock, executable=str(PROCESS),
            privilege_prefix=(sys.executable,),drain_monotonic=timer.monotonic,drain_sleep=timer.sleep),None


class TimedTelemetry(PowermetricsTelemetryAdapter):
    def measure_idle(self, config, context=None):
        baseline = super().measure_idle(config, context)
        # The synthetic child already emitted this interval. Advance the
        # collection clock to its endpoint, just as wall time would advance
        # while the real observer waits for these primary records.
        if context is not None:
            rows = [json.loads(line) for line in
                    (context.bundle_path/'rich_telemetry_idle.jsonl').read_text().splitlines()]
            self._clock._now = max(row['timestamp_s'] for row in rows)
        return baseline


def collect(root, config, *, base_s=1791649400., lag_s=.021331, policy_path=None,
            calibration_dir=None, config_path=None):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    cal=Path(calibration_dir) if calibration_dir is not None else root/'calibration'
    if calibration_dir is None:calibration(cal,base_s-500.,lag_s)
    policy,binding,preflight,snapshot,_=claim_admission_fixture()
    snapshot['power'].update(adapter_watts=140,adapter_description='140W synthetic adapter')
    if policy_path is not None:
        raw=Path(policy_path).read_bytes();policy=CampaignPolicy.from_mapping(json.loads(raw))
        binding.update(policy_id=policy.policy_id,policy_version=policy.policy_version,
                       sha256=hashlib.sha256(raw).hexdigest(),source=str(policy_path))
        from joulewise.environment import evaluate_environment_policy
        preflight.update(policy_sha256=binding['sha256'],evaluation=evaluate_environment_policy(snapshot,policy.environment_guard))
    profile=json.loads(PROCESS.with_name('paired_clock_native_records.json').read_bytes())
    clock=FixtureClock(base_s,profile)
    battery_clock=BatteryClock(base_s)
    increment=.73331 if config['run_id'].startswith('d117') else .003331
    power_w=7.331+(zlib.crc32(config['run_id'].encode())%13)*increment
    guard={'display_power_state':'all_asleep','screensaver_engaged':False,'screensaver_module':'Ventura',
        'screensaver_delay_s':1200,'hid_idle_s':1200.,'power_source':'AC Power','adapter_wattage_w':140.,
        'adapter_description':'140W synthetic adapter','errors':{},
        'power':{'adapter_watts':140.,'adapter_description':'140W synthetic adapter','external_connected':True}}
    def battery_probe(argv):
        raw=('+-o AppleSmartBattery  <class AppleSmartBattery, id 0x1>\n  {\n'
             '    "ExternalConnected" = Yes\n    "IsCharging" = No\n    "InstantAmperage" = 0\n'
             f'    "UpdateTime" = {int(battery_clock.now())}\n    "Amperage" = 0\n    "Voltage" = 12733\n'
             '    "Temperature" = 3031\n    "FullyCharged" = Yes\n    "CurrentCapacity" = 100\n'
             '    "AppleRawCurrentCapacity" = 7331\n    "AppleRawMaxCapacity" = 7331\n  }\n').encode()
        return subprocess.CompletedProcess(argv,0,raw,b'')
    with mock.patch.dict(os.environ,{'P2038_FAKE_POWERMETRICS_MODE':'normal',
        'P2038_FAKE_POWERMETRICS_STATE':str(root/'state'),'P2038_V3_FIXTURE_EPOCH_S':str(base_s),
        'S10_POWER_W':str(power_w)}), \
        mock.patch('joulewise.controller.collect_environment_guard_observation',side_effect=lambda **kw:dict(guard)), \
        mock.patch('joulewise.adapters.mock_runtime.PREFILL_SECONDS_PER_PROMPT_TOKEN',.004331), \
        mock.patch('joulewise.adapters.mock_runtime.DECODE_SECONDS_PER_OUTPUT_TOKEN',.017331), \
        mock.patch.object(sys,'argv',['joulewise','run',str(config_path)] if config_path else ['joulewise']):
        return run_benchmark(BenchmarkConfig.from_mapping(config),root,clock,
            registry=Registry(),reducer=reduce_bundle,environment_snapshot=snapshot,
            campaign_policy=policy,campaign_policy_binding=binding,campaign_environment_preflight=preflight,
            instrument_calibration_dir=cal,instrument_power_policy='ac_high_power',
            battery_runner=battery_probe,battery_clock=battery_clock)
