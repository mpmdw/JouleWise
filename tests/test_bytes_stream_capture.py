"""Production-shaped synthetic chain. No hardware, MLX or measured data."""
from __future__ import annotations
import contextlib
import copy
import dataclasses
import json
import math
import os
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


class Array:
    uint8 = 'uint8'
    __version__ = 'synthetic-no-mlx'
    def __init__(self, clock):
        self.clock = clock
    def ones(self, shape, dtype):
        return shape[0]
    def sum(self, size):
        # Synthetic cache transition; no acceptance choice. C sizes have the
        # same fixed dispatch work, with DRAM 10x slower per payload byte.
        duration = .01 + size/(1e11 if size <= 2**23 else 1e10)
        self.clock.ns += round(duration*1e9)
        return None
    def eval(self, value):
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
            per_byte = 8e-9 if size > 2**23 else 1e-9
            if boundary == 'meter':
                per_byte *= 2
            work = r['repeats']*(.05 + per_byte*size)/r['duration_s']
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


def synthetic_stage(archive, meter_path=None):
    clock = Clock()
    mx = Array(clock)
    calls = []
    def probe(*a, **kw):
        r = bt.stream(*a, **kw)
        calls.append(r)
        return r
    adapter = Capture(clock,calls)
    # Only runtime identity/clock hardware metadata are synthetic seams. The
    # kernel, probe stamps, scan, repeat selection and call order are real.
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
                measured, adapter.start,clock.ns)
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
            root=Path(tmp)/'clone'
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
                    programmed_span_s=10390,span_derivation='ceil(3573.6+22*48+2*1800+900+600+600+60)')
            self.assertEqual(value['hazard_window']['thresholds']['clock']['t_stream_max_s'], cap.CAPTURE_PLANNED_S)
            self.assertEqual(value['hazard_window']['T_stream_max_s'], cap.CAPTURE_PLANNED_S)
            self.assertEqual(value['hazard_window']['member_count'],8)
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
                'rc = cap.main()\n'
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
            self.assertEqual(value['status'],'knee not found')
            self.assertEqual(adapter.starts,1)
            self.assertEqual(adapter.stops,1)
            self.assertIn('allocation_stop',value)
            self.assertEqual(value['call_count'],0)

    def test_unallocatable_stream_size_retains_specific_missing_scan_reason(self):
        with tempfile.TemporaryDirectory(prefix='kb-size-') as tmp:
            clock=Clock()
            mx=Array(clock)
            allocate=mx.ones
            def limited(shape,dtype):
                if shape[0]>2**31:
                    raise RuntimeError('synthetic allocation ceiling')
                return allocate(shape,dtype)
            mx.ones=limited
            with patch.object(bt,'collect_stack',return_value={**copy.deepcopy(bt.REFERENCE_STACK),
                             **copy.deepcopy(bt.REFERENCE_VERSIONS)}):
                result=cap.run_stage(Path(tmp)/'capture',device='synthetic',adapter=Capture(clock,[]),clock=clock,mx=mx)
            self.assertEqual(result['status'],'incomplete')
            self.assertIn('no allocatable scan triplet: S',result['error'])
            self.assertEqual(result['call_count'],0)

    def test_missing_fiducials_stays_reasoned(self):
        with tempfile.TemporaryDirectory(prefix="kb-cap-missing-") as tmp:
            synthetic_chain(self, Path(tmp)/"archive", fiducials=False)

    def test_real_driver_chain_stage_and_harvest(self):
        with tempfile.TemporaryDirectory(prefix='kb-cap-e2e-') as tmp:
            synthetic_chain(self, Path(tmp)/'archive')


def synthetic_chain(test, destination, *, fiducials=True):
    from tests.test_b5_driver import Harness
    from joulewise import night_gate
    from scripts import bytes_stream_harvest as harvest
    harness = Harness(test, g10=False)
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
        'synthetic_stage(sys.argv[sys.argv.index("--archive")+1], Path('+repr(str(harness.custody/'hazards/meter/stream-001.jsonl'))+'))\n')
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
    # Fake hardware lives until supervision stops it. Its allowance is the
    # §1/§2 planned palindrome plus the 22×3×2 s scan, not an arbitrary timeout.
    meter_life = sum(cap.CALL_S[a]+2*cap.IDLE_S+3*cap.SETTLE_S for a in cap.ORDER)+22*3*cap.SCAN_CALL_S
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
    rc=harness.run()
    test.assertEqual(rc,harness.driver.EXIT_GO)
    claim = Path(bindings['claim_runs_root'])
    stage = cap.read(claim/'capture/STAGE.json')
    test.assertEqual(stage['status'],'completed',stage)
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
    reader = bt.read_known_bytes(result['records'],result['scan'])
    cap.write(destination/'READ.json',reader)
    if fiducials:
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
    test.assertEqual(len(result['records']),8)
    test.assertEqual(result['scan']['status'],'knee found')
    test.assertEqual(len(cap.read(destination/'READ.json')['calls']),8)
    test.assertTrue(any(r['harvest']['meter_gaps'] for r in result['records']))
    test.assertTrue(any(row['power_w']>0 for row in result['records'][0]['harvest']['battery_samples']))
    print(json.dumps({'synthetic_archive':str(destination),'stage':stage['status'],
        'records':len(result['records']),'scan':result['scan']['status'],
        'classes':{k:v['class'] for k,v in cap.read(destination/'READ.json')['boundaries'].items()}}))
    return destination


if __name__ == '__main__':
    if '--stage-fixture' in sys.argv:
        synthetic_stage(Path(sys.argv[-1]))
    elif '--synthetic' in sys.argv:
        class Case(unittest.TestCase):
            def runTest(self):
                synthetic_chain(self,Path(sys.argv[-1]))
        case=Case()
        try:
            case.runTest()
        finally:
            case.doCleanups()
    else:
        unittest.main()
