"""Production-shaped synthetic chain. No hardware, MLX or measured data."""
from __future__ import annotations
import contextlib
import copy
import dataclasses
import json
import math
import os
import signal
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise import bytes_stream_capture as cap
from joulewise.b5 import chain
from joulewise.clock import ClockStamp
from joulewise.external import km003c_parse as kp
from scripts import bytes_stream_test as bt


class Clock:
    def __init__(self):
        self.ns = 10**12  # Synthetic RAW origin; not a timing threshold.
    def stamp(self):
        s = self.ns/1e9
        return ClockStamp(1_000_000+s, s, s, 1e-9, 1e-9)
    def sleep(self, value):
        self.ns += round(value*1e9)


class Buffer:
    """Contiguous storage with aliasing row views, never copies of ring bytes."""
    def __init__(self,shape,storage=None,offset=0):
        self.shape = tuple(shape)
        self.storage = object() if storage is None else storage
        self.offset = offset
        self.dtype = 'uint8'
    @property
    def nbytes(self):
        return math.prod(self.shape)  # uint8: exactly one byte per element.
    def __getitem__(self,i):
        assert len(self.shape) == 2 and 0 <= i < self.shape[0]
        return Buffer((self.shape[1],),self.storage,self.offset+i*self.shape[1])


class Array:
    uint8 = 'uint8'
    __version__ = '0.31.2'
    def __init__(self,clock,*,resolves=True):
        self.clock,self.resolves = clock,resolves
        self.last = None
        self.allocations = []
        self.seen = []
    def ones(self,shape,dtype):
        # MLX per-axis signed 32-bit, as observed at source branch 79de7be49.
        if any(n > 2**31-1 for n in shape):
            raise TypeError('ones(): incompatible function arguments')
        self.allocations.append(tuple(shape))
        return Buffer(shape)
    def reshape(self,data,shape):
        assert math.prod(data.shape) == math.prod(shape)
        return Buffer(shape,data.storage,data.offset)
    def sum(self,view):
        assert len(view.shape) == 1
        identity = (view.storage,view.offset)
        hit = self.last == identity
        self.last = identity
        # Synthetic inputs from the archive's ~205 us fixed time and the
        # admitted example's 1 TB/s cache assumption. DRAM's 300 GB/s is its
        # H value 331.6 GB/s rounded to one significant figure; no timing bar.
        rate = 1e12 if hit and self.resolves else 3e11
        self.clock.ns += round((205e-6+view.shape[0]/rate)*1e9)
        return None
    def eval(self,*values):
        pass
    def synchronize(self):
        pass


class Capture:
    """Fake physical stream seam; output is Apple's native NUL-plist shape."""
    def __init__(self, clock, calls):
        self.clock, self.calls = clock, calls
        self.starts = self.stops = 0
    def start_sampling(self, config, context):
        self.starts += 1
        self.start = self.clock.ns
        return SimpleNamespace(ok=True, message=None)
    def device_metadata(self, config):
        return {'telemetry':'powermetrics', 'rail_manifest':['cpu_power','gpu_power','ane_power']}
    def stop_sampling_with_evidence(self, config, context, **kw):
        self.stops += 1
        context.raw_dir.mkdir(parents=True)
        # Extra one-second native tail brackets every receipt. 10 Hz is §2.
        begin, end = self.start-10**9, self.clock.ns+10**9
        cursor = begin
        with (context.raw_dir/'powermetrics.plist').open('wb') as f:
            while cursor < end:
                nxt = cursor+100_000_000
                power = synthetic_power(self.calls, cursor, nxt, boundary='rails')
                gpu = power-2
                doc = {'timestamp': datetime(1970,1,1)+timedelta(seconds=1_000_000+nxt/1e9),
                       'elapsed_ns':100_000_000, 'processor': {
                           'cpu_power':2000., 'gpu_power':gpu*1000, 'ane_power':0.,
                           'cpu_energy':200, 'gpu_energy':round(gpu*100), 'ane_energy':0},
                       'thermal_pressure':'Nominal'}
                f.write(plistlib.dumps(doc)+b'\0')
                cursor = nxt
        return SimpleNamespace(samples=[], uncertainty_evidence={'clock_anchor': {
            'first_sample_end_point_epoch_s': 1_000_000+(begin+100_000_000)/1e9}})


