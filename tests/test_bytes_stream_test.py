"""Matched v3 probe/check/reader: synthetic fixtures, never hardware evidence."""
from copy import deepcopy
from fractions import Fraction
import io
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import bytes_stream_test as probe
from joulewise.flags.collect import RUNTIME_PACKAGES
from tests.test_bytes_stream_capture import Array, Buffer, Clock


def synthetic_clock():
    # Recorded Mac: r=max(42,125/3) ns; two endpoints × (r+1 ns)=86 ns.
    return {"clock":"CLOCK_MONOTONIC_RAW","clock_resolution_s":4.2e-8,
            "clock_tick_num_ns":125,"clock_tick_den":3,"clock_tick_source":"synthetic recorded Mac 125/3 ns",
            "clock_ns_conversion":"unknown","clock_ns_conversion_source":"synthetic"}


def identity():
    return {**deepcopy(probe.REFERENCE_STACK),**deepcopy(probe.REFERENCE_VERSIONS),"git_commit":"synthetic"}


def timing_receipt(b,n,t,arm,*,start=0,rung_index=None,phase=None):
    """Integer RAW stamps over a synthetic span; metadata follows v3 exactly."""
    end = start+round(t*n*1e9)
    q = probe.RING_BYTES//b
    return {"schema_version":probe.SCHEMA,**synthetic_clock(),"start_ns":start,"end_ns":end,
            "idle_pre_start_ns":start,"idle_pre_end_ns":start,"idle_post_start_ns":end,"idle_post_end_ns":end,
            "bytes_per_read":b,"repeats":n,"bytes_read":b*n,"logical_bytes":b*n,"duration_s":(end-start)/1e9,
            "settle_s":0,"idle_s":0,"arm":arm,"ring_bytes":probe.RING_BYTES,"ring_shape":[q,b],
            "dtype":"uint8","view_nbytes":b,"view_order":"rotate" if arm.endswith("R") else "repeat",
            "sweeps":n//q,"geometry_branch_bytes":probe.GEOMETRY_BYTES,"geometry_source":probe.GEOMETRY_SOURCE,
            "launch_side":"small","stack":identity(),"rung_index":rung_index,"check_phase":phase}


# Revision §5's archived per-dispatch spans. Transposition to production
# whole-sweep counts is a synthetic fixture, not new diagnostic evidence.
EXAMPLE_TIMES = {
    2**26:{"C":[.0006139860881990132,.0007013643176398026,.0008012981428865132],
           "R":[.000664278361328125,.000661487466796875,.0006659087724609375]},
    2**25:{"C":[.000254390858203125,.0002570832140625,.00025723296979166666],
           "R":[.00030861413854166666,.00030873202057291667,.00030859111328125004]}}


