"""Synthetic §2 receipt checks. No Metal, telemetry or hardware timing evidence."""
from copy import deepcopy
import io
import json
import math
import statistics
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
                                 "stamp", "sleep", "stamp", "sleep", "stamp",
                                 "sum", "eval", "sum", "eval", "sum", "eval", "sync",
                                 "stamp", "sleep", "stamp", "sleep", "stamp"])
        self.assertEqual([event[1] for event in mx.events if event[0] == "sleep"], [57.6, 3, 3, 57.6])
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
                     "repeats": n} for size, rows in calls.items() for duration, n in rows]
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
        vm = nw(meter, 500, [57.6/len(meter)] * len(meter)).governed_variance_of_mean_w2
        vb = nw(battery, 50, [57.6/len(battery)] * len(battery)).governed_variance_of_mean_w2
        se = math.sqrt(vm/2) + math.sqrt(vb/2)
        self.assertGreater(se, 0)
        # The same native streams give exactly one output, independent of any
        # hold/linear policy, since neither policy is an input to this formula.
        self.assertEqual(se, math.sqrt(vm + vm)/2 + math.sqrt(vb + vb)/2)

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
            vals = {a: (v[1][beta], v[2][beta] + (gap_j/(2*v[0]) if a == 'C2' and beta != 'rails' else 0))
                    for a, v in rows.items()}
            (xs, ds), (x1, d1), (x3, _), (x2, d2) = (vals[a] for a in ('S','C1','C3','C2'))
            c1, c3, c2 = (payload[a] for a in ('C1','C3','C2'))
            gc = (x2-x1)/(c2-c1)
            alpha = x1-gc*c1
            residual = x3-alpha-gc*c3
            dgc = (d1+d2+abs(residual))/(c2-c1)
            da = d1+abs(residual)+dgc*c1
            delta = ((xs-alpha)/b-gc)*gb
            width = ((ds+da+abs(alpha))/b+dgc)*gb
            eps = width*(c2-c1)/gb/(1-c1/b)
            return delta, width, eps*1e6
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


if __name__ == "__main__":
    unittest.main()