def synthetic_power(calls, lo, hi, *, boundary):
    power = 4. if boundary == 'rails' else 8.
    for r in calls:
        fraction = max(0,min(hi,r['end_ns'])-max(lo,r['start_ns']))/(hi-lo)
        if fraction:
            size = r['bytes_per_read']
            per_byte = 1e-10 if r.get('arm','R').endswith('R') else 2.8e-11
            # Synthetic energy inputs from the admitted example:
            # fixed = 28 W × 205 us; cache = 28 W / 1 TB/s;
            # DRAM = (31.399 W / 331.6 GB/s), rounded to one significant
            # figure = 0.1 J/GB. DC/rails = 53 W / 28 W, rounded likewise
            # to 2. These are fixture powers/energies, not acceptance bars.
            factor = 2 if boundary == 'meter' else 1
            work = factor*r['repeats']*(28*205e-6+per_byte*size)/r['duration_s']
            power += fraction*work
    return power


def write_meter(path, calls, start, end):
    """50 Hz counter, 300 ms polls, a 7 s host/device offset and two lost samples.

    Battery discharge of 3 W occupies the middle half and a 300 ms end-edge
    interval of the first stream (making the edge-charge check nonzero).
    These are explicit synthetic inputs, never acceptance thresholds.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    start -= 10**9
    end += 5*10**9  # Covers τ=2 s+300 ms after the final receipt.
    r = calls[0] if calls else None
    gap = (r['start_ns']+r['end_ns'])//2 if r else start+10**9
    assist = lambda t: bool(r and r['start_ns']+(r['end_ns']-r['start_ns'])//4 <= t <
                             r['end_ns']-(r['end_ns']-r['start_ns'])//4 or
                             r and r['end_ns'] <= t < r['end_ns']+300_000_000)
    header = {'k':'h','status':'streaming','rate_idx':2, 'start_raw_ns':start,
              'start_mono_ns':start-7*10**9}
    with path.open('w') as f:
        f.write(json.dumps(header)+'\n')
        batch = []
        for i,t in enumerate(range(start,end,20_000_000)):
            if gap <= t < gap+40_000_000:
                continue
            watts = synthetic_power(calls,t,t+20_000_000,boundary='meter')
            # Counter wraps naturally; initial device time deliberately offset.
            batch.append(kp.SAMPLE.pack((7000+i*20)%65536,0,20_000_000,round(watts/20*1e6),0,0,0,0))
            if len(batch) == 15:
                rx = t+1_000_000
                row = {'k':'b','tx':rx-2_000_000,'rx':rx,'n':15,'p':b''.join(batch).hex(),
                       'smc':{'B0AC':-250 if assist(rx) else 0, 'B0AV':12000}}
                f.write(json.dumps(row)+'\n')
                batch=[]
        f.write(json.dumps({'k':'t','end_raw_ns':end,'end_mono_ns':end-7*10**9})+'\n')


def synthetic_stage(archive, meter_path=None, *, resolves=True):
    clock = Clock()
    mx = Array(clock,resolves=resolves)
    calls = []
    def probe(*a, **kw):
        r = bt.stream(*a, **kw)
        calls.append(r)
        return r
    adapter = Capture(clock,calls)
    # Only runtime identity/clock hardware metadata are synthetic seams. The
    # kernel, probe stamps, residency check, repeat selection and call order are real.
    metadata = {'clock':'CLOCK_MONOTONIC_RAW','clock_resolution_s':1e-9,
                'clock_tick_num_ns':None,'clock_tick_den':None,'clock_tick_source':'not applicable (non-macOS clock_getres)',
                'clock_ns_conversion':'unknown','clock_ns_conversion_source':'synthetic'}
    with patch.object(bt,'collect_stack',return_value={**copy.deepcopy(bt.REFERENCE_STACK),
                     **copy.deepcopy(bt.REFERENCE_VERSIONS), 'git_commit':'synthetic'}), \
         patch.object(bt,'clock_metadata',return_value=metadata):
        result = cap.run_stage(archive, device='macbook_m3_max', adapter=adapter,clock=clock,mx=mx,probe=probe)
    if result.get('capture_stop_error'):
        raise AssertionError(result)
    measured = [r for r in calls if r['idle_s']]
    write_meter(meter_path or Path(archive).parents[1]/'custody/hazards/meter/stream-001.jsonl',
                measured, getattr(adapter,'start',clock.ns),clock.ns)
    return result


class CaptureTests(unittest.TestCase):
    def test_fixed_graph_and_generator(self):
        tree = cap.read(cap.ROOT/cap.KIT/'plan_tree.json')
        self.assertEqual([s.kind for s in chain.stage_plan(tree)],
                         ['bracket_reservation','calibration_capture','bytes_stream_capture','calibration_capture'])
        bad = copy.deepcopy(tree)
        bad['non_claim'] = False
        with self.assertRaises(chain.ChainRenderError):
            chain.stage_plan(bad)
        subprocess.run([sys.executable,'-B',str(cap.ROOT/cap.KIT/'generate.py'),'--check'], check=True)

    def test_synthetic_switch_blocks_hardware(self):
        with self.assertRaisesRegex(ValueError,'injected'):
            cap.run_stage('/unused', device='macbook_m3_max')

    def test_prepare_authors_isolated_night_plan_without_default_ledger(self):
        from tests.git_fixture import init_git_fixture
        with tempfile.TemporaryDirectory(prefix='kb-prepare-') as tmp:
            root=(Path(tmp)/'clone').resolve()
            root.mkdir()
            kit=root/cap.KIT
            shutil.copytree(cap.ROOT/cap.KIT,kit)
            for relative in (chain.RUNBOOK_RELATIVE,'configs/b6/registration/acceptance.json'):
                target=root/relative
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(cap.ROOT/relative,target)
            init_git_fixture(root)
            subprocess.run(['git','add','.'],cwd=root,check=True,capture_output=True)
            subprocess.run(['git','-c','user.name=t','-c','user.email=t@t','-c','commit.gpgsign=false','commit','-m','synthetic inputs'],cwd=root,check=True,capture_output=True)
            with patch.object(cap,'ROOT',root), contextlib.redirect_stdout(__import__('io').StringIO()):
                # Span and disk bytes are synthetic plan inputs, with their
                # explicit derivation/source strings, not acceptance limits.
                value=cap.prepare(root,Path(tmp)/'session',t0=__import__('time').time()+420,
                    adapter_max_w=140,adapter_source='synthetic 140 W adapter',disk_bytes=10**9,
                    disk_derivation='synthetic frame envelope × planned records',
                    programmed_span_s=9734,span_derivation='ceil(3573.6+270+10+2*1800+900+600+600+4*30+60)')
            self.assertEqual(value['hazard_window']['thresholds']['clock']['t_stream_max_s'], cap.CAPTURE_PLANNED_S)
            self.assertEqual(value['hazard_window']['T_stream_max_s'], cap.CAPTURE_PLANNED_S)
            self.assertEqual(value['hazard_window']['member_count'],len(bt.ORDER))
            self.assertIn('runs_bytes_stream_test/calibration_ledger.jsonl',
                          value['hazard_window']['bindings']['ledger_path'])
            self.assertFalse((root/'runs/calibration_observation_ledger.jsonl').exists())
            self.assertEqual(len(chain.stage_plan(cap.read(kit/'plan_tree.json'))),4)

    def test_path_cli_bootstrap_without_editable_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = Path(tmp)/'never-created'
            result = subprocess.run([sys.executable, '-I', '-B', str(cap.ROOT/'joulewise/bytes_stream_capture.py'),
                'prepare', '--checkout', str(cap.ROOT), '--session', str(session), '--t0', '0',
                '--adapter-max-w', '140', '--adapter-source', 'synthetic nameplate',
                '--disk-bytes', '1', '--disk-derivation', 'synthetic',
                '--programmed-span-s', '1', '--span-derivation', 'synthetic'],
                capture_output=True, text=True, cwd='/tmp')
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertNotIn('ModuleNotFoundError', result.stderr)
            self.assertTrue('checkout must be clean' in result.stderr or
                            'installer minimum lead' in result.stderr, result.stderr)
            self.assertFalse(session.exists())

    def test_start_exception_never_stops_unstarted_capture(self):
        # Real stage CLI; only physical adapter/array/clock seams are injected.
        with tempfile.TemporaryDirectory() as tmp:
            script = (f'import sys; sys.path.insert(0, {str(cap.ROOT)!r})\n'
                'from tests.test_bytes_stream_capture import Clock, Capture, Array\n'
                'from joulewise import bytes_stream_capture as cap\n'
                'clock = Clock(); adapter = Capture(clock, [])\n'
                'def fail(*args): raise RuntimeError("start failed")\n'
                'adapter.start_sampling = fail\n'
                'run = cap.run_stage\n'
                'cap.run_stage = lambda archive, device: run(archive, device=device, '
                'clock=clock, adapter=adapter, mx=Array(clock))\n'
                'from unittest.mock import patch\n'
                'from scripts import bytes_stream_test as bt\n'
                'with patch.object(bt, "collect_stack", return_value={**bt.REFERENCE_STACK, **bt.REFERENCE_VERSIONS}):\n'
                '    rc = cap.main()\n'
                'assert adapter.stops == 0, adapter.stops\n'
                'raise SystemExit(rc)\n')
            result = subprocess.run([sys.executable, '-I', '-B', '-c', script,
                'stage', '--archive', str(Path(tmp)/'capture'), '--device', 'synthetic'],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertNotIn('Traceback', result.stderr)
            stage = cap.read(Path(tmp)/'capture/STAGE.json')
            self.assertIn('start failed', stage['error'])
            self.assertNotIn('capture_stop_error', stage)

    def test_allocation_stop_and_capture_teardown_are_reasoned(self):
        with tempfile.TemporaryDirectory(prefix='kb-alloc-') as tmp:
            clock=Clock()
            mx=Array(clock)
            mx.ones=lambda *a,**kw: (_ for _ in ()).throw(RuntimeError('synthetic allocation failure'))
            adapter=Capture(clock,[])
            value=cap.run_stage(Path(tmp)/'capture',device='synthetic',adapter=adapter,clock=clock,mx=mx)
            self.assertEqual(value['status'],'residency not resolved')
            self.assertEqual(adapter.starts,0)
            self.assertEqual(adapter.stops,0)
            self.assertIn('allocation_stop',value)
            self.assertEqual(value['call_count'],0)

    def test_unresolved_check_stops_before_energy_capture(self):
        with tempfile.TemporaryDirectory(prefix='kb-refuse-') as tmp:
            result = synthetic_stage(Path(tmp)/'capture',Path(tmp)/'meter.jsonl',resolves=False)
            self.assertEqual(result['status'],'residency not resolved')
            self.assertEqual(result['reason'],'residency not resolved')
            self.assertEqual(result['call_count'],0)
            self.assertFalse((Path(tmp)/'capture/capture_stop.json').exists())
            self.assertEqual(len(cap.read(Path(tmp)/'capture/CHECK.json')['rungs']),len(bt.LADDER))

    def test_ring_axes_and_aliasing_match_mlx(self):
        mx = Array(Clock())
        with self.assertRaises(TypeError):
            mx.ones((2**31,),dtype=mx.uint8)
        ring = bt.allocate_ring(mx)
        for b in (bt.LADDER[0],bt.LADDER[-1]):
            rows = bt.ring_views(mx,ring,b)
            self.assertIs(rows[0].storage,ring.storage)
            self.assertIs(rows[-1].storage,ring.storage)
            self.assertEqual(rows[-1].offset,bt.RING_BYTES-b)
        self.assertEqual(mx.allocations,[(bt.RING_BYTES//bt.GEOMETRY_BYTES,bt.GEOMETRY_BYTES)])

    def test_exception_preserves_check_prefix_and_never_starts_capture(self):
        for exception in (RuntimeError('synthetic dispatch failed'),MemoryError('synthetic view allocation failed')):
            with self.subTest(exception=type(exception).__name__), tempfile.TemporaryDirectory() as tmp:
                clock=Clock();adapter=Capture(clock,[]);count=0
                def probe(*a,**kw):
                    nonlocal count
                    count+=1
                    if count == 2:  # Fail after exactly the first durable pilot.
                        raise exception
                    return bt.stream(*a,**kw)
                with patch.object(bt,'collect_stack',return_value={**bt.REFERENCE_STACK,**bt.REFERENCE_VERSIONS}):
                    result=cap.run_stage(Path(tmp)/'capture',device='synthetic',adapter=adapter,
                        clock=clock,mx=Array(clock),probe=probe)
                self.assertEqual(adapter.starts,0)
                self.assertEqual(result['call_count'],0)
                self.assertEqual(len(cap.read(Path(tmp)/'capture/CHECK_RECEIPTS.json')),1)
                self.assertEqual(len(cap.read(Path(tmp)/'capture/CHECK.json')['receipts']),1)
                if isinstance(exception,MemoryError):
                    self.assertEqual(result['reason'],f'allocation failed ({bt.RING_BYTES} B ring)')
                else:
                    self.assertIn('synthetic dispatch failed',result['error'])

    def test_hour_allocation_failure_prints_registered_reason(self):
        from scripts.bytes_stream_harvest import harvest
        with tempfile.TemporaryDirectory() as tmp:
            clock=Clock();mx=Array(clock);allocate=mx.ones;adapter=Capture(clock,[])
            def ones(shape,dtype):
                if mx.allocations:  # Check allocation succeeds; first hour allocation fails.
                    raise RuntimeError('synthetic hour allocation failed')
                return allocate(shape,dtype)
            mx.ones=ones
            archive=Path(tmp)/'runs_bytes_stream_test/capture'
            with patch.object(bt,'collect_stack',return_value={**bt.REFERENCE_STACK,**bt.REFERENCE_VERSIONS}):
                result=cap.run_stage(archive,device='synthetic',adapter=adapter,clock=clock,mx=mx)
            self.assertEqual(result['call_count'],0)
            self.assertEqual((adapter.starts,adapter.stops),(1,1))
            inputs=harvest(Path(tmp))
            self.assertEqual(inputs['check']['completed_check']['status'],'residency resolved')
            reader=bt.read_known_bytes(inputs['records'],inputs['check'])
            for boundary in reader['boundaries'].values():
                self.assertEqual(boundary['class'],'UNDETERMINED')
                self.assertEqual(boundary['reason'],f'allocation failed ({bt.RING_BYTES} B ring)')

    def test_bad_geometry_or_clock_stops_before_capture(self):
        for field,value,reason in (('dtype','float32','geometry check failed (dtype)'),
                                   ('clock_resolution_s',None,'clock prerequisite missing')):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                clock = Clock(); adapter = Capture(clock,[])
                def probe(*a,**kw):
                    r = bt.stream(*a,**kw); r[field] = value; return r
                with patch.object(bt,'collect_stack',return_value={**bt.REFERENCE_STACK,**bt.REFERENCE_VERSIONS}):
                    result = cap.run_stage(Path(tmp)/'capture',device='synthetic',adapter=adapter,
                        clock=clock,mx=Array(clock),probe=probe)
                self.assertIn(reason,result['reason'])
                self.assertEqual(result['call_count'],0)
                self.assertEqual(adapter.starts,0)
                self.assertEqual(adapter.stops,0)
                self.assertEqual(len(cap.read(Path(tmp)/'capture/CHECK_RECEIPTS.json')),1)

    def test_incorrect_graph_count_is_refused(self):
        tree = cap.read(cap.ROOT/cap.KIT/'plan_tree.json')
        own = next(s for s in tree['stage_graph'] if s['kind'] == 'bytes_stream_capture')
        self.assertEqual(own['expected_count'],len(bt.ORDER))
        own['expected_count'] = 2*len(bt.ORDER)  # The retired eight-call graph.
        with self.assertRaisesRegex(chain.ChainRenderError,'four calls'):
            chain.stage_plan(tree)

    def test_missing_fiducials_stays_reasoned(self):
        with tempfile.TemporaryDirectory(prefix="kb-cap-missing-") as tmp:
            synthetic_chain(self, Path(tmp)/"archive", fiducials=False)

    def test_real_driver_chain_unresolved(self):
        with tempfile.TemporaryDirectory(prefix='kb-cap-no-residency-') as tmp:
            synthetic_chain(self,Path(tmp)/'archive',resolves=False)

    def test_real_driver_chain_stage_and_harvest(self):
        with tempfile.TemporaryDirectory(prefix='kb-cap-e2e-') as tmp:
            synthetic_chain(self, Path(tmp)/'archive')


def synthetic_chain(test, destination, *, fiducials=True, resolves=True):
    from tests.test_b5_driver import Harness
    from joulewise import night_gate
    from scripts import bytes_stream_harvest as harvest
    harness = Harness(test, g10=False)
    # Own every direct child and journaled group without depending on ps/pgrep,
    # which this sandbox cannot read. The real driver still keeps its census.
    owned = []
    real_init = subprocess.Popen.__init__
    def tracked_init(process, *args, **kwargs):
        real_init(process, *args, **kwargs)
        owned.append((process, kwargs.get('start_new_session',False)))
    def reap_owned():
        from tests.process_reaper import journal_pgids, kill_and_wait
        groups = journal_pgids(harness.night) | {p.pid for p,group in owned if group}
        for pgid in groups - {os.getpgid(0)}:
            try:
                os.killpg(pgid,signal.SIGKILL)
            except ProcessLookupError:
                pass
        for process,_ in owned:
            kill_and_wait(process)
        test.assertTrue(all(p.poll() is not None for p,_ in owned))
    test.addCleanup(reap_owned)
    measurement = Path(harness.plan.measurement_root)
    kit = measurement/cap.KIT
    kit.mkdir()
    for p in (cap.ROOT/cap.KIT).iterdir():
        if p.is_file():
            shutil.copyfile(p,kit/p.name)
    tree = cap.read(kit/'plan_tree.json')
    window = harness.plan.hazard_window
    bindings = window['bindings']
    # Match prepare's production attempt names, rather than Harness's B5 names.
    bindings.update(pre_attempt_id='pre', post_attempt_id='post',
        pre_calibration_dir=str(Path(bindings['claim_runs_root'])/'instrument_validation/pre'),
        post_calibration_dir=str(Path(bindings['claim_runs_root'])/'instrument_validation/post'))
    # Keep only real hardware seams faked: existing reservation/calibration
    # fixture tools and new stage's fake array/capture adapter. Dispatch and
    # the rendered four-stage chain are the production implementations.
    package = measurement/'joulewise'
    package.mkdir(exist_ok=True)
    stage_script = package/'bytes_stream_capture.py'
    stage_script.write_text('import sys\nsys.path.insert(0,'+repr(str(cap.ROOT))+')\n'
        'from tests.test_bytes_stream_capture import synthetic_stage\n'
        'from pathlib import Path\n'
        'synthetic_stage(sys.argv[sys.argv.index("--archive")+1], Path('+repr(str(harness.custody/'hazards/meter/stream-001.jsonl'))+'), resolves='+repr(resolves)+')\n')
    raw = chain.render_chain(tree=tree, tree_sha256=cap.sha(kit/'plan_tree.json'),
            stages=chain.stage_plan(tree),bindings=bindings,measurement_root=measurement,pack_root=kit,
            plan_id=harness.plan.plan_id,runbook_text=(cap.ROOT/chain.RUNBOOK_RELATIVE).read_text(),settle_s=0)
    harness.replace_chain(raw.decode(),keep_yield_plan=True)
    plan = cap.read(harness.plan_path)
    plan['hazard_window']['bindings'] = bindings
    plan['hazard_window']['pack'].update(pack_root=str(kit),pack_id=kit.name,
        plan_tree_sha256=cap.sha(kit/'plan_tree.json'))
    plan['hazard_window']['stages']=[s.summary() for s in chain.stage_plan(tree)]
    cap.write(harness.root/'updated-plan.json',plan)
    harness.plan_path=harness.root/'updated-plan.json'
    harness.plan=night_gate.NightPlan.from_mapping(plan)
    # The meter/monitor are real child processes, killed by the driver's
    # supervision/reaper. Their planning allowance is the rule's full stage.
    meter_life = cap.CAPTURE_PLANNED_S
    harness.meter_argv = lambda request: [sys.executable, '-c',
        'import sys,time; time.sleep(float(sys.argv[1]))', str(meter_life), str(request.custody_root)]
    if fiducials:
        from tests.test_reduce import self_consistent_calibration
        from joulewise.powermetrics_fiducial import PROTOCOL_ID
        evidence, raw_plist, events = self_consistent_calibration(protocol_id=PROTOCOL_ID)
        fixture = harness.root/'fiducial-source'
        (fixture/'raw').mkdir(parents=True)
        cap.write(fixture/'instrument_evidence.json', evidence)
        (fixture/'raw/powermetrics.plist').write_bytes(raw_plist)
        (fixture/'events.jsonl').write_bytes(events)
        # Replace only the physical calibration seam. The rendered pre/post
        # tools write the production artifact trio at their real output paths.
        tool = measurement/'scripts/validate_powermetrics_fiducial.py'
        tool.write_text(tool.read_text() + '\nimport shutil\n' +
            'shutil.copytree('+repr(str(fixture))+', directory, dirs_exist_ok=True)\n')
    with patch.object(subprocess.Popen,'__init__',tracked_init):
        try:
            rc=harness.run()
        finally:
            reap_owned()
    night_result = harness.result()
    if rc != harness.driver.EXIT_GO:
        # Admit only the sandbox's documented unreadable-census failure after
        # a successful chain. Never turn that driver refusal into a GO record.
        census = cap.read(harness.night/'chain.exit-census.json')
        test.assertEqual(night_result['chain_exit_code'],0,night_result)
        test.assertEqual(night_result['aborted_reason'],'night_chain_alive',night_result)
        test.assertFalse(census['proven'],census)
        test.assertIn('census_',json.dumps(census),census)
        print(json.dumps({'environment':'sandbox process-group census unavailable',
            'driver_exit':rc,'driver_verdict':night_result['verdict'],'chain_exit':0}))
    claim = Path(bindings['claim_runs_root'])
    stage = cap.read(claim/'capture/STAGE.json')
    test.assertEqual(stage['status'],'completed' if resolves else 'residency not resolved',stage)
    destination.mkdir(parents=True)
    shutil.copytree(claim,destination/'runs_bytes_stream_test')
    shutil.copytree(harness.custody,destination/'custody')
    # Meter's fake stream seam wrote at the run-parent (same lifecycle as the
    # driver-owned stream). Preserve it at the production archive location.
    meter = harness.custody/'hazards/meter'
    target=destination/'custody/hazards/meter'
    target.mkdir(parents=True,exist_ok=True)
    for p in meter.glob('stream-*.jsonl'):
        shutil.copyfile(p,target/p.name)
    cap.write(destination/'SESSION.json',dict(non_claim=True,adapter_max_w=140,
        adapter_source='synthetic 140 W nameplate; no hardware',
        calibration_registration=cap.read(cap.ROOT/'configs/b6/registration/acceptance.json')))
    result=harvest.harvest(destination)
    cap.write(destination/'INPUT.json',result)
    reader = bt.read_known_bytes(result['records'],result['check'])
    cap.write(destination/'READ.json',reader)
    if not resolves:
        test.assertEqual(stage['call_count'],0)
        test.assertEqual(len(result['records']),0)
        test.assertEqual(result['check']['reason'],'residency not resolved')
        for boundary in reader['boundaries'].values():
            test.assertEqual(boundary['class'],'UNDETERMINED')
            test.assertEqual(boundary['reason'],'residency not resolved')
    elif fiducials:
        test.assertIsNotNone(result['provenance']['calibration']['operative_bound_s'])
        for record in result['records']:
            test.assertIsNotNone(record['harvest']['anchor_shift_j'])
            test.assertIsNotNone(record['harvest']['operative_timing_bound_s'])
        for boundary in reader['boundaries'].values():
            test.assertIn(boundary['class'], ('RESOLVED', 'NOT RESOLVED'))
        from tests.test_bytes_stream_harvest import independent_arithmetic
        independent_arithmetic(test, destination, result['records'][0])
    else:
        for name in ('rails', 'gpu', 'rest'):
            test.assertEqual(reader['boundaries'][name]['class'], 'UNDETERMINED')
            test.assertIn('anchor_shift_j', reader['boundaries'][name]['reason'])
        test.assertIsNone(result['provenance']['calibration']['operative_bound_s'])
    print(json.dumps({k: reader['printed'][k] for k in ('contrasts','claim_lines','share')}, sort_keys=True))
    test.assertEqual(len(result['records']),len(bt.ORDER) if resolves else 0)
    test.assertEqual(result['check']['status'],'residency resolved' if resolves else 'residency not resolved')
    test.assertEqual(len(cap.read(destination/'READ.json')['calls']),len(bt.ORDER) if resolves else 0)
    if resolves:
        test.assertTrue(any(r['harvest']['meter_gaps'] for r in result['records']))
        test.assertTrue(any(row['power_w']>0 for row in result['records'][0]['harvest']['battery_samples']))
    print(json.dumps({'synthetic_archive':str(destination),'stage':stage['status'],
        'records':len(result['records']),'check':result['check']['status'],
        'classes':{k:v['class'] for k,v in cap.read(destination/'READ.json')['boundaries'].items()}}))
    return destination


if __name__ == '__main__':
    if '--stage-fixture' in sys.argv:
        synthetic_stage(Path(sys.argv[-1]))
    elif '--synthetic' in sys.argv:
        class Case(unittest.TestCase):
            def runTest(self):
                synthetic_chain(self,Path(sys.argv[-1]),resolves='--unresolved' not in sys.argv)
        case=Case()
        try:
            case.runTest()
        finally:
            case.doCleanups()
    else:
        unittest.main()