def check_receipts(*,resolves=True):
    result=[]; start=0
    for k,b in enumerate(probe.LADDER):
        for arm in ("C","R"):
            times = EXAMPLE_TIMES[b][arm] if resolves else [205e-6+b/3e11]*3
            mean = statistics.mean(times)
            q = probe.RING_BYTES//b
            pilot = timing_receipt(b,q,mean,"check-"+arm,start=start,rung_index=k,phase="pilot")
            result.append(pilot);start=pilot["end_ns"]
            n = probe.planned_repeats(b,pilot["duration_s"]/q,probe.CHECK_CALL_S,at_least_one=True)
            for value in times:
                receipt=timing_receipt(b,n,value,"check-"+arm,start=start,rung_index=k,phase="timing")
                result.append(receipt);start=receipt["end_ns"]
        if resolves and b == 2**25:
            break
    return result


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.reference,self.versions=probe.registered_stack()
        self.stack=identity()
        self.capture={"telemetry_backend":"powermetrics","measurement_boundary_label":deepcopy(self.reference["measurement_boundary_label"])}

    def run_stream(self,arm="R",**kw):
        clock=Clock(); mx=Array(clock)
        with patch.object(probe,"collect_stack",return_value=self.stack), patch.object(probe,"clock_metadata",return_value=synthetic_clock()):
            receipt=probe.stream(probe.GEOMETRY_BYTES,probe.RING_BYTES//probe.GEOMETRY_BYTES,
                device="macbook_m3_max",arm=arm,mx=mx,clock_ns=lambda:clock.ns,sleep=clock.sleep,**kw)
        return receipt,mx

    def test_v3_counts_geometry_and_order(self):
        r,mx=self.run_stream()
        self.assertEqual(r["schema_version"],probe.SCHEMA)
        self.assertEqual(r["bytes_read"],probe.RING_BYTES)  # One sweep, excludes warm-up.
        self.assertEqual(r["sweeps"],1)
        self.assertEqual(mx.allocations,[(probe.RING_BYTES//probe.GEOMETRY_BYTES,probe.GEOMETRY_BYTES)])
        self.assertIsNone(probe.geometry_error(r))
        self.assertEqual(r["stack_check"]["status"],"pending_capture")
        self.assertEqual(r,json.loads(json.dumps(r,allow_nan=False)))
        keys=("idle_pre_start_ns","idle_pre_end_ns","start_ns","end_ns","idle_post_start_ns","idle_post_end_ns")
        self.assertEqual(sorted(r[k] for k in keys),[r[k] for k in keys])
        for a,b,seconds in ((keys[0],keys[1],57.6),(keys[1],keys[2],3),(keys[3],keys[4],3),(keys[4],keys[5],57.6)):
            self.assertEqual(r[b]-r[a],round(seconds*1e9))  # Exact synthetic sleep stamps.

    def test_matched_modes_differ_only_in_address_reuse(self):
        rotate,_=self.run_stream("R",idle_s=0,settle_s=0)
        repeat,_=self.run_stream("C",idle_s=0,settle_s=0)
        for field in ("bytes_per_read","ring_shape","dtype","view_nbytes","repeats","logical_bytes","geometry_source","launch_side"):
            self.assertEqual(rotate[field],repeat[field])
        self.assertGreater(rotate["duration_s"],repeat["duration_s"])

    def test_signed_axis_reasoning_retained_and_bad_counts_refused(self):
        self.assertEqual(probe.payload_shape(2**31-1),(2**31-1,))
        self.assertEqual(probe.payload_shape(2**35),(32,2**30))
        with self.assertRaises(ValueError): probe.payload_shape(2**31+1)
        for b,n in ((0,1),(True,1),(2**27,512),(2**26,1),(2**26,0),(3,512)):
            with self.subTest(b=b,n=n), self.assertRaises(ValueError):
                probe.stream(b,n,device="synthetic",mx=Array(Clock()))

    def test_all_geometry_leaves_are_required(self):
        receipt,_=self.run_stream()
        fields=("schema_version","ring_bytes","ring_shape","dtype","view_nbytes","view_order","arm",
                "sweeps","logical_bytes","bytes_read","bytes_per_read","repeats","geometry_branch_bytes",
                "geometry_source","launch_side")
        for field in fields:
            row=deepcopy(receipt);del row[field]
            with self.subTest(field=field): self.assertIn(field,probe.geometry_error(row))
        for field in ("runtime_version.version","packages.mlx","packages.mlx-metal"):
            row=deepcopy(receipt);parent,key=field.split(".");row["stack"][parent][key]="other"
            self.assertIn(field,probe.geometry_error(row))

    def test_invalid_stamps(self):
        clock=Clock();mx=Array(clock)
        with patch.object(probe,"collect_stack",return_value=identity()), self.assertRaises(ValueError):
            probe.stream(2**26,512,device="synthetic",mx=mx,clock_ns=lambda:-1,sleep=clock.sleep)

    def test_collect_stack_uses_pass1_sources_and_explicit_device(self):
        with patch.object(probe, "runtime_versions", return_value=self.versions) as versions, \
             patch.object(probe.platform, "platform", return_value="observed-os"), \
             patch.object(probe.platform, "machine", return_value="observed-machine"), \
             patch.object(probe.subprocess, "check_output", return_value="observed-head\n") as git:
            stack = probe.collect_stack(Array(Clock()), "config-device")
        versions.assert_called_once_with(sys.executable)
        self.assertEqual(stack["os_version"], "observed-os")
        self.assertEqual(stack["hardware_unit"], {"machine": "observed-machine", "device": "config-device"})
        self.assertEqual(stack["runtime_version"], {"name": "mlx", "version": "0.31.2"})
        self.assertEqual(stack["kernel_library"], "unavailable")
        self.assertEqual(stack["git_commit"], "observed-head")
        self.assertEqual(git.call_args.args[0][-2:], ["rev-parse", "HEAD"])
        self.assertEqual(stack["packages"], self.versions["packages"])
        for field in probe.NOT_APPLICABLE:
            self.assertEqual(stack[field], "not_applicable")

    def test_kernel_library_uses_prepare_fallback(self):
        with patch.object(probe, "runtime_versions", return_value=self.versions), \
             patch.object(probe.platform, "platform", return_value="synthetic-os"), \
             patch.object(probe.subprocess, "check_output", return_value="head"):
            for prepare, expected in ((None, "unavailable"), ({}, "unavailable"),
                                      ({"kernel_library": "observed-kernel"}, "observed-kernel")):
                self.assertEqual(probe.collect_stack(Array(Clock()), "device", prepare=prepare)["kernel_library"], expected)

    def test_match_compares_projections_not_model_adapter_config_or_git(self):
        self.stack["hardware_unit"]["config_id"] = "not compared"
        self.stack["runtime_version"]["adapter"] = "not compared"
        check = probe.compare_stack(self.stack, self.reference, self.versions, capture_stack=self.capture)
        self.assertEqual(check["status"], "match")
        self.assertEqual(check["differences"], [])
        self.assertEqual(len(check["comparison"]), len(probe.LOCAL_FIELDS)+len(probe.CAPTURE_FIELDS)+8)

    def test_every_compared_local_field_and_each_package_detects_change(self):
        fields = probe.LOCAL_FIELDS + ("python",) + tuple("packages." + k for k in RUNTIME_PACKAGES)
        for field in fields:
            stack = deepcopy(self.stack)
            value = stack
            parts = field.split(".")
            for part in parts[:-1]:
                value = value[part]
            value[parts[-1]] = "different"
            with self.subTest(field=field):
                check = probe.compare_stack(stack, self.reference, self.versions, capture_stack=self.capture)
                self.assertEqual(check["differences"], [field])
                self.assertEqual(check["physical_differences"], [field] if field in probe.PHYSICAL_FIELDS else [])
                self.assertEqual(check["disclosure_differences"], [] if field in probe.PHYSICAL_FIELDS else [field])

    def test_missing_and_extra_package_keys_are_not_ignored(self):
        for name, value in (("mlx", None), ("extra", "1")):
            stack = deepcopy(self.stack)
            if value is None:
                del stack["packages"][name]
            else:
                stack["packages"][name] = value
            check = probe.compare_stack(stack, self.reference, self.versions)
            self.assertEqual(check["differences"], ["packages." + name])
        del self.stack["os_version"]
        self.assertIn("os_version", probe.compare_stack(self.stack, self.reference, self.versions)["differences"])

    def test_capture_is_pending_until_harvest_and_mismatches_are_named(self):
        # Receipt-supplied capture values cannot claim to be observed by harvest.
        self.stack.update(self.capture)
        check = probe.compare_stack(self.stack, self.reference, self.versions)
        self.assertEqual(check["status"], "pending_capture")
        self.assertEqual(check["pending_fields"], list(probe.CAPTURE_FIELDS))
        for field in probe.CAPTURE_FIELDS:
            capture = deepcopy(self.capture)
            if field == "telemetry_backend":
                capture[field] = "different"
            else:
                capture["measurement_boundary_label"]["rails"] = ["gpu_power"]
            with self.subTest(field=field):
                self.assertEqual(probe.compare_stack(self.stack, self.reference, self.versions,
                                                    capture_stack=capture)["differences"], [field])

    def test_registered_unit_projections_and_all_seven_package_keys(self):
        self.assertEqual(set(self.versions["packages"]), set(RUNTIME_PACKAGES))
        self.assertEqual(self.reference["runtime_version"]["version"], "0.31.2")
        # A changing model identity does not affect registered_stack's projection.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for parent in ("configs/b6/registration", "configs/bytes"):
                (root / parent).mkdir(parents=True)
            bp = root / "configs/b6/registration/identity_pins.json"
            cp = root / "configs/bytes/identity_pins.json"
            cp.write_text(json.dumps({"runtime_versions": self.versions}))
            other = deepcopy(self.reference)
            other["model_artifact_sha256"] = "other model"
            pins = {"units": {"one": {"stack_identity": self.reference}, "two": {"stack_identity": other}}}
            bp.write_text(json.dumps(pins))
            probe.registered_stack(root)
            other["os_version"] = "changed"
            bp.write_text(json.dumps(pins))
            self.assertEqual(probe.registered_stack(root), (self.reference, self.versions))
            check = probe.checkout_reference_check(root)
            self.assertEqual(check["units"]["two"]["differences"], ["os_version"])
            bp.write_text("invalid json")
            self.assertTrue(probe.checkout_reference_check(root)["errors"])
        self.assertTrue(probe.checkout_reference_check("/nonexistent/kb-reference")["errors"])



    def test_help_needs_no_metal(self):
        out=subprocess.run([sys.executable,"-I","-B",str(probe.ROOT/"scripts/bytes_stream_test.py"),"--help"],capture_output=True,text=True)
        self.assertEqual(out.returncode,0,out.stderr)
        self.assertIn("--arm",out.stdout)


class ResidencyTests(unittest.TestCase):
    def test_first_resolved_rung_and_conservative_correction(self):
        result=probe.residency_check(check_receipts())
        self.assertEqual(result["status"],"residency resolved")
        self.assertEqual((result["b"],result["W"],result["Q"]),(2**25,2**35,1024))
        self.assertEqual([r["resolved"] for r in result["rungs"]],[False,True])
        # κ prints four significant figures: half a last-place unit.
        self.assertAlmostEqual(result["kappa"],6.213,delta=.0005)
        row=result["rungs"][-1]
        expected=1/((1-Fraction(1,64))*Fraction(row["D_s"]-row["dD_s"])/Fraction(row["R"]["t_s"]+row["R"]["dt_s"]))
        # κ: 1e6×float noise (≈1e-8 after ≈21× amplification) < 1e-6 < 4-s.f. half-unit (≥5e-5 relative).
        self.assertAlmostEqual(result["kappa"],float(expected),delta=1e-6*abs(float(expected)))

    def test_unresolved_ladder_and_no_retries(self):
        receipts=check_receipts(resolves=False)
        result=probe.residency_check(receipts)
        self.assertEqual(result["reason"],"residency not resolved")
        self.assertEqual(len(result["rungs"]),len(probe.LADDER))
        self.assertEqual(len(result["receipts"]),len(probe.LADDER)*2*4)  # C/R × pilot+three.
        self.assertIsNone(result["b"])
        for rows in (check_receipts()[:-1],check_receipts()+check_receipts()[-1:]):
            self.assertIn("check-status fault",probe.residency_check(rows)["reason"])

    def test_clock_prerequisite_never_uses_one_ns_fallback(self):
        for field in ("clock","clock_resolution_s","clock_tick_source","clock_tick_num_ns","clock_tick_den"):
            rows=check_receipts();rows[0].pop(field)
            result=probe.residency_check(rows)
            self.assertIn("clock prerequisite missing",result["reason"])
            self.assertIn(field,result["reason"])
            self.assertEqual(len(result["receipts"]),len(rows))
        receipt=check_receipts()[1]
        actual=probe.clock_duration_bound_ns(receipt)/receipt["repeats"]
        # q: 1e6×4ε q < 1e-6 q; converting ns to s puts that bar below .01×smallest δt (0.086 µs).
        self.assertAlmostEqual(actual,86/receipt["repeats"],delta=1e-6*86/receipt["repeats"])

    def test_geometry_check_includes_pilots_and_later_receipts(self):
        for index in (0,1,7,15):
            rows=check_receipts();rows[index]["view_nbytes"]+=1
            self.assertEqual(probe.residency_check(rows)["reason"],"geometry check failed (view_nbytes)")

    def test_clock_and_observed_spread_are_added(self):
        calls=check_receipts()[1:4]
        result=probe.timing_summary(calls)
        values=[Fraction(c["end_ns"]-c["start_ns"],10**9*c["repeats"]) for c in calls]
        mean=sum(values)/3
        width=max(abs(v-mean) for v in values)+sum(Fraction(86,10**9*c["repeats"]) for c in calls)/3
        # t: 1e6×4ε t ≈ 6e-13 s < 1e-6 t ≈ 7e-10 s < .01×smallest printed δt (8.6e-10 s).
        self.assertAlmostEqual(result["t_s"],float(mean),delta=1e-6*abs(float(mean)))
        # δt: 1e6×4ε t ≈ 6e-13 s < 1e-6 δt ≈ 9.6e-11 s < .01×smallest printed δt (8.6e-10 s).
        self.assertAlmostEqual(result["dt_s"],float(width),delta=1e-6*abs(float(width)))

    def test_serialized_success_is_recomputed(self):
        check=probe.residency_check(check_receipts())
        check["kappa"]=123  # Deliberate corruption, not a threshold.
        self.assertNotEqual(probe.validated_check(check)["kappa"],check["kappa"])
        for field,value in (("b",2**24),("W",2**33),("Q",512),("reason",None),("receipts",[]),("status","other")):
            bad=deepcopy(check);bad[field]=value
            self.assertEqual(probe.validated_check(bad)["status"],"residency not resolved")


class ArithmeticTests(unittest.TestCase):
    def test_native_gpu_means_and_missing_support_are_descriptions(self):
        # Two one-second synthetic calls: 0.75 s active at 400 MHz and
        # 0.25 s at 800 MHz -> 500 MHz active mean, 1/2 time active.
        calls=[]
        for i,(idle,freq) in enumerate(((.25,400),(.75,800))):
            a,b=i*10**9,(i+1)*10**9
            calls.append({'arm':'R','receipt':{'start_ns':a,'end_ns':b},'gpu_state':[
                {'start_ns':a,'end_ns':b,'state':{'idle_ratio':idle,'active_freq_mhz_weighted':freq}}]})
        result=probe.describe_gpu_arms(calls)['R']
        # Frequency (description only): 1e6×8ε≈1.8e-9 < 1e-6 < .01×smallest printed relative width (.00031/.075≈.0041).
        self.assertAlmostEqual(result['active_frequency_mhz'],500,delta=1e-6*500)
        # Residency (description only): 1e6×8ε≈1.8e-9 < 1e-6 < .01×smallest printed relative width (.00031/.075≈.0041).
        self.assertAlmostEqual(result['active_residency'],.5,delta=1e-6*.5)
        calls[0]['gpu_state'][0]['end_ns']-=1  # Exactly one native ns missing.
        self.assertIn('support incomplete',probe.describe_gpu_arms(calls)['R']['active_residency'])

    def test_native_dc_variance_needs_no_alignment(self):
        from joulewise.idle_dependence import estimate_newey_west_bartlett as nw
        # Sol's alternating battery fixture, clipped to [0,57.6); the
        # integrator is a mean of retained samples, so equal support per stream.
        meter = [2.386] * 2880
        battery = [1.0 if int(i/5) % 2 == 0 else -1.0 for i in range(288)]
        def native(values, step_ns, kind):
            return probe.idle_statistics([{'stamp_ns': i*step_ns, 'power_w': p} for i,p in enumerate(values)],
                                         0,57_600_000_000,kind)
        m = native(meter,20_000_000,'meter')
        b = native(battery,200_000_000,'battery')
        spans = {'meter': m, 'battery': b, 'rails': {'reason':'not supplied'}, 'gpu': {'reason':'not supplied'}}
        result = probe.combined_idle(spans,spans)
        self.assertEqual((m['lag_count'],b['lag_count']), (500,50))
        self.assertEqual((m['sample_count'],b['sample_count']), (2880,288))
        self.assertGreater(result['dc']['se_w'],0)
        self.assertEqual(result['dc']['se_w'], math.sqrt(m['variance_w2']/2)+math.sqrt(b['variance_w2']/2))
        # Independent native-battery arithmetic: no held/interpolated meter stamps.
        expected = nw(battery,50,[.2]*288).governed_variance_of_mean_w2
        # Bit-identity: the same estimator receives the identical native inputs.
        self.assertEqual(b['variance_w2'],expected)

    def test_idle_arithmetic_overflow_is_reasoned(self):
        for stream in ('meter','rails'):
            rows = [dict({'stamp_ns':i*14_400_000_000} if stream == 'meter' else
                         {'start_ns':i*14_400_000_000,'end_ns':(i+1)*14_400_000_000},
                         power_w=1e308) for i in range(4)]
            result = probe.idle_statistics(rows,0,57_600_000_000,stream)
            self.assertIn('arithmetic unavailable',result['reason'])
            self.assertNotIn('mean_w',result)


    def test_classes_and_zero_width(self):
        epsilon=1e9/(512*39_852_331_520)
        # Hand-set endpoints derived from ε₀; κ=2 doubles the corrected scale.
        self.assertEqual(probe.classify(epsilon/4,epsilon/8,2)["class"],"RESOLVED")
        self.assertEqual(probe.classify(0,epsilon/4,2)["class"],"BELOW ATTRIBUTION LEVEL")
        result=probe.classify(0,epsilon,2)
        self.assertEqual(result["class"],"NOT RESOLVED")
        # Identical endpoint addition and multiplication on identical binary64 inputs.
        self.assertEqual(result["upper_limit"],2*(0+epsilon))
        self.assertEqual(probe.classify(-2*epsilon,epsilon,2)["reason"],"contrast negative")
        self.assertEqual(probe.format_interval(0,0),"0.00 ± 0.00")


class ExampleArray(Array):
    def __init__(self,clock,t_s):
        super().__init__(clock);self.t_s=t_s;self.count=0
    def sum(self,view):
        # Quantize accumulated elapsed time: at most one ns error per span,
        # preserving the archived per-dispatch mean in this synthetic example.
        before=round(self.count*self.t_s*1e9);self.count+=1
        self.clock.ns+=round(self.count*self.t_s*1e9)-before
        return None


def worked_records():
    """Real stream and full reader with §5 powers and native idle variance."""
    from joulewise.idle_dependence import estimate_newey_west_bartlett as nw
    check=probe.residency_check(check_receipts())
    shapes={}
    for kind,step,se in [('rails',100_000_000,math.sqrt(1.2037e-4)),('gpu',100_000_000,0),
                         ('meter',20_000_000,.05),('battery',200_000_000,.01)]:
        n=57_600_000_000//step  # Registered idle span at each native cadence.
        values=[(63 if i%64 == 0 else -1) if kind=='rails' else (-1)**i for i in range(n)]
        variance=nw(values,10_000_000_000//step,[57.6/n]*n).governed_variance_of_mean_w2
        shapes[kind]=(step,[v*se/math.sqrt(variance) for v in values])
    records=[];clock=Clock()
    for arm in probe.ORDER:
        t_s=statistics.mean(EXAMPLE_TIMES[2**25][arm])
        n=probe.planned_repeats(check['b'],t_s,probe.CALL_S)
        mx=ExampleArray(clock,t_s)
        with patch.object(probe,'collect_stack',return_value=identity()),patch.object(probe,'clock_metadata',return_value=synthetic_clock()):
            r=probe.stream(check['b'],n,arm=arm,device='macbook_m3_max',mx=mx,clock_ns=lambda:clock.ns,sleep=clock.sleep)
        duration=r['duration_s']
        pr,pe=(31.399,50.055) if arm=='R' else (28,25)  # §5 excess powers.
        h={'energy_j':{'rails':(.051+pr)*duration,'gpu':pr/2*duration,
                        'meter':(2.386+pr+pe+10)*duration,'battery':-10*duration},
           'idle':{},'anchor_shift_j':.5388,'r_max_s':.01776,'tau_s':2.302,
           'meter_edge_w':[2.386+pr+pe]*2,'battery_edge_j':[0,0],
           'capture_stack':deepcopy(probe.REFERENCE_STACK),'adapter_max_w':140,
           'adapter_source':'H 140 W adapter','battery_source':'synthetic native charging polls',
           'meter_gaps':[],'hour_as_run_s':3573.6}
        for name,sign in [('pre',1),('post',-1)]:
            start=r['idle_'+name+'_start_ns'];h['idle'][name]={}
            for kind,(step,values) in shapes.items():
                mean={'rails':.051+sign*.002,'gpu':0,'meter':2.386+10+sign*.05,'battery':-10}[kind]
                h['idle'][name][kind]=[dict({'stamp_ns':start+i*step} if kind in ('meter','battery') else
                    {'start_ns':start+i*step,'end_ns':start+(i+1)*step},power_w=mean+v) for i,v in enumerate(values)]
        h['battery_samples']=h['idle']['pre']['battery']+h['idle']['post']['battery']
        records.append({'receipt':r,'harvest':h})
    return records,check


def replay_archive(directory):
    """NOTES §1's historical timing replay, not admission of legacy data as v3.

    SUMMARY contains d_j and N, but neither clock nor new geometry leaves.
    Use NOTES' explicitly supplied 42 ns/125:3 clock for the R3/R4 replay.
    The actual ring was 8 GiB; never relabel it as a production 32-GiB ring.
    """
    source=Path(directory)/'SUMMARY.json'
    raw=json.loads(source.read_text())
    bysize={}
    for row in raw:
        if row['bytes'] not in probe.LADDER:
            continue
        calls=[{'start_ns':0,'end_ns':round(d*row['repeats']*1e9),
                'repeats':row['repeats'],**synthetic_clock()} for d in row['d_s']]
        bysize.setdefault(row['bytes'],{})['C' if row['mode']=='repeat' else 'R']=probe.timing_summary(calls)
    rungs=[]
    for b in probe.LADDER:
        if b not in bysize or set(bysize[b]) != {'R','C'}:
            raise ValueError('archive is incomplete before a resolved rung; not replayable as a whole')
        row=probe.residency_rung(b,bysize[b]['C'],bysize[b]['R']);rungs.append(row)
        print(f"archive b={b}: D={row['D_s']*1e6:.6f} µs; δD={row['dD_s']*1e6:.6f} µs; "+
              ('resolved' if row['resolved'] else 'not resolved'))
        if row['resolved']:
            break
    refusal=int(not rungs[-1]['resolved'])
    print(f"Refusal count: {refusal} of 1 replayable run; b={rungs[-1]['b']}; κ={rungs[-1].get('kappa',float('nan')):.4g}")
    print('Historical timing replay only: actual 8 GiB ring; clock supplied by NOTES §1; v3 geometry not attested.')
    print('Strict v3 reader gate: '+probe.residency_check(raw)['reason'])
    return rungs,refusal


class ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records,cls.check=worked_records()
        cls.result=probe.read_known_bytes(cls.records,cls.check)

    def test_worked_example_and_independent_arithmetic(self):
        # §5: 1% of smallest displayed width .00031 J/GB exceeds
        # 1e6×float-noise (3.2e-10 J/GB); no fitted tolerance.
        bar=.01*.00031
        for boundary,delta,width in [('rails',.075,.000306823),('dc',.344513,.002389013),('rest',.269513,.002695836)]:
            v=self.result['boundaries'][boundary]
            self.assertAlmostEqual(v['delta'],delta,delta=bar)
            self.assertAlmostEqual(v['halfwidth'],width,delta=bar)
            self.assertEqual(v['class'],'RESOLVED')
            arms={}
            for arm in ('R','C'):
                rows=[c for c in self.result['calls'] if c['arm']==arm]
                count=sum(c['N'] for c in rows)
                x=sum(Fraction(c['boundaries'][boundary]['excess_j']) for c in rows)/count
                dx=sum(Fraction(c['boundaries'][boundary]['bound_j']) for c in rows)/count
                rep=abs(Fraction(rows[0]['boundaries'][boundary]['excess_j'])/rows[0]['N']-
                        Fraction(rows[1]['boundaries'][boundary]['excess_j'])/rows[1]['N'])*max(c['N'] for c in rows)/count
                arms[arm]=(x,dx+rep)
            self.assertAlmostEqual(v['delta'],float((arms['R'][0]-arms['C'][0])*10**9/2**25),delta=bar)
            self.assertAlmostEqual(v['halfwidth'],float((arms['R'][1]+arms['C'][1])*10**9/2**25),delta=bar)
            for retired in ('alpha','gamma_c','gamma_d','r','epsilon_flip'): self.assertNotIn(retired,v)
        self.assertEqual([c['N'] for c in self.result['calls']],[2459648,2962432,2962432,2459648])
        self.assertEqual(self.result['printed']['contrasts']['rails'],'0.07500 ± 0.00031')
        self.assertEqual(self.result['printed']['share'],'0.2177 ± 0.0024')
        self.assertEqual(self.result['printed']['claim_lines'],{})

    def test_real_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'input.json';p.write_text(json.dumps({'records':self.records,'check':self.check}))
            result=subprocess.run([sys.executable,'-I','-B',str(probe.ROOT/'scripts/bytes_stream_test.py'),'read',str(p)],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout),json.loads(json.dumps(self.result)))  # Identical code/inputs.

    def test_failed_check_prints_no_interval(self):
        for check in (probe.residency_check(check_receipts(resolves=False)),{},None,
                      {**self.check,'reason':'spurious'},{**self.check,'b':2**24}):
            result=probe.read_known_bytes(self.records,check)
            for v in result['boundaries'].values(): self.assertEqual(v['class'],'UNDETERMINED')
            self.assertNotIn('±',json.dumps(result['printed']['contrasts']))
            self.assertIsInstance(result['share']['f'],str)
            self.assertEqual(len(result['calls']),len(probe.ORDER))

    def test_geometry_and_legacy_schema_faults(self):
        for field,value in (('schema_version','joulewise.bytes_stream.v2'),('ring_shape',[1024,2**24]),
                            ('view_nbytes',2**24),('bytes_read',0),('sweeps',0),('view_order','repeat')):
            records=deepcopy(self.records);records[0]['receipt'][field]=value
            result=probe.read_known_bytes(records,self.check)
            self.assertEqual(result['boundaries']['rails']['class'],'UNDETERMINED')
            self.assertIn(field,result['boundaries']['rails']['reason'])
            self.assertNotIn('±',json.dumps(result['printed']['contrasts']))

    def test_hour_clock_prerequisite_is_retained_and_refuses(self):
        for field in ('clock','clock_resolution_s','clock_tick_den'):
            records=deepcopy(self.records);del records[0]['receipt'][field]
            result=probe.read_known_bytes(records,self.check)
            for value in result['boundaries'].values():
                self.assertEqual(value['class'],'UNDETERMINED')
                self.assertIn('clock prerequisite missing',value['reason'])
                self.assertIn(field,value['reason'])
            self.assertNotIn('±',json.dumps(result['printed']['contrasts']))
            self.assertEqual(len(result['input_records']),len(probe.ORDER))

    def test_order_and_missing_call_preserve_computable_arms(self):
        for records in (self.records[:-1],[self.records[i] for i in (0,2,1,3)]):
            result=probe.read_known_bytes(records,self.check)
            self.assertEqual(result['boundaries']['rails']['class'],'UNDETERMINED')
            self.assertEqual(len(result['calls']),len(records))
        c=probe.read_known_bytes(self.records[1:],self.check)['boundaries']['rails']['arms']['C']
        self.assertIsInstance(c['x'],float)

    def test_gap_sources_and_transient(self):
        records=deepcopy(self.records);records[1]['harvest']['meter_gaps']=[{'span':'stream','missing_samples':1}]
        result=probe.read_known_bytes(records,self.check)
        # Gap: 1e6×4ε×2.8≈2.5e-9 J < 2.8e-6 J; divided by 2*N_C*b_GB it is < .01*.00031 J/GB.
        self.assertAlmostEqual(result['calls'][1]['meter_gaps']['bound_j'],.020*140,delta=1e-6*.020*140)
        for beta,w in [('dc',.002403097),('rest',.002709920)]:
            self.assertAlmostEqual(result['boundaries'][beta]['halfwidth'],w,delta=.01*.00031)
        records[1]['harvest']['adapter_source']=''
        self.assertIn('gap power sources',probe.read_known_bytes(records,self.check)['boundaries']['dc']['reason'])
        records=deepcopy(self.records);records[0]['harvest']['energy_j']['rails']+=5*records[0]['receipt']['duration_s']
        v=probe.read_known_bytes(records,self.check)['boundaries']['rails']
        self.assertEqual(probe.format_interval(v['delta'],v['halfwidth']),'0.098 ± 0.023')
        self.assertEqual(v['class'],'RESOLVED')
        self.assertGreater(v['arms']['R']['rep'],0)

    def test_small_true_contrast_uses_check_kappa_and_h2_upper_place(self):
        # Revision §5's .00030 J/GB case. Set R's per-dispatch excess to
        # x_C + b*Δ/1e9; all baseline and edge inputs stay the example's.
        records=deepcopy(self.records)
        target=.00030
        xc=self.result['boundaries']['rails']['arms']['C']['x']
        for row in records:
            r,h=row['receipt'],row['harvest']
            if r['arm']=='R':
                h['energy_j']['rails']=.051*r['duration_s']+r['repeats']*(xc+r['bytes_per_read']*target/1e9)
        result=probe.read_known_bytes(records,self.check)
        value=result['boundaries']['rails']
        self.assertEqual(value['class'],'NOT RESOLVED')
        self.assertAlmostEqual(value['delta'],target,delta=.01*.00031)  # §5's common bar.
        expected=float((Fraction(value['delta'])+Fraction(value['halfwidth']))*Fraction(result['kappa']))
        # Upper limit: 1e6×4ε×.00377≈3.3e-12 < 1e-6×.00377≈3.8e-9 < .01*.00031 J/GB.
        self.assertAlmostEqual(value['upper_limit'],expected,delta=1e-6*abs(expected))
        self.assertIn('0.00030 ± 0.00031',result['printed']['claim_lines']['rails'])
        self.assertIn('memory-traffic energy contrast',result['printed']['claim_lines']['rails'])
        self.assertIn('under the stated model and constant payload',result['printed']['claim_lines']['rails'])
        # §4 and §5 require the interval's decimal place: .00377.
        self.assertIn('upper limit 0.00377 J/GB',result['printed']['claim_lines']['rails'])
        self.assertEqual(format(value['upper_limit'],'.2g'),'0.0038')

    def test_boundary_specific_missing_fields(self):
        for leaf,affected in [('r_max_s',('rails','gpu','dc','rest')),('anchor_shift_j',('rails','gpu','rest'))]:
            records=deepcopy(self.records);del records[0]['harvest'][leaf]
            result=probe.read_known_bytes(records,self.check)
            for beta in affected: self.assertEqual(result['boundaries'][beta]['class'],'UNDETERMINED')
            self.assertIsInstance(result['boundaries']['rails']['delta'],float)
            if leaf == 'anchor_shift_j':
                # §3/§4: retain the numeric estimate, but no precision without its half-width.
                for beta in ('rails','gpu','rest'):
                    self.assertEqual(result['printed']['contrasts'][beta],
                                     result['boundaries'][beta]['description'])
                    self.assertTrue(result['printed']['contrasts'][beta].startswith('not defined ('))
        records=deepcopy(self.records);records[0]['harvest']['idle']['pre']['gpu']=[]
        result=probe.read_known_bytes(records,self.check)
        self.assertEqual(result['boundaries']['gpu']['class'],'UNDETERMINED')
        self.assertEqual(result['boundaries']['rails']['class'],'RESOLVED')

    def test_stack_scope(self):
        for field in ('python','kernel_library','os_version'):
            records=deepcopy(self.records);records[0]['receipt']['stack'][field]='different'
            result=probe.read_known_bytes(records,self.check)
            self.assertEqual(result['boundaries']['rails']['class'],'UNDETERMINED' if field=='os_version' else 'RESOLVED')
        records=deepcopy(self.records);records[0]['harvest']['capture_stack']['measurement_boundary_label']['rails']=['cpu_power']
        result=probe.read_known_bytes(records,self.check)
        self.assertEqual(result['boundaries']['dc']['class'],'RESOLVED')
        for beta in ('rails','rest','gpu'): self.assertEqual(result['boundaries'][beta]['class'],'UNDETERMINED')

    def test_native_order_not_repaired(self):
        for stream in ('rails','gpu','meter','battery'):
            records=deepcopy(self.records);rows=records[0]['harvest']['idle']['pre'][stream]
            rows[1],rows[0]=rows[0],rows[1]
            result=probe.read_known_bytes(records,self.check)
            beta='dc' if stream in ('meter','battery') else stream
            self.assertEqual(result['boundaries'][beta]['class'],'UNDETERMINED')
            self.assertIn(stream,result['boundaries'][beta]['reason'])
            self.assertEqual(len(result['input_records'][0]['harvest']['idle']['pre'][stream]),len(rows))

    def test_hour_timing_is_description_only(self):
        result=self.result
        self.assertIn('thermal journal missing',result['calls'][0]['thermal']['spans'])
        records=deepcopy(self.records)
        for row in records:
            r=row['receipt'];r['end_ns']=r['start_ns']+round(r['duration_s']*(.5 if r['arm']=='R' else 1)*1e9)
        actual=probe.read_known_bytes(records,self.check)
        self.assertLess(actual['hour_timing']['D_s'],0)
        self.assertEqual(actual['kappa'],result['kappa'])  # Identical check code/input.

    def test_missing_and_invalid_native_leaves_preserve_boundary_scope(self):
        # Fault the admitted native prerequisites; these tests survive the
        # change in contrast geometry. No invalid row may be dropped to shrink
        # a width, and a DC prerequisite prevents every boundary's validity.
        cases=[
            (('energy_j','rails'),None,('rails','rest')),
            (('energy_j','gpu'),None,('gpu',)),
            (('energy_j','meter'),None,('rails','gpu','dc','rest')),
            (('energy_j','battery'),None,('rails','gpu','dc','rest')),
            (('battery_edge_j',),[-1,0],('rails','gpu','dc','rest')),
            (('meter_edge_w',),[None,0],('rails','gpu','dc','rest')),
            (('meter_gaps',),[{'span':'invalid','missing_samples':1}],('rails','gpu','dc','rest')),
            (('battery_samples',),[],('rails','gpu','dc','rest')),
            (('tau_s',),None,('rails','gpu','dc','rest')),
        ]
        for stream in ('rails','gpu','meter','battery'):
            cases.append((('idle','pre',stream,0,'power_w'),float('nan'),
                          ('rails','gpu','dc','rest') if stream in ('meter','battery') else
                          ('rails','rest') if stream=='rails' else ('gpu',)))
        for path,bad,affected in cases:
            records=deepcopy(self.records);parent=records[0]['harvest']
            for key in path[:-1]: parent=parent[key]
            parent[path[-1]]=bad
            with self.subTest(path=path):
                result=probe.read_known_bytes(records,self.check)
                self.assertEqual(len(result['input_records']),len(records))
                for beta in affected:
                    self.assertEqual(result['boundaries'][beta]['class'],'UNDETERMINED')
                if 'rails' not in affected:
                    self.assertEqual(result['boundaries']['rails']['class'],'RESOLVED')
                if 'dc' not in affected:
                    self.assertEqual(result['boundaries']['dc']['class'],'RESOLVED')

    def test_dc_zero_lower_endpoint_refuses_and_null_containers_are_reasoned(self):
        real=probe.reduce_boundary
        def zero_lower(calls,sizes,boundary):
            value=real(calls,sizes,boundary)
            if boundary=='dc': value['delta']=value['halfwidth']
            return value
        with patch.object(probe,'reduce_boundary',side_effect=zero_lower):
            result=probe.read_known_bytes(self.records,self.check)
        for v in result['boundaries'].values():
            self.assertEqual(v['class'],'UNDETERMINED')
            self.assertEqual(v['reason'],'contrast not resolved')  # DC requires strictly >0.
        for records in (None,{},[None],[{'receipt':None,'harvest':None}]):
            result=probe.read_known_bytes(records,self.check)
            self.assertTrue(all(v['class']=='UNDETERMINED' for v in result['boundaries'].values()))
            json.dumps(result,allow_nan=False)


if __name__=='__main__':
    if '--replay-archive' in sys.argv:
        replay_archive(sys.argv[-1])
    elif '--worked-example' in sys.argv:
        records,check=worked_records(); result=probe.read_known_bytes(records,check)
        print('Revision / real reader (J/GB):')
        for beta,delta,width in [('rails',.075,.000306823),('dc',.344513,.002389013),('rest',.269513,.002695836)]:
            v=result['boundaries'][beta]
            print(f"{beta}: revision {delta:.9f} ± {width:.9f}; reader {v['delta']:.9f} ± {v['halfwidth']:.9f}; {v['class']}")
        print('Revision κ=6.213; reader κ='+format(result['kappa'],'.4g'))
        print('Revision f=0.2177 ± 0.0024; reader f='+result['printed']['share'])
        for beta in ('rails','dc','rest'):
            print(beta+' x_R/x_C mJ='+', '.join(format(result['boundaries'][beta]['arms'][a]['x']*1000,'.7f') for a in ('R','C')))
            print(beta+' δx_R/δx_C µJ='+', '.join(format(result['boundaries'][beta]['arms'][a]['dx']*1e6,'.4f') for a in ('R','C')))
    else:
        unittest.main()
