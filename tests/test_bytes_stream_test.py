"""Synthetic §2 receipt checks. No Metal, telemetry or hardware timing evidence."""
from copy import deepcopy
import io
import json
import math
import statistics
import random
from fractions import Fraction as F
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch
import weakref

from scripts import bytes_stream_test as probe
from joulewise.flags.collect import RUNTIME_PACKAGES


def synthetic_clock():
    return {"clock": "CLOCK_MONOTONIC_RAW", "clock_resolution_s": 4.2e-8,
            "clock_tick_num_ns": 125, "clock_tick_den": 3,
            "clock_tick_source": "synthetic 125/3 ns model (lead measurement 2026-10-28)",
            "clock_ns_conversion": "unknown", "clock_ns_conversion_source": "synthetic"}


class Array:
    pass


class FakeMLX:
    uint8 = "uint8"
    __version__ = "0.31.2"

    def __init__(self):
        self.events = []
        self.ns = 0
        self.results = []
        self.payload = None

    def ones(self, shape, dtype):
        self.events.append(("ones", shape, dtype))
        data = Array()
        self.payload = weakref.ref(data)
        return data

    def sum(self, data):
        assert data is self.payload()
        self.events.append(("sum",))
        self.ns += 100_000_000
        result = Array()
        self.results.append(result)
        return result

    def eval(self, value):
        self.events.append(("eval", id(value)))
        self.ns += 25_000_000

    def synchronize(self):
        self.events.append(("sync",))
        self.ns += 125_000_000

    def clock(self):
        self.events.append(("stamp", self.ns))
        return self.ns

    def sleep(self, seconds):
        assert self.payload() is not None, "payload must stay resident through post-idle"
        self.events.append(("sleep", seconds))
        self.ns += round(seconds * 1_000_000_000)


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.reference, self.versions = probe.registered_stack()
        self.stack = {key: deepcopy(self.reference[key]) for key in
                      ("os_version", "hardware_unit", "runtime_version", "kernel_library")}
        self.stack.update(deepcopy(self.versions))
        self.stack["git_commit"] = "a different checkout by design"
        self.stack.update({field: "not_applicable" for field in probe.NOT_APPLICABLE})
        self.capture = {key: deepcopy(self.reference[key]) for key in
                        ("telemetry_backend", "measurement_boundary_label")}

    def run_stream(self, mx=None, **kwargs):
        mx = mx or FakeMLX()
        with patch.object(probe, "collect_stack", return_value=self.stack):
            return probe.stream(1024, 3, device="macbook_m3_max", mx=mx,
                                clock_ns=kwargs.pop("clock_ns", mx.clock), sleep=mx.sleep, **kwargs), mx

    def test_order_warmup_idles_settle_and_fresh_reductions(self):
        receipt, mx = self.run_stream()
        names = [event[0] for event in mx.events]
        self.assertEqual(names, ["ones", "eval", "sync", "sum", "eval", "sync",
                                 "sleep", "stamp", "sleep", "stamp", "sleep", "stamp",
                                 "sum", "eval", "sum", "eval", "sum", "eval", "sync",
                                 "stamp", "sleep", "stamp", "sleep", "stamp"])
        self.assertEqual([event[1] for event in mx.events if event[0] == "sleep"], [3, 57.6, 3, 3, 57.6])
        self.assertEqual(mx.events[0], ("ones", (1024,), "uint8"))
        self.assertEqual(len(mx.results), 4)  # one warm-up plus three measured reads
        self.assertEqual(len({event[1] for event in mx.events if event[0] == "eval"}), 5)
        self.assertEqual(receipt["schema_version"], "joulewise.bytes_stream.v2")
        self.assertEqual(receipt["bytes_read"], 3072)  # excludes the warm-up
        self.assertEqual(receipt["bytes_per_read"], 1024)
        self.assertEqual(receipt["repeats"], 3)
        self.assertIs(receipt["non_claim"], True)
        self.assertEqual(receipt["stack_check"]["status"], "pending_capture")
        self.assertEqual(receipt, json.loads(json.dumps(receipt, allow_nan=False)))

    def test_stamps_use_one_clock_and_exclude_idle_settle_and_warmup(self):
        receipt, mx = self.run_stream()
        keys = ("idle_pre_start_ns", "idle_pre_end_ns", "start_ns", "end_ns",
                "idle_post_start_ns", "idle_post_end_ns")
        self.assertEqual([receipt[k] for k in keys], [v[1] for v in mx.events if v[0] == "stamp"])
        self.assertEqual(receipt["clock"], "CLOCK_MONOTONIC_RAW")
        self.assertEqual(receipt["idle_pre_end_ns"] - receipt["idle_pre_start_ns"], 57_600_000_000)
        self.assertEqual(receipt["idle_post_end_ns"] - receipt["idle_post_start_ns"], 57_600_000_000)
        self.assertEqual(receipt["start_ns"] - receipt["idle_pre_end_ns"], 3_000_000_000)
        self.assertEqual(receipt["idle_post_start_ns"] - receipt["end_ns"], 3_000_000_000)
        self.assertEqual(receipt["end_ns"] - receipt["start_ns"], 500_000_000)
        # Exact only because this synthetic interval is the binary-exact 1/2 s.
        self.assertEqual(receipt["duration_s"], 0.5)

    def test_scan_zero_idle_and_settle_still_stamps_and_warms(self):
        receipt, mx = self.run_stream(idle_s=0, settle_s=0)
        self.assertNotIn("sleep", [v[0] for v in mx.events])
        self.assertEqual(receipt["idle_pre_start_ns"], receipt["idle_pre_end_ns"])
        self.assertEqual(receipt["idle_pre_end_ns"], receipt["start_ns"])
        self.assertEqual(receipt["end_ns"], receipt["idle_post_start_ns"])
        self.assertEqual(receipt["idle_post_start_ns"], receipt["idle_post_end_ns"])
        self.assertEqual(len(mx.results), 4)

    def test_default_clock_is_raw_for_every_stamp(self):
        mx = FakeMLX()
        with patch.object(probe, "collect_stack", return_value=self.stack), \
             patch.object(probe.time, "clock_gettime_ns", side_effect=lambda _: mx.clock()) as raw:
            probe.stream(1, 1, device="macbook_m3_max", mx=mx, sleep=mx.sleep)
        self.assertEqual(raw.call_count, 6)
        for call in raw.call_args_list:
            self.assertEqual(call.args, (probe.time.CLOCK_MONOTONIC_RAW,))

    def test_bad_counts_devices_or_seconds_fail_before_array_calls(self):
        mx = FakeMLX()
        for byte_count, repeats in ((0, 1), (1, 0), (True, 1), (1, True), (1.0, 1), (-1, 1)):
            with self.subTest(counts=(byte_count, repeats)), self.assertRaises(ValueError):
                probe.stream(byte_count, repeats, device="macbook_m3_max", mx=mx)
        for name in ("idle_s", "settle_s"):
            for value in (-1, float("nan"), float("inf"), True, "3"):
                with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                    probe.stream(1, 1, device="macbook_m3_max", mx=mx, **{name: value})
        for device in (None, "", " "):
            with self.subTest(device=device), self.assertRaises(ValueError):
                probe.stream(1, 1, device=device, mx=mx)
        self.assertEqual(mx.events, [])

    def test_invalid_clocks_do_not_emit_a_receipt(self):
        for stamps in ((0, 1, 2, 2, 3, 4), (0, 2, 1, 3, 4, 5), (1, 0, 2, 3, 4, 5),
                       (0, 1, 2, 3, 4, 4), (-1, 1, 2, 3, 4, 5), (0, 1, 2.0, 3, 4, 5)):
            with self.subTest(stamps=stamps), self.assertRaises(ValueError):
                values = iter(stamps)
                self.run_stream(clock_ns=lambda: next(values))

    def test_collect_stack_uses_pass1_sources_and_explicit_device(self):
        with patch.object(probe, "runtime_versions", return_value=self.versions) as versions, \
             patch.object(probe.platform, "platform", return_value="observed-os"), \
             patch.object(probe.platform, "machine", return_value="observed-machine"), \
             patch.object(probe.subprocess, "check_output", return_value="observed-head\n") as git:
            stack = probe.collect_stack(FakeMLX(), "config-device")
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
             patch.object(probe.subprocess, "check_output", return_value="head"):
            for prepare, expected in ((None, "unavailable"), ({}, "unavailable"),
                                      ({"kernel_library": "observed-kernel"}, "observed-kernel")):
                self.assertEqual(probe.collect_stack(FakeMLX(), "device", prepare=prepare)["kernel_library"], expected)

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

    def test_mismatch_preserves_receipt_instead_of_discarding_measurement(self):
        self.stack["os_version"] = "different"
        receipt, _ = self.run_stream()
        self.assertEqual(receipt["stack_check"]["differences"], ["os_version"])
        self.assertEqual(receipt["bytes_read"], 3072)

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


    def test_cli_flags_and_receipt_serialization_without_metal(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(probe, "stream", return_value={"fake": True}) as stream, \
             patch("sys.stdout", new_callable=io.StringIO) as stdout:
            out = Path(tmp) / "receipt.json"
            self.assertEqual(probe.main(["--bytes", "1024", "--repeats", "3", "--device", "config-device",
                                         "--idle-s", "0", "--settle-s", "0", "--out", str(out)]), 0)
            stream.assert_called_once_with(1024, 3, device="config-device", idle_s=0, settle_s=0)
            self.assertEqual(out.read_text(), '{\n  "fake": true\n}\n')
            self.assertEqual(json.loads(stdout.getvalue()), {"fake": True})

    def test_cli_end_to_end_with_fake_mlx_and_real_identity_sources(self):
        mx = FakeMLX()
        package = ModuleType("mlx")
        package.core = mx
        with tempfile.TemporaryDirectory() as tmp, patch.dict(sys.modules, {"mlx": package, "mlx.core": mx}), \
             patch.object(probe.time, "sleep", side_effect=mx.sleep), \
             patch.object(probe.time, "clock_gettime_ns", side_effect=lambda _: mx.clock()), \
             patch("sys.stdout", new_callable=io.StringIO) as stdout:
            out = Path(tmp) / "receipt.json"
            probe.main(["--bytes", "1024", "--repeats", "3", "--device", "macbook_m3_max",
                        "--out", str(out)])
            receipt = json.loads(out.read_text())
            self.assertEqual(receipt, json.loads(stdout.getvalue()))
        self.assertEqual(receipt["schema_version"], "joulewise.bytes_stream.v2")
        self.assertEqual(receipt["bytes_read"], 3072)
        self.assertEqual(receipt["stack"]["python"], probe.platform.python_version())
        self.assertEqual(set(receipt["stack"]["packages"]), set(RUNTIME_PACKAGES))
        self.assertEqual(len(receipt["stack"]["git_commit"]), 40)
        self.assertEqual(receipt["stack_check"]["pending_fields"], list(probe.CAPTURE_FIELDS))

    def test_help_needs_no_mlx(self):
        result = subprocess.run([sys.executable, "-B", str(probe.ROOT / "scripts/bytes_stream_test.py"), "--help"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--idle-s", result.stdout)
        self.assertIn("--settle-s", result.stdout)
        self.assertIn("--device", result.stdout)


class ReadingRuleArithmeticTests(unittest.TestCase):
    """Independent arithmetic fixtures for the normative rule, not hardware evidence."""

    @staticmethod
    def knee(calls):
        receipts = [{"bytes_per_read": size, "start_ns": 0, "end_ns": duration*1e9,
                     "repeats": n, **synthetic_clock()} for size, rows in calls.items() for duration, n in rows]
        result = probe.knee_scan(receipts)
        marg = {p["size"]: p["m_bytes_s"] for p in result["pairs"] if p["m_bytes_s"] is not None}
        dm = {p["size"]: p["dm_bytes_s"] for p in result["pairs"] if p["m_bytes_s"] is not None}
        return result["K"], marg, dm, result["threshold"]

    @staticmethod
    def scan_model(cache, quantized):
        calls = {}
        for s in (2**k for k in range(14, 36)):
            throughput = 1e12 if cache and s < 2**26 else 331.6e9
            td = 50e-6 + s / throughput
            n = math.floor(2 / td)
            duration = round(n * td * 1e9) / 1e9 if quantized else n * td
            calls[s] = [(duration, n)] * 3
        return calls

    def test_dram_only_rounding_never_supplies_cache_evidence(self):
        for quantized in (False, True):
            with self.subTest(quantized=quantized):
                self.assertIsNone(self.knee(self.scan_model(False, quantized))[0])

    def test_worked_example_knee_survives_stamp_quantization(self):
        for quantized in (False, True):
            with self.subTest(quantized=quantized):
                self.assertEqual(self.knee(self.scan_model(True, quantized))[0], 2**26)

    def test_zero_negative_and_uncertain_differences_are_undefined(self):
        for duration in (1.0, 0.9, 1.000000001):
            calls = {2**k: [(duration if k == 15 else 1.0, 1)] * 3 for k in range(14, 36)}
            k, marg, _, _ = self.knee(calls)
            self.assertNotIn(2**15, marg)
            self.assertIsNone(k)

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

    def test_revised_worked_energy_publication_digits_and_bounded_gap(self):
        # Recompute §3 directly from §5 input ratios. Compare publication
        # strings; these are rounding properties, not new acceptance bars.
        gb, b = 1e9, 2**32
        payload = {'S': b, 'C1': 2**22, 'C3': 2**23, 'C2': 2**24}
        thr = 4597412096 * 512 / 7.098
        idle_r, idle_dc = .051, (6101.072862 - 5967.417892) / 56.018813
        sr = 223.22/7.098 - idle_r
        se = 577.210005/11.017813 - (idle_dc - idle_r)
        rows = {}
        for arm, size in payload.items():
            td = 50e-6 + size / (thr if arm == 'S' else 1e12)
            n = math.floor((500 if arm == 'S' else 250) / td)
            t = n * td
            pr, pe = (sr, se) if arm == 'S' else (28., 25.)
            br = .5388 + t * (.002 + 2 * math.sqrt(1.2037e-4/2))
            bd = 2 * (pr+pe+idle_dc) * (.017762388+.020) + t * (.05 + 2 * (.05+.01)/math.sqrt(2))
            rows[arm] = (n, {'rails': pr*t/n, 'dc': (pr+pe)*t/n, 'rest': pe*t/n},
                         {'rails': br/n, 'dc': bd/n, 'rest': (br+bd)/n})
        def reduce(beta, gap_j=0):
            calls = []
            for arm in ('S','C1','C3','C2','C2','C3','C1','S'):
                n,energy,bounds = rows[arm]
                calls.append({'arm': arm, 'N': n, 'boundaries': {beta: {
                    'excess_j': energy[beta]*n,
                    'bound_j': bounds[beta]*n + (gap_j if arm=='C2' and beta!='rails' and
                                                not any(c['arm']=='C2' for c in calls) else 0)}}})
            v = probe.reduce_boundary(calls, payload, beta)
            return v['delta'],v['halfwidth'],v['epsilon_flip']*1e6
        self.assertEqual([f'{reduce(x)[1]:.8f}' for x in ('rails','dc','rest')],
                         ['0.00057180','0.00252421','0.00244408'])
        self.assertEqual([f'{reduce(x)[2]:.2f}' for x in ('rails','dc','rest')], ['7.20','31.79','30.78'])
        for beta, digits in (('dc','0.00255396'), ('rest','0.00247383')):
            delta, width, _ = reduce(beta, .020*140)
            self.assertEqual(f'{width:.8f}', digits)
            self.assertGreater(delta-width, 0)
        dr, ur, _ = reduce('rails')
        dd, ud, _ = reduce('dc')
        f = dr/dd
        self.assertEqual(f'{f:.4f}', '0.3458')
        self.assertEqual(f'{(ur+abs(f)*ud)/abs(dd):.4f}', '0.0075')
        # Sol's zero-rails case is nonsingular with valid DC.
        self.assertEqual((.001 + abs(0/.1)*.002)/abs(.1), .01)


class ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Real stream(), full §5 counts and sizes, constant-memory fake array.
        # Per-dispatch clocks use integer ns, as the actual receipts do.
        class ProductionMLX:
            uint8 = 'uint8'
            __version__ = '0.31.2'
            def __init__(self, ns, dispatch_ns):
                self.ns,self.dispatch_ns,self.sums,self.sleeps = ns,dispatch_ns,0,[]
            def ones(self, shape, dtype):
                return Array()
            def sum(self, data):
                self.sums += 1
                return Array()
            def eval(self, value):
                self.ns += self.dispatch_ns
            def synchronize(self):
                pass
            def sleep(self, seconds):
                self.sleeps.append(seconds)
                self.ns += round(seconds*1e9)
        from joulewise.idle_dependence import estimate_newey_west_bartlett as nw
        cls.payload = {'S': 2**32,'C1':2**22,'C3':2**23,'C2':2**24}
        cls.scan = real_scan_cli(worked5)
        cls.dram_scan = real_scan_cli(dram_only)
        reference,versions = probe.registered_stack()
        stack = deepcopy(reference);stack.update(versions)
        cls.records=[]
        ns=0
        idle_dc=(6101.072862-5967.417892)/56.018813
        # Native alternating fixtures scaled so governed per-span SEs are
        # the §5 assumptions. Battery is charging, so measured max discharge=0.
        shapes={}
        for kind,step,se in [('rails',100_000_000,math.sqrt(1.2037e-4)),('gpu',100_000_000,0),
                             ('meter',20_000_000,.05),('battery',200_000_000,.01)]:
            n=57_600_000_000//step
            values=[(-1)**i for i in range(n)]
            var=nw(values,10_000_000_000//step,[57.6/n]*n).governed_variance_of_mean_w2
            shapes[kind]=(step,[v*se/math.sqrt(var) for v in values])
        for arm in ('S','C1','C3','C2','C2','C3','C1','S'):
            size=cls.payload[arm]
            td=50e-6+size/(4597412096*512/7.098 if arm=='S' else 1e12)
            n=math.floor((500 if arm=='S' else 250)/td)
            mx=ProductionMLX(ns,round(td*1e9))
            with patch.object(probe,'collect_stack',return_value=deepcopy(stack)):
                r=probe.stream(size,n,device='macbook_m3_max',mx=mx,clock_ns=lambda:mx.ns,sleep=mx.sleep)
            assert mx.sums==n+1
            assert mx.sleeps==[3,57.6,3,3,57.6]
            ns=mx.ns
            t=r['duration_s']
            pr,pe=(223.22/7.098-.051,577.210005/11.017813-(idle_dc-.051)) if arm=='S' else (28.,25.)
            h={'energy_j':{'rails':(.051+pr)*t,'gpu':(pr/2)*t,
                           'meter':(idle_dc+pr+pe+10)*t,'battery':-10*t},
               'idle':{},'anchor_shift_j':.5388,'r_max_s':.017762388,'tau_s':2.302,
               'meter_edge_w':[idle_dc+pr+pe]*2,'battery_edge_j':[0,0],
               'capture_stack':reference,'adapter_max_w':140,'adapter_source':'H adapter nameplate 140 W',
               'battery_source':'synthetic native battery polls','meter_gaps':[]}
            for name,sign in [('pre',1),('post',-1)]:
                start=r['idle_'+name+'_start_ns'];h['idle'][name]={}
                for kind,(step,values) in shapes.items():
                    mean={'rails':.051+sign*.002,'gpu':0,'meter':idle_dc+10+sign*.05,'battery':-10}[kind]
                    h['idle'][name][kind]=[dict({'stamp_ns':start+i*step} if kind in ('meter','battery') else
                        {'start_ns':start+i*step,'end_ns':start+(i+1)*step},power_w=mean+v) for i,v in enumerate(values)]
            h['battery_samples']=h['idle']['pre']['battery']+h['idle']['post']['battery']
            cls.records.append({'receipt':r,'harvest':h})
        cls.result=probe.read_known_bytes(cls.records,cls.scan)

    def test_full_production_shaped_palindrome_reader_and_cli(self):
        res=self.result
        self.assertEqual([c['arm'] for c in res['calls']],['S','C1','C3','C2','C2','C3','C1','S'])
        # Common bar 5.7e-6 J/GB is derived in §3/§5, not a new tolerance.
        for beta,delta,width in [('rails',.066716626,.000571796),('dc',.192943505,.002524213),
                                  ('rest',.126226879,.002444084)]:
            v=res['boundaries'][beta]
            self.assertLessEqual(abs(v['delta']-delta),5.7e-6)
            self.assertLessEqual(abs(v['halfwidth']-width),5.7e-6)
            self.assertEqual(v['class'],'RESOLVED')
        self.assertEqual(f"{res['share']['df']:.4f}",'0.0075')
        self.assertEqual(res['printed']['contrasts']['dc'],'0.1929 ± 0.0025')
        self.assertEqual(res['printed']['share'],'0.3458 ± 0.0075')
        self.assertEqual(res['calls'][0]['thermal']['spans'],'not defined (thermal journal missing)')
        # Real read CLI serialization from the same production-shaped records.
        with tempfile.TemporaryDirectory() as tmp, patch('sys.stdout',new_callable=io.StringIO) as out:
            path=Path(tmp)/'input.json'
            path.write_text(json.dumps({'scan':self.scan,'records':self.records},allow_nan=False))
            self.assertEqual(probe.main(['read',str(path)]),0)
            self.assertEqual(json.loads(out.getvalue()),json.loads(json.dumps(res)))

    def test_stream_and_idle_gaps_preserve_validity_and_disclose_sources(self):
        records=deepcopy(self.records)
        records[3]['harvest']['meter_gaps']=[{'span':'stream','missing_samples':1}]
        res=probe.read_known_bytes(records,self.scan)
        self.assertEqual(f"{res['calls'][3]['meter_gaps']['bound_j']:.1f}",'2.8')
        for beta in ('dc','rest'):
            self.assertEqual(res['boundaries'][beta]['class'],'RESOLVED')
        for beta,width in [('dc',.00255396),('rest',.00247383)]:
            self.assertLessEqual(abs(res['boundaries'][beta]['halfwidth']-width),5.7e-6)
        direct=probe.meter_gap_bound([{'span':'pre','missing_samples':2},{'span':'post','missing_samples':1}],
            duration_s=250,idle_lengths_s={'pre':57.6,'post':57.6},adapter_max_w=140,
            adapter_source='nameplate',battery_max_w=5,battery_source='native polls')
        self.assertEqual(direct['P_max_w'],145)
        self.assertEqual(direct['bound_j'],sum(n*.020*145*250/(2*57.6) for n in (2,1)))

    def test_metadata_disclosure_and_physical_mismatch_classes(self):
        records=deepcopy(self.records)
        records[0]['receipt']['stack']['packages']['transformers']='metadata-only'
        res=probe.read_known_bytes(records,self.scan)
        self.assertEqual(res['boundaries']['rails']['class'],'RESOLVED')
        self.assertIn('packages.transformers',res['stack_comparisons'][0]['disclosure_differences'])
        records[0]['receipt']['stack']['os_version']='different-build'
        res=probe.read_known_bytes(records,self.scan)
        self.assertEqual(res['boundaries']['rails']['class'],'UNDETERMINED')
        self.assertEqual(res['boundaries']['rails']['reason'],'stack differs in: os_version')

    def test_missing_native_support_and_battery_keep_receipts_and_rails_numbers(self):
        records=deepcopy(self.records)
        records[0]['harvest']['idle']['pre']['battery']=[]
        records[0]['harvest']['energy_j']['battery']=None
        res=probe.read_known_bytes(records,self.scan)
        self.assertIn('delta',res['boundaries']['rails'])
        self.assertEqual(len(res['calls']),8)
        self.assertEqual(res['share']['f'],'not defined (DC contrast not valid)')
        records=deepcopy(self.records)
        records[0]['harvest']['idle']['pre']['meter']=records[0]['harvest']['idle']['pre']['meter'][:4]
        res=probe.read_known_bytes(records,self.scan)
        self.assertTrue(any('idle variance not defined' in s for s in res['reasons']))

    def test_missing_knee_and_invalid_dc_are_reasoned_results(self):
        result=probe.read_known_bytes(self.records,{'K':None,'status':'knee not found'})
        self.assertEqual(result['boundaries']['rails']['reason'],'knee not found')
        self.assertEqual(result['boundaries']['rails']['description'],'not defined (knee not found)')
        records=deepcopy(self.records)
        for record in records:
            h=record['harvest'];t=record['receipt']['duration_s']
            h['energy_j']['meter']=(10+(6101.072862-5967.417892)/56.018813)*t
        result=probe.read_known_bytes(records,self.scan)
        self.assertEqual(result['boundaries']['rails']['reason'],'contrast not resolved')
        self.assertEqual(result['share']['df'],'not defined (DC contrast not valid)')

    def read_cli(self, records, scan=None):
        # Every variant serializes/reloads the real stream receipts and all
        # harvest data before entering the actual read CLI. Synthetic only.
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'input.json'
            path.write_text(json.dumps({'records':records,'scan':self.scan if scan is None else scan},allow_nan=False))
            cli=subprocess.run([sys.executable,'-B',str(probe.ROOT/'scripts/bytes_stream_test.py'),
                                'read',str(path)],capture_output=True,text=True)
            self.assertEqual(cli.returncode,0,cli.stderr)
            return json.loads(cli.stdout)

    def test_generated_input_leaf_faults_through_real_read_cli(self):
        # Real stream receipts above, written/reloaded by every CLI invocation.
        # Compact native support still covers 57.6 s with >=3 bandwidths. Walk
        # every consumed leaf, including every row, rather than sampling paths.
        records = deepcopy(self.records)
        for record in records:
            h = record['harvest']
            for span in ('pre', 'post'):
                start = record['receipt']['idle_'+span+'_start_ns']
                for kind in probe.NATIVE_INPUTS:
                    mean = sum(r['power_w'] for r in h['idle'][span][kind])/len(h['idle'][span][kind])
                    h['idle'][span][kind] = [dict(
                        {'stamp_ns': start+i*9_600_000_000} if kind in ('meter','battery') else
                        {'start_ns':start+i*9_600_000_000,'end_ns':start+(i+1)*9_600_000_000},
                        power_w=mean) for i in range(6)]
            h['battery_samples'] = deepcopy(h['idle']['pre']['battery']+h['idle']['post']['battery'])
            h['meter_gaps'] = [{'span':'stream','missing_samples':1}]
        baseline = self.read_cli(records)
        specs = {'receipt': {**probe.RECEIPT_INPUTS, 'stack':probe.STACK_INPUTS},
                 'harvest': {'capture_stack':probe.CAPTURE_INPUTS,
                    'energy_j': {k:probe.NUMBER for k in probe.NATIVE_INPUTS},
                    'idle':{span:probe.NATIVE_INPUTS for span in ('pre','post')},
                    'battery_samples':probe.NATIVE_INPUTS['battery'],
                    'meter_gaps':[{'span':probe.TEXT,'missing_samples':probe.COUNT}],
                    'adapter_max_w':probe.POSITIVE,'adapter_source':probe.TEXT,'battery_source':probe.TEXT,
                    'tau_s':probe.NONNEG,'r_max_s':probe.NONNEG,'anchor_shift_j':probe.NONNEG,
                    'meter_edge_w':probe.EDGES,'battery_edge_j':probe.EDGES}}
        def walk(value, spec, path=()):
            if isinstance(spec, dict):
                for key, child in spec.items():
                    yield from walk(value[key], child, path+(key,))
            elif isinstance(spec, list):
                for i, row in enumerate(value):
                    yield from walk(row, spec[0], path+(i,))
            else:
                yield path, value, spec
                if spec == probe.EDGES:
                    for i, item in enumerate(value):
                        yield path+(i,), item, probe.NONNEG
        # All eight positions use the same accessor; exhaust the production
        # schema in one call, and separately test lost calls in every arm.
        count = 0
        for path, value, spec in walk(records[0], specs):
            modes = ['deleted','null','wrong_type','non_finite','wrong_length']
            for mode in modes:
                with self.subTest(path=path, mode=mode):
                    mutated = deepcopy(records)
                    parent = mutated[0]
                    for key in path[:-1]:
                        parent = parent[key]
                    key = path[-1]
                    if mode == 'deleted': del parent[key]
                    elif mode == 'null': parent[key] = None
                    elif mode == 'wrong_type': parent[key] = {} if not isinstance(value,dict) else 7
                    elif mode == 'non_finite': parent[key] = float('nan')
                    else: parent[key] = value[:1] if isinstance(value,list) else []
                    with tempfile.TemporaryDirectory() as tmp:
                        file = Path(tmp)/'read.json'
                        file.write_text(json.dumps({'records':mutated,'scan':self.scan}))
                        proc = subprocess.run([sys.executable,'-B',str(probe.ROOT/'scripts/bytes_stream_test.py'),
                                               'read',str(file)],capture_output=True,text=True)
                    self.assertEqual(proc.returncode,0,proc.stderr)
                    result = json.loads(proc.stdout)
                    self.assertEqual(len(result['calls']),8)
                    leaf = '.'.join(str(k) for k in path)
                    leaf_name = next(k for k in reversed(path) if isinstance(k,str))
                    self.assertTrue(any(leaf_name in reason for reason in result['reasons']),leaf)
                    undefined = [v for v in result['boundaries'].values() if v['class']=='UNDETERMINED']
                    self.assertTrue(undefined,leaf)
                    self.assertTrue(any(leaf_name in v['reason'] for v in undefined),leaf)
                    self.assertTrue(any('not defined (' in v['description'] for v in undefined))
                    # No still-defined propagated bound may shrink. Undefined
                    # widths are deliberately not replaced with numeric zero.
                    for beta, base in baseline['boundaries'].items():
                        width = result['boundaries'][beta].get('halfwidth')
                        if isinstance(width,(float,int)):
                            self.assertGreaterEqual(width,base['halfwidth'])
                    for call, original in zip(result['calls'],baseline['calls']):
                        gap = call.get('meter_gaps',{}).get('bound_j')
                        if isinstance(gap,(int,float)):
                            self.assertGreaterEqual(gap,original['meter_gaps']['bound_j'])
                        for beta, row in call['boundaries'].items():
                            for field in ('bound_j','edge_bound_j','baseline_bound_j'):
                                bound = row.get(field)
                                if isinstance(bound,(int,float)):
                                    self.assertGreaterEqual(bound,original['boundaries'][beta][field])
                    count += 1
        print('generated real read CLI leaf faults:',count)

    def test_null_containers_and_scan_inputs_keep_complete_records(self):
        paths = [('receipt',),('harvest',),('harvest','idle'),('harvest','idle','pre'),
                 ('harvest','energy_j'),('harvest','meter_gaps')]
        for path in paths:
            for value in (None, 7, 'wrong'):
                records = deepcopy(self.records)
                parent = records[0]
                for key in path[:-1]: parent = parent[key]
                parent[path[-1]] = value
                result = self.read_cli(records)
                self.assertEqual(len(result['calls']),8)
                self.assertTrue(any(str(path[-1]) in why for why in result['reasons']))
                self.assertTrue(any(v['class']=='UNDETERMINED' for v in result['boundaries'].values()))
        for key in ('K','B','Bc1','Bc3','Bc2'):
            scan = deepcopy(self.scan); scan[key] = 'invalid'
            result = self.read_cli(self.records, scan)
            self.assertTrue(all(v['class']=='UNDETERMINED' for v in result['boundaries'].values()))
        for path in ('repeats','start_ns','end_ns','bytes_per_read','clock_resolution_s',
                     'clock_tick_num_ns','clock_tick_den','clock','clock_tick_source'):
            for value in (None, {}, float('nan')):
                receipts = [{'bytes_per_read':size,'repeats':1,'start_ns':0,'end_ns':100+size,
                             **synthetic_clock()} for size in (16,32) for _ in range(3)]
                receipts[0][path] = value
                result = probe.knee_scan(receipts)
                self.assertEqual(result['status'],'knee not found')
                self.assertIn(path,result['reason'])
                json.dumps(result, allow_nan=False)

    def test_lost_calls_preserve_other_arm_reductions(self):
        for i in range(8):
            for lost in (None, {}):
                records = deepcopy(self.records)
                arm = self.result['calls'][i]['arm']
                if lost is None: records.pop(i)
                else: records[i] = lost
                result = self.read_cli(records)
                for beta in ('rails','gpu','dc','rest'):
                    arms = result['boundaries'][beta]['arms']
                    for name in self.payload:
                        if name != arm:
                            self.assertEqual(arms[name],self.result['boundaries'][beta]['arms'][name])

    def test_scan_reference_and_negative_place_upper_limit(self):
        for key in ('cache_reference','dram_reference'):
            ref = self.scan[key]
            self.assertEqual(ref,next(p for p in self.scan['pairs'] if p['size']==ref['size']))
        value = {'delta':5.,'halfwidth':150.,**probe.classify(5.,150.,1/64)}
        printed = probe.printed_record({'share':{'f':'x'},'stack_comparisons':[],
                                       'boundaries':{'rails':value}})
        self.assertIn('upper limit 160 J/GB',printed['claim_lines']['rails'])

    def test_missing_prerequisites_print_complete_results_through_cli(self):
        cases=[('adapter_source','',True,'gap power sources must be named'),
               ('battery_source',None,True,'gap power sources must be named'),
               ('adapter_max_w',None,True,'adapter rating missing'),
               ('r_max_s',None,False,'r_max missing'),
               ('meter_edge_w',None,False,'meter edge powers missing'),
               ('battery_edge_j',None,False,'battery edge energy missing'),
               ('anchor_shift_j',None,False,'anchor shift bound missing'),
               ('tau_s',None,False,'tau missing')]
        for field,value,gap,reason in cases:
            with self.subTest(field=field):
                records=deepcopy(self.records);h=records[0]['harvest']
                if value is None: del h[field]
                else: h[field]=value
                if gap: h['meter_gaps']=[{'span':'stream','missing_samples':1}]
                result=self.read_cli(records)
                self.assertEqual(len(result['calls']),8)
                self.assertEqual(result['input_records'],records)
                self.assertTrue(any(reason in r for r in result['reasons']))
                beta='rails' if field in ('anchor_shift_j','tau_s') else 'dc'
                self.assertEqual(result['boundaries'][beta]['class'],'UNDETERMINED')
                self.assertIn('not defined (',result['boundaries'][beta]['description'])
                if field=='anchor_shift_j':
                    self.assertEqual(result['boundaries']['dc']['class'],'RESOLVED')
                elif field!='tau_s':
                    self.assertIn('delta',result['boundaries']['rails'])
                    self.assertIn('delta',result['boundaries']['dc'])
        for beta in ('rails','gpu','meter','battery'):
            with self.subTest(integral=beta):
                records=deepcopy(self.records);del records[0]['harvest']['energy_j'][beta]
                result=self.read_cli(records)
                self.assertEqual(len(result['calls']),8)
                self.assertTrue(any('stream integral missing' in r or 'battery reading missing' in r for r in result['reasons']))
        for records in (self.records[:7],[],[{}]+self.records[1:]):
            result=self.read_cli(records)
            self.assertEqual(len(result['calls']),len(records))
            self.assertTrue(all(v['class']=='UNDETERMINED' for v in result['boundaries'].values()))

    def test_duplicate_stamps_are_disclosed_and_keep_native_variance(self):
        for stream,expected in (('meter',20_000_000),('battery',200_000_000)):
            records=deepcopy(self.records)
            rows=records[0]['harvest']['idle']['pre'][stream]
            rows[1]['stamp_ns']=rows[0]['stamp_ns']
            result=self.read_cli(records)
            stats=result['calls'][0]['native_idle']['pre'][stream]
            self.assertEqual(stats['duplicate_stamp_count'],1)
            self.assertEqual(stats['sample_count'],len(rows))
            self.assertEqual(stats['native_interval_ns'],expected)
            self.assertIn('variance_w2',stats)
            self.assertEqual(result['boundaries']['dc']['class'],'RESOLVED')

    def test_different_rail_set_has_boundary_specific_physical_effect(self):
        records=deepcopy(self.records)
        records[0]['harvest']['capture_stack']['measurement_boundary_label']['rails']=['cpu_power','gpu_power']
        result=self.read_cli(records)
        self.assertIn('measurement_boundary_label.rails',result['stack_comparisons'][0]['physical_differences'])
        for beta in ('rails','rest'):
            self.assertEqual(result['boundaries'][beta]['class'],'UNDETERMINED')
            self.assertIn('measured rails boundary differs',result['boundaries'][beta]['reason'])
            self.assertIn('delta',result['boundaries'][beta])
        self.assertEqual(result['boundaries']['dc']['class'],'RESOLVED')
        self.assertEqual(result['boundaries']['gpu']['class'],'RESOLVED')

    def test_gpu_source_must_exist_in_recorded_rail_sets(self):
        records = deepcopy(self.records)
        records[0]['harvest']['capture_stack']['measurement_boundary_label']['rails'] = ['cpu_power','ane_power']
        observed = self.read_cli(records)
        reference, versions = probe.registered_stack()
        reference['measurement_boundary_label']['rails'] = ['cpu_power','ane_power']
        with patch.object(probe,'registered_stack',return_value=(reference,versions)):
            expected = probe.read_known_bytes(self.records,self.scan)
        for result in (observed, expected):
            self.assertEqual(result['boundaries']['gpu']['class'], 'UNDETERMINED')
            self.assertIn('gpu_power', result['boundaries']['gpu']['reason'])
            self.assertEqual(result['boundaries']['dc']['class'], 'RESOLVED')

    def test_phi_is_recomputed_from_its_defining_sizes(self):
        scan=deepcopy(self.scan);del scan['phi']
        result=self.read_cli(self.records,scan)
        self.assertEqual(result['phi'],1/64)  # power-of-two fraction is bit exact
        self.assertEqual(result['printed']['contrasts']['dc'],'0.1929 ± 0.0025')

    def test_no_knee_descriptions_and_h2_upper_limit_rounding(self):
        result=self.read_cli(self.records,self.dram_scan)
        self.assertEqual(result['share'],{k:'not defined (knee not found)' for k in ('f','df')})
        self.assertEqual(result['gpu_power_contrast_w'],'not defined (knee not found)')
        self.assertEqual(result['phi'],'not defined (knee not found)')
        for beta in result['boundaries'].values():
            for key in ('delta','halfwidth','alpha','gamma_c','gamma_d','r','epsilon_flip','raw_stream_j_per_byte'):
                self.assertEqual(beta[key],'not defined (knee not found)')
        value={'delta':0.,'halfwidth':.000996,**probe.classify(0.,.000996,1/64)}
        printed=probe.printed_record({'share':{'f':'unknown'},'stack_comparisons':[], 'boundaries':{'rails':value}})
        self.assertEqual(printed['contrasts']['rails'],'0.0000 ± 0.0010')
        self.assertIn('upper limit 0.0010 J/GB',printed['claim_lines']['rails'])
        self.assertEqual(probe.format_interval(.1+.2,0),'0.30 ± 0.00')

    def test_nonsingular_descriptions_and_ordered_classes(self):
        self.assertEqual(probe.describe_share({'delta':0.,'halfwidth':.001},{'delta':.1,'halfwidth':.002}),
                         {'f':0.,'df':.01})
        self.assertEqual(probe.describe_share(None,{'delta':0.,'halfwidth':0.})['df'],
                         'not defined (DC contrast not valid)')
        for delta,width,expected in [(2.5e-5,1e-5,'RESOLVED'),(-.0100,.0020,'UNDETERMINED'),
                                     (1e-5,2e-5,'BELOW ATTRIBUTION LEVEL'),(0,.00057,'NOT RESOLVED')]:
            self.assertEqual(probe.classify(delta,width,1/64)['class'],expected)
        calls=[{'arm':a,'N':1,'boundaries':{'rails':{'excess_j':self.payload[a]*1e-9,'bound_j':.001}}}
               for a in ('S','C1','C3','C2','C2','C3','C1','S')]
        value=probe.reduce_boundary(calls,self.payload,'rails')
        self.assertEqual(value['epsilon_flip_over_alpha'],'not defined (alpha is zero)')



def dram_only(s):
    return 50e-6+s/331.6e9


def worked5(s):
    # marginal: 1000 GB/s up to 32 MiB; 32->64 MiB pair at 198.8 GB/s; 331.6 from 64 MiB up
    k = 64*2**20
    if s <= k//2:
        return 50e-6+s/1e12
    t32 = 50e-6+(k//2)/1e12
    t64 = t32+(k//2)/198.8e9
    return t64+(s-k)/331.6e9


def quantized_stamp(tick_index, rounding):
    value = tick_index*125
    return value//3 if rounding == 'floor' else (value+1)//3


def receipts(model, sigma, rng, rounding='floor'):
    out=[]
    for s in (2**k for k in range(14,36)):
        td=model(s)
        n=math.floor(2/td)
        for j in range(3):
            dur=n*td*(1+rng.gauss(0,sigma))
            # Random phase in one physical tick, at random integer tick epoch.
            # Integer arithmetic for the large epoch avoids floating cancellation.
            phase=rng.random()
            index=rng.randrange(24_000_000_000,48_000_000_000)
            end_index=index+math.floor(phase+dur*1e9/(125/3))
            start=quantized_stamp(index,rounding)
            end=quantized_stamp(end_index,rounding)
            out.append(dict(bytes_per_read=s,repeats=n,start_ns=start,end_ns=end,
                **{**synthetic_clock(), "clock_ns_conversion": rounding}))
    return out


def exact_reference(rec):
    times={}
    for s in sorted({c['bytes_per_read'] for c in rec}):
        calls=[c for c in rec if c['bytes_per_read']==s]
        ds=[F(c['end_ns']-c['start_ns'],10**9*c['repeats']) for c in calls]
        t=sum(ds)/len(ds)
        qs=[2*(max(F(str(c['clock_resolution_s']))*10**9, F(c['clock_tick_num_ns'],c['clock_tick_den']))+1)
            / (10**9*c['repeats']) for c in calls]
        times[s]=(t,max(abs(d-t) for d in ds)+sum(qs)/len(qs))
    pairs={}
    sizes=sorted(times)
    for lo,hi in zip(sizes,sizes[1:]):
        d=times[hi][0]-times[lo][0]
        dd=times[hi][1]+times[lo][1]
        if d>dd:
            pairs[hi]={'m_bytes_s':F(hi-lo)/d,'lower':F(hi-lo)/(d+dd),'upper':F(hi-lo)/(d-dd)}
    c=max(pairs,key=lambda s:pairs[s]['lower'])
    md,mc=pairs[sizes[-1]],pairs[c]
    h=lambda x,y:1/(F(63,64)/x+F(1,64)/y)
    th={key:h(md[key],mc[key]) for key in ('m_bytes_s','lower','upper')}
    target=pairs[2**25]
    target.update(margin=target['m_bytes_s']-th['m_bytes_s'],
                  bar=target['m_bytes_s']-target['lower']+th['upper']-th['m_bytes_s'])
    return th,target



def real_scan_cli(model):
    class ScanMX:
        uint8='uint8'
        def __init__(self, td): self.td,self.count=td,0
        def ones(self, shape, dtype): return object()
        def sum(self, data): return object()
        def eval(self, value): self.count+=1
        def synchronize(self): pass
        def clock(self): return 10**12+round(self.count*self.td*1e9)
    reference,versions=probe.registered_stack()
    stack={**reference,**versions}
    calls=[]
    with tempfile.TemporaryDirectory() as tmp:
        for size in (2**k for k in range(14,36)):
            for j in range(3):
                mx=ScanMX(model(size));n=math.floor(2/model(size))
                with patch.object(probe,'collect_stack',return_value=stack), \
                     patch.object(probe,'clock_metadata',return_value=synthetic_clock()):
                    rec=probe.stream(size,n,device='synthetic',idle_s=0,settle_s=0,
                                     mx=mx,clock_ns=mx.clock,sleep=lambda _:None)
                path=Path(tmp)/f'{size}-{j}.json'
                path.write_text(json.dumps(rec,allow_nan=False))
                calls.append(json.loads(path.read_text()))
        path=Path(tmp)/'scan.json';path.write_text(json.dumps(calls))
        cli=subprocess.run([sys.executable,'-B',str(probe.ROOT/'scripts/bytes_stream_test.py'),
                            'scan',str(path)],capture_output=True,text=True,check=True)
        return json.loads(cli.stdout)


class ExactKneeTests(unittest.TestCase):
    def test_rational_worked_comparison(self):
        rec=receipts(worked5,0,random.Random(8))
        result=probe.knee_scan(rec)
        th,pair=exact_reference(rec)
        actual=next(p for p in result['pairs'] if p['size']==2**25)
        differences=[float(abs(F(actual[key])-pair[key]))/1e9
                     for key in ('m_bytes_s','lower','upper','margin','bar')]
        differences += [float(abs(F(result[outkey])-th[key]))/1e9 for outkey,key in
                        [('threshold','m_bytes_s'),('threshold_lower','lower'),('threshold_upper','upper')]]
        # Consult verify.py: 1% of H2's smallest printed uncertainty,
        # 0.000045 GB/s, is 4.5e-7 GB/s. Against the exact rationals,
        # 1e6 * binary64 discrepancy must also fit below that same bar.
        agreement=4.5e-7
        self.assertLess(1e6*max(differences),agreement)
        for difference in differences:
            self.assertLess(difference,agreement)
        self.assertEqual(result['K'],2**26)  # discrete output identity

    def test_reduced_consult_noise_sweep(self):
        # Fixed assumptions, not fitted tolerances; retain outcomes without
        # asserting rates. 20 trials/cell keeps this regression in seconds.
        for rounding in ('floor','nearest'):
            for level,sigma in enumerate((0,.0005,.002,.005,.01)):
                for world,model in enumerate((worked5,dram_only)):
                    rng=random.Random(20261028+level*10+world)
                    for trial in range(20):
                        rec=receipts(model,sigma,rng,rounding)
                        result=probe.knee_scan(rec)
                        self.assertEqual(len(result['pairs']),21)
                        if sigma == 0:
                            self.assertEqual(result['K'],2**26 if world==0 else None)
                        if result['K'] is not None:
                            self.assertTrue(all(p['above'] for p in result['arm_checks']))
                            self.assertTrue(all(p['lower']>result['threshold_upper'] for p in
                                                result['pairs'] if p['above']))

    def test_real_stream_scan_receipts_reloaded_through_cli(self):
        for model,expected in ((worked5,2**26),(dram_only,None)):
            result=real_scan_cli(model)
            self.assertEqual(result['K'],expected)
            self.assertEqual(len(result['receipts']),66)

    def test_isolated_late_pair_is_retained_and_does_not_shrink_k(self):
        def late_model(s):
            if 2**26 < s <= 2**27:
                return worked5(2**26)+(s-2**26)/1e12
            return worked5(s)
        result=probe.knee_scan(receipts(late_model,0,random.Random(8)))
        self.assertTrue(next(p for p in result['pairs'] if p['size']==2**27)['above'])
        self.assertEqual(result['candidate_K'],2**28)
        self.assertIsNone(result['K'])
        self.assertEqual(result['reason'],'cache arm pairs not both resolved')
        self.assertEqual(len(result['pairs']),21)
        self.assertEqual([p['size'] for p in result['arm_checks']],[2**25,2**26])

    def test_missing_clock_retains_all_calls_and_reason(self):
        rec=receipts(worked5,0,random.Random(8))
        del rec[0]['clock_resolution_s']
        result=probe.knee_scan(rec)
        self.assertIsNone(result['K'])
        self.assertIn('clock resolution missing',result['reason'])
        self.assertEqual(result['receipts'],rec)

    def test_clock_receipt_and_measured_mac_timebase(self):
        self.assertEqual(probe.clock_duration_bound_ns(synthetic_clock()),86.)
        metadata=probe.clock_metadata()
        self.assertEqual(metadata['clock_resolution_s'],probe.time.clock_getres(probe.time.CLOCK_MONOTONIC_RAW))
        self.assertEqual(metadata['clock_ns_conversion'],'unknown')
        # Exercise the actual macOS collection path via a fake C ABI, rather
        # than substituting this seat's Linux clock for the Mac timebase.
        class Mach:
            def __call__(self, ptr):
                ptr._obj.numer,ptr._obj.denom=125,3
                return 0
        class Lib:
            mach_timebase_info=Mach()
        with patch.object(probe.sys,'platform','darwin'), patch('ctypes.CDLL',return_value=Lib()), \
             patch.object(probe.time,'clock_getres',return_value=4.2e-8):
            mac=probe.clock_metadata()
        self.assertEqual((mac['clock_tick_num_ns'],mac['clock_tick_den']),(125,3))
        self.assertEqual(mac['clock_duration_bound_ns'],86.)


if __name__ == "__main__":
    unittest.main()
