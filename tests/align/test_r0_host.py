from pathlib import Path
from types import SimpleNamespace
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise import prewindow
from joulewise.hazards import contention
from joulewise.align.r0 import PINS
from joulewise.align.r0_host import QuietGuard, Refused, disk_census, w1_disk_gate, host_snapshot, host_identity, inventory, smc_enumeration, swap_bytes
from joulewise.measurement_liveness import Census
from tests.align.test_r0_checks import config_at
from tests.align.test_r0_step import write_capture

# WP14(a) classifier fixture (docs/align/council-2026-11-05/WP14-RULINGS.md):
# a die key (t63 <= 5 s, tau <= 300 s) and a heatsink key (t63 > 5 s,
# 30 s < tau <= 300 s, dT >= 3 degC), with a non-stale idle series. The
# superseded fitted rule's taus (20 s / 400 s) are record-only under WP14(a).
WP14A_STEP = {"taus": {"TC0P": 2, "TH0P": 100}, "idle_jitter": 0.02}


class GuardClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


# Darwin pid,ppid,lstart,time,ucomm layout (including header and ucomm
# padding); ps itself is unavailable in the delegated sandbox.
PS_HEADER = "  PID  PPID STARTED                           TIME UCOMM\n"
OLD_START = "Fri Nov  6 17:00:00 2026"
NEW_START = "Fri Nov  6 18:05:15 2026"


def cpu_table(*rows):
    return PS_HEADER + f"    1     0 {OLD_START}   0:01.00 launchd         \n" + "".join(
        f"{pid:5d}     1 {start}   {cpu} {name:<16}\n" for pid, start, cpu, name in rows)


class R0HostTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.default_parent = Path(self.temp.name)
        env = patch.dict("os.environ", {"JOULEWISE_CUSTODY_PARENT": self.temp.name,
                                       "JOULEWISE_ADDITIONAL_CUSTODY_PARENTS": "[]"})
        env.start()
        self.addCleanup(env.stop)
        home = patch("joulewise.align.r0_host.Path.home", return_value=self.default_parent)
        home.start()
        self.addCleanup(home.stop)
    def runner(self, argv, **kwargs):
        if "launchctl" in argv[0]:
            return subprocess.CompletedProcess(argv, 113, "", "Could not find service")
        if "pgrep" in argv[0]:
            return subprocess.CompletedProcess(argv, 1, "", "")
        if argv == contention.PS_ARGV:
            return subprocess.CompletedProcess(argv, 0, cpu_table(), "")
        return subprocess.CompletedProcess(argv, 0, "1 0.0 /sbin/launchd\n", "")

    def test_armed_launchagent_refuses_even_without_running_process(self):
        agents = self.default_parent / "Library/LaunchAgents"
        agents.mkdir(parents=True)
        plist = agents / "com.joulewise.night.future.plist"
        plist.write_text("synthetic installed future window")
        guard = QuietGuard([], run=self.runner, inspect_custody=lambda **kw: Census())
        with self.assertRaises(Refused):
            guard.check(force=True)

    def test_loaded_agent_without_plist_and_unavailable_launchctl_refuse(self):
        for code, stderr in ((0, ""), (1, "permission denied")):
            def run(argv, **kwargs):
                if "launchctl" in argv[0]:
                    return subprocess.CompletedProcess(argv, code, "", stderr)
                return self.runner(argv, **kwargs)
            guard = QuietGuard([], run=run, inspect_custody=lambda **kw: Census())
            with self.assertRaises(Refused):
                guard.check(force=True)

    def test_guard_clear_reuses_shared_censuses_with_explicit_parents(self):
        calls = []
        def custody(**kwargs):
            calls.append(kwargs)
            return Census()
        explicit = self.default_parent / "explicit"
        explicit.mkdir()
        clock = GuardClock()
        guard = QuietGuard([str(explicit)], run=self.runner, inspect_custody=custody,
                           clock=clock, sleep=clock.sleep)
        guard.check(force=True)
        self.assertEqual(calls, [{"parents": [self.default_parent, explicit]}])
        self.assertEqual(len(guard.receipts), 1)

    def test_missing_configured_parent_refuses_and_records_resolved_parents(self):
        missing = self.default_parent / "typo"
        guard = QuietGuard([missing], run=self.runner, inspect_custody=lambda **kw: Census())
        with self.assertRaises(Refused):
            guard.check(force=True)
        self.assertIn(str(missing), guard.receipts[-1]["resolved_custody_parents"])

    def test_environment_parents_cannot_be_hidden_by_explicit_extras(self):
        extra = self.default_parent / "additional"
        extra.mkdir()
        calls = []
        def custody(**kwargs):
            calls.append(kwargs["parents"])
            return Census(refusals=["live chain in default parent"])
        with patch.dict("os.environ", {"JOULEWISE_ADDITIONAL_CUSTODY_PARENTS": json.dumps([str(extra)])}):
            guard = QuietGuard([], run=self.runner, inspect_custody=custody)
            with self.assertRaises(Refused):
                guard.check(force=True)
        self.assertEqual(calls, [[self.default_parent, extra]])

    def test_measurement_chain_refuses_and_refusal_is_latched(self):
        def running(argv, **kwargs):
            if argv != prewindow.PS_ARGV:
                return self.runner(argv)
            return subprocess.CompletedProcess(argv, 0, "1 0.0 /sbin/launchd\n99 0.0 python scripts/run_campaign.py --runs-root /tmp/fake\n", "")
        guard = QuietGuard([], run=running, inspect_custody=lambda **kw: Census())
        with self.assertRaises(Refused):
            guard.check(force=True)
        self.assertIn("run_campaign.py", guard.receipts[-1]["chains"][0])
        guard.run = self.runner
        with self.assertRaises(Refused):
            guard.check(force=True)

    def test_agent_hits_and_probe_errors_refuse(self):
        for code, stdout in ((0, "999999 codex\n"), (2, "")):
            def run(argv, **kwargs):
                if "pgrep" in argv[0]:
                    return subprocess.CompletedProcess(argv, code, stdout, "")
                return self.runner(argv)
            guard = QuietGuard([], run=run, inspect_custody=lambda **kw: Census())
            with self.assertRaises(Refused):
                guard.check(force=True)

    def test_custody_unknown_and_malformed_process_table_refuse(self):
        guard = QuietGuard([], run=self.runner, inspect_custody=lambda **kw: Census(refusals=["unknown owner"]))
        with self.assertRaises(Refused):
            guard.check(force=True)
        def malformed(argv, **kwargs):
            return self.runner(argv) if "pgrep" in argv[0] else subprocess.CompletedProcess(argv, 0, "bad row\n", "")
        guard = QuietGuard([], run=malformed, inspect_custody=lambda **kw: Census())
        with self.assertRaises(Refused):
            guard.check(force=True)

    def test_inventory_hashes_and_refuses_links_or_restricted_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a").write_bytes(b"abc")
            rows = inventory(root)
            self.assertEqual(rows[0]["bytes"], 3)
            self.assertEqual(rows[0]["sha256"], "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
            (root / "link").symlink_to(root / "a")
            with self.assertRaises(ValueError):
                inventory(root)
            (root / "link").unlink()
            (root / "restricted").mkdir()
            with self.assertRaises(ValueError):
                inventory(root)

    def snapshot(self, root):
        cache = root / "hub/models--synthetic--model"
        snapshot = cache / "snapshots" / ("a" * 40)
        snapshot.mkdir(parents=True)
        blobs = cache / "blobs"
        blobs.mkdir()
        return snapshot, blobs

    def test_inventory_hashes_resolved_hf_blob_under_snapshot_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            snapshot, blobs = self.snapshot(Path(tmp))
            blob = blobs / "hash"
            blob.write_bytes(b"abc")
            for target in (Path("../../blobs/hash"), blob):
                with self.subTest(target=target):
                    link = snapshot / "model.safetensors"
                    link.symlink_to(target)
                    rows = inventory(snapshot)
                    self.assertEqual(rows, [{"path": "model.safetensors", "bytes": 3,
                                            "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"}])
                    link.unlink()

    def test_inventory_refuses_hub_escape_before_opening_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            snapshot, blobs = self.snapshot(root)
            outside = root / "outside"
            outside.write_bytes(b"not a hub blob")
            for target in (outside, Path("../../../../outside")):
                with self.subTest(target=target):
                    link = snapshot / "model.safetensors"
                    link.symlink_to(target)
                    with patch.object(Path, "open", side_effect=AssertionError("must not open escaped bytes")):
                        with self.assertRaisesRegex(ValueError, "escapes hub root"):
                            inventory(snapshot)
                    link.unlink()
            # An apparently confined blob link must not hide another escape.
            (blobs / "indirect").symlink_to(outside)
            (snapshot / "model.safetensors").symlink_to("../../blobs/indirect")
            with self.assertRaisesRegex(ValueError, "escapes hub root"):
                inventory(snapshot)

    def test_inventory_refuses_nonblob_broken_loop_and_restricted_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            snapshot, blobs = self.snapshot(Path(tmp))
            (snapshot / "config.json").write_text("{}")
            (blobs / "loop").symlink_to("loop")
            # Synthetic restricted path only; no study data.
            for target in ("config.json", "../../blobs/missing", "../../blobs/loop", "../../restricted/blob"):
                with self.subTest(target=target):
                    link = snapshot / "model.safetensors"
                    link.symlink_to(target)
                    with self.assertRaises(ValueError):
                        inventory(snapshot)
                    link.unlink()
            (snapshot / "directory-link").symlink_to(blobs, target_is_directory=True)
            with self.assertRaises(ValueError):
                inventory(snapshot)

    def test_r0_disk_reports_66_gb_and_does_not_read_w1_offloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = config_at(root)
            for tag in ("D", "anchor"):
                folder = root / tag
                folder.mkdir()
                (folder / "model").write_text("tiny fake weight")
            config["offloads"] = [{"label": "pilot10", "inventory": str(root / "absent.json"),
                                   "destination": str(root / "not-offloaded")}]
            with patch("shutil.disk_usage", return_value=SimpleNamespace(free=66_000_000_000)):
                result = disk_census(config, PINS)
            self.assertEqual(result["status"], "diagnostic")
            self.assertEqual(result["free_bytes_after_present_weights"], 66_000_000_000)
            self.assertEqual(result["configured_w1_offload_labels"], ["pilot10"])
            self.assertEqual(result["offloads"], [])
            self.assertTrue(result["anchor"]["files"])
            self.assertEqual(result["design"]["W1_two_copies_bytes"], 37_400_000_000)
            self.assertEqual(result["smc_step_budget"]["capture_seconds"], 1800)

    def test_w1_requires_configured_verified_offloads_and_80_decimal_gb(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = config_at(root)
            for tag in ("D", "anchor"):
                folder = root / tag
                folder.mkdir()
                (folder / "model").write_text("tiny fake weight")
            for label in ("pilot8", "pilot10"):
                folder = root / label
                folder.mkdir()
                (folder / "file").write_text("synthetic offload")
                manifest = root / (label + ".json")
                manifest.write_text(json.dumps(inventory(folder)))
                config["offloads"].append({"label": label, "inventory": str(manifest), "destination": str(folder)})
            with patch("shutil.disk_usage", return_value=SimpleNamespace(free=80_000_000_000)):
                result = w1_disk_gate(config)
                self.assertEqual(result["status"], "pass")
                self.assertEqual(result["required_offload_labels"], ["pilot8", "pilot10"])
                self.assertEqual(result["required_free_bytes_after_r0"], 80_000_000_000)
            with patch("shutil.disk_usage", return_value=SimpleNamespace(free=79_999_999_999)):
                self.assertEqual(w1_disk_gate(config)["status"], "fail")
            with patch("shutil.disk_usage", return_value=SimpleNamespace(free=80_000_000_000)):
                (root / "pilot10" / "file").write_text("changed")
                self.assertEqual(w1_disk_gate(config)["status"], "fail")
                (root / "pilot10.json").write_text("not JSON")
                self.assertEqual(w1_disk_gate(config)["status"], "fail")
                (root / "pilot10.json").unlink()
                self.assertEqual(w1_disk_gate(config)["status"], "fail")

    def test_swap_parse_and_missing_value(self):
        self.assertEqual(swap_bytes(lambda argv: "total = 0.00M used = 1.50M free = 1M"), 1572864)
        with self.assertRaises(ValueError):
            swap_bytes(lambda argv: "unavailable")

    def test_host_identity_requires_pinned_model_and_128_gib_before_loading(self):
        for memory, model, status in ((24 * 1024**3, "MacSynthetic", "fail"),
                                     (128 * 1024**3, "WrongMac", "fail"),
                                     (128 * 1024**3, "MacSynthetic", "pass")):
            def run(argv):
                return str(memory) if "hw.memsize" in argv else model
            self.assertEqual(host_identity("MacSynthetic", run=run)["status"], status)

    def test_readiness_handles_current_and_legacy_power_mode_spellings(self):
        for setting, expected in (("powermode 0", "pass"), ("powermode 2", "pass"),
                                  ("lowpowermode 0", "pass"), ("powermode 1", "fail")):
            def run(argv):
                if "custom" in argv:
                    return "Battery Power:\n lowpowermode 1\nAC Power:\n " + setting + "\n"
                if "batt" in argv:
                    return "Now drawing from 'AC Power'"
                return "probe output"
            self.assertEqual(host_snapshot(run)["status"], expected)

    def test_smc_missing_and_present_hook(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(smc_enumeration(root, root / "output")["status"], "unavailable")
            (root / "scripts").mkdir()
            (root / "scripts/align_smc_enumerate.py").write_text("# fake hook")
            with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0, "enumerated", "")) as call:
                self.assertEqual(smc_enumeration(root, root / "output")["status"], "inconclusive")
                self.assertIn("--gpu-step", call.call_args.args[0])
                argv = call.call_args.args[0]
                self.assertEqual(argv[argv.index("--load-seconds") + 1], "900")
                self.assertEqual(argv[argv.index("--idle-seconds") + 1], "300")
                self.assertEqual(argv[argv.index("--recovery-seconds") + 1], "600")
                self.assertEqual(call.call_args.kwargs["timeout"], 2400)
                output = root / "output"
                output.mkdir()
                payload = write_capture(output, **WP14A_STEP)
                result = smc_enumeration(root, output)
                self.assertEqual(result["selection"], {"s_fast": "TC0P", "s_slow": "TH0P"})
                self.assertEqual(result["status"], "pass")
                self.assertIn("exponential_fit_diagnostic", result)
                self.assertEqual(result["smc_source_commit"], "58525031a")
                self.assertEqual(result["selection_status"], "PROVISIONAL")
                # WP14(a): the response is the classifier's; its picks carry the
                # provisional label, and the retired fit is a diagnostic only.
                self.assertTrue(result["response"]["picks_provisional"])
                self.assertEqual(result["exponential_fit_diagnostic"]["selection_status"], "PROVISIONAL")
                payload["coverage"]["per_key"]["TH0P"]["valid_samples"] = 0
                (output / "r0.json").write_text(json.dumps(payload))
                self.assertEqual(smc_enumeration(root, output)["status"], "inconclusive")

    def test_smc_configured_durations_and_timeout_reach_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts/align_smc_enumerate.py").write_text("# fake hook")
            output = root / "output"
            output.mkdir()
            profile = {"idle_seconds": 400, "load_seconds": 1200, "recovery_seconds": 700}
            write_capture(output, profile=profile, **WP14A_STEP)
            with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0, "", "")) as call:
                result = smc_enumeration(root, output, profile)
            self.assertEqual(result["status"], "pass")
            argv = call.call_args.args[0]
            for phase, duration in profile.items():
                self.assertEqual(argv[argv.index("--" + phase.replace("_", "-")) + 1], str(duration))
            self.assertEqual(call.call_args.kwargs["timeout"], 2900)

    def test_smc_journal_mismatch_never_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts/align_smc_enumerate.py").write_text("# fake hook")
            output = root / "output"
            output.mkdir()
            write_capture(output)
            with (output / "samples.jsonl").open("ab") as handle:
                handle.write(b"\n")
            with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0, "", "")):
                result = smc_enumeration(root, output)
            self.assertEqual(result["status"], "inconclusive")
            self.assertIn("SHA-256 mismatch", result["reason"])


class R0QuietIntervalTest(unittest.TestCase):
    setUp = R0HostTest.setUp
    runner = R0HostTest.runner

    def guard(self, snapshots, *, diagnostic="", clock=None):
        clock = clock or GuardClock()
        samples = iter(snapshots)
        calls = []
        def run(argv, **kwargs):
            if argv == contention.PS_ARGV:
                calls.append(clock())
                self.assertEqual(kwargs["env"]["LC_ALL"], "C")
                sample = next(samples)
                if isinstance(sample, Exception):
                    raise sample
                if isinstance(sample, tuple):
                    code, stdout = sample
                else:
                    code, stdout = 0, sample
                return subprocess.CompletedProcess(argv, code, stdout, "")
            if argv == prewindow.PS_ARGV:
                return subprocess.CompletedProcess(argv, 0, "1 0.0 /sbin/launchd\n" + diagnostic, "")
            return self.runner(argv, **kwargs)
        guard = QuietGuard([], run=run, inspect_custody=lambda **kw: Census(),
                           clock=clock, sleep=clock.sleep)
        return guard, clock, calls

    def assert_rate(self, actual, expected, elapsed):
        # One ps TIME quantum over the measured interval bounds the
        # counter's rate resolution; no acceptance margin is added.
        self.assertAlmostEqual(actual, expected,
                               delta=contention.PS_TIME_QUANTUM_S / elapsed)

    def test_real_respawn_bursts_are_diagnostic_only(self):
        # Replays mdworker_shared pid 18002 at 6% and photoanalysisd at 34%:
        # each was born 0.6 s before a subsequent call, using 0.6 CPU-s.
        # Wall time is fixed independently of the injected monotonic clock.
        from datetime import datetime
        wall_end = datetime(2026, 11, 6, 18, 5, 15).timestamp() + 0.6
        for pid, name, pcpu in ((18002, "mdworker_shared", "6.0"),
                                (18003, "photoanalysisd", "34.0")):
            with self.subTest(name=name):
                clock = GuardClock()
                guard, _, calls = self.guard(
                    [cpu_table(), cpu_table(), cpu_table((pid, NEW_START, "0:00.60", name))],
                    diagnostic=f"{pid} {pcpu} /usr/libexec/{name}\n", clock=clock)
                with patch("joulewise.align.r0_host.time.time_ns",
                           side_effect=lambda: int((wall_end - 60 + clock()) * 1e9)):
                    guard.check(force=True)
                    clock.now = 60
                    guard.check(force=True)
                self.assertEqual(len(calls), 3)
                self.assertFalse(guard.receipts[-1]["busy"])
                self.assertEqual(guard.receipts[-1]["pcpu_diagnostic"][0][0], pid)
                entry = guard.receipts[-1]["cpu_interval"]["contaminants"][0]
                self.assertEqual((entry["pid"], entry["lstart"], entry["name"]),
                                 (pid, " ".join(NEW_START.split()), name))
                self.assert_rate(entry["cpu_s_per_s"], 0.02, 30)
                # TIME's 0.01 s resolution also bounds the reported CPU-s.
                self.assertAlmostEqual(entry["cpu_s"], 0.6, delta=contention.PS_TIME_QUANTUM_S)

    def test_burst_before_first_call_is_not_charged_again_during_startup(self):
        from datetime import datetime
        wall_start = datetime(2026, 11, 6, 18, 5, 15).timestamp() + 0.6
        for pid, name, pcpu in ((18002, "mdworker_shared", "6.0"),
                                (18003, "photoanalysisd", "34.0")):
            with self.subTest(name=name):
                snapshot = cpu_table((pid, NEW_START, "0:00.60", name))
                guard, clock, _ = self.guard([snapshot, snapshot],
                                             diagnostic=f"{pid} {pcpu} {name}\n")
                with patch("joulewise.align.r0_host.time.time_ns",
                           side_effect=lambda: int((wall_start + clock()) * 1e9)):
                    guard.check(force=True)
                self.assertFalse(guard.receipts[-1]["busy"])
                self.assertFalse(guard.receipts[-1]["cpu_interval"]["contaminants"])

    def test_startup_waits_full_interval_and_sustained_cpu_straddles_bar(self):
        for cpu, rate, refuses in (("0:01.80", 0.06, True), ("0:01.20", 0.04, False)):
            with self.subTest(rate=rate):
                guard, clock, calls = self.guard([
                    cpu_table((42, OLD_START, "0:00.00", "mdworker_shared")),
                    cpu_table((42, OLD_START, cpu, "mdworker_shared"))])
                if refuses:
                    with self.assertRaisesRegex(Refused, "42 mdworker_shared 0.06 CPU-s/s"):
                        guard.check(force=True)
                    # Busy refusals latch even when subsequent CPU would be quiet.
                    with self.assertRaises(Refused):
                        guard.check(force=True)
                else:
                    guard.check(force=True)
                self.assertEqual(len(calls), 2)
                self.assertGreaterEqual(calls[1] - calls[0], prewindow.INTERVAL_S)
                self.assertEqual(len(clock.sleeps), 1)
                interval = guard.receipts[-1]["cpu_interval"]
                self.assertGreaterEqual(interval["elapsed_s"], prewindow.INTERVAL_S)
                self.assert_rate(interval["contaminants"][0]["cpu_s_per_s"], rate, interval["elapsed_s"])

    def test_burst_above_interval_budget_refuses(self):
        # 1.60 CPU-s exceeds 0.05 * 30 = 1.50 by ten TIME quanta.
        guard, _, _ = self.guard([cpu_table(), cpu_table((42, NEW_START, "0:01.60", "photoanalysisd"))])
        from datetime import datetime
        with patch("joulewise.align.r0_host.time.time_ns",
                   return_value=int(datetime(2026, 11, 6, 18, 5, 15).timestamp() * 1e9)):
            with self.assertRaisesRegex(Refused, "photoanalysisd.*CPU-s/s"):
                guard.check(force=True)

    def test_forced_calls_use_newest_30_second_opening_and_prune_history(self):
        def snapshot(cpu):
            return cpu_table((42, OLD_START, cpu, "mdworker_shared"))
        guard, clock, calls = self.guard([snapshot("0:00.00"), snapshot("0:00.00"),
                                         snapshot("0:01.00"), snapshot("0:01.00"),
                                         snapshot("0:01.00")])
        guard.check(force=True)
        clock.now = 30.1
        guard.check(force=True)  # 1 CPU-s / 30.1 s, rather than / 0.1 s.
        self.assertLess(guard.receipts[-1]["cpu_interval"]["start_monotonic_s"], 1)
        self.assertGreaterEqual(guard.receipts[-1]["cpu_interval"]["elapsed_s"], 30)
        clock.now = 45
        guard.check(force=True)
        clock.now = 60.2
        guard.check(force=True)
        opening = guard.receipts[-1]["cpu_interval"]["start_monotonic_s"]
        self.assertGreater(opening, 30)
        self.assertLess(opening, 31)
        self.assertEqual(len(guard._snapshots), 3)
        self.assertEqual(len(calls), 5)

    def test_reused_pid_counts_new_identity_from_zero(self):
        from datetime import datetime
        for cpu, refuses in (("0:00.60", False), ("0:01.80", True)):
            with self.subTest(cpu=cpu):
                guard, clock, _ = self.guard([
                    cpu_table((42, OLD_START, "1:00.00", "mdworker_shared")),
                    cpu_table((42, NEW_START, cpu, "mdworker_shared"))])
                with patch("joulewise.align.r0_host.time.time_ns", side_effect=lambda: int(
                        (datetime(2026, 11, 6, 18, 5, 0).timestamp() + clock()) * 1e9)):
                    if refuses:
                        with self.assertRaisesRegex(Refused, "mdworker_shared.*CPU-s/s"):
                            guard.check(force=True)
                    else:
                        guard.check(force=True)
                        self.assert_rate(guard.receipts[-1]["cpu_interval"]["contaminants"][0]["cpu_s_per_s"],
                                         0.02, 30)

    def test_counter_regression_refuses_even_between_short_forced_calls(self):
        def snapshot(cpu):
            return cpu_table((42, OLD_START, cpu, "mdworker_shared"))
        guard, clock, _ = self.guard([snapshot("0:01.00"), snapshot("0:02.00"), snapshot("0:01.90")])
        guard.check(force=True)
        clock.now = 30.1
        with self.assertRaisesRegex(Refused, "census indeterminate.*counter regressed"):
            guard.check(force=True)

    def test_failed_unparsable_and_regressed_initial_snapshots_refuse(self):
        for sample in ((1, ""), "", "PID PPID\ninvalid\n", RuntimeError("ps failed"),
                       cpu_table((42, OLD_START, "0:00.50", "mdworker_shared"))):
            with self.subTest(sample=sample):
                guard, _, _ = self.guard([
                    cpu_table((42, OLD_START, "0:01.00", "mdworker_shared")), sample])
                with self.assertRaises(Refused):
                    guard.check(force=True)

    def test_clock_regression_refuses_even_when_nonforced_call_would_skip(self):
        guard, clock, _ = self.guard([cpu_table(), cpu_table()])
        guard.check(force=True)
        clock.now = 29
        with self.assertRaisesRegex(Refused, "census indeterminate.*clock went backwards"):
            guard.check()

    def test_scope_includes_args_but_does_not_expand_to_other_consumers(self):
        for name, diagnostic, refuses in (("unrelated", "", False),
                                          ("python", "42 0.0 python mdworker_task.py\n", True)):
            with self.subTest(name=name):
                guard, _, _ = self.guard([
                    cpu_table((42, OLD_START, "0:00.00", name)),
                    cpu_table((42, OLD_START, "0:03.00", name))], diagnostic=diagnostic)
                if refuses:
                    with self.assertRaisesRegex(Refused, "python.*CPU-s/s"):
                        guard.check(force=True)
                else:
                    guard.check(force=True)
                    self.assertFalse(guard.receipts[-1]["busy"])

    def test_exited_below_limit_is_unaccounted_and_does_not_refuse(self):
        guard, clock, _ = self.guard([
            cpu_table((42, OLD_START, "0:00.00", "mdworker_shared")),
            cpu_table((42, OLD_START, "0:01.20", "mdworker_shared")), cpu_table()])
        guard.check(force=True)
        clock.now = 60
        guard.check(force=True)
        interval = guard.receipts[-1]["cpu_interval"]
        self.assertFalse(interval["exited_over_limit"])
        self.assertEqual(interval["unaccounted"][0]["reason"], "exited")

    def test_exited_over_limit_rule_uses_contention_previous_interval_evidence(self):
        # The public check latches before a second busy interval. Exercise
        # accounting directly to prove the retained exit rule independently.
        guard, clock, _ = self.guard([
            cpu_table((42, OLD_START, "0:00.00", "mdworker_shared")),
            cpu_table((42, OLD_START, "0:01.80", "mdworker_shared")), cpu_table()])
        with self.assertRaises(Refused):
            guard.check(force=True)
        clock.now = 60
        receipt = {}
        busy = guard._cpu_interval("1 0.0 launchd\n", receipt)
        self.assertEqual(busy[0]["pid"], 42)
        self.assertIn("previous interval", busy[0]["basis"])
        self.assert_rate(busy[0]["cpu_s_per_s"], 0.06, 30)

    def test_report_floor_filters_only_the_receipt(self):
        guard, _, _ = self.guard([
            cpu_table((42, OLD_START, "0:00.00", "mdworker_shared"),
                      (43, OLD_START, "0:00.00", "photoanalysisd")),
            cpu_table((42, OLD_START, "0:00.14", "mdworker_shared"),
                      (43, OLD_START, "0:00.16", "photoanalysisd"))])
        guard.check(force=True)
        entries = guard.receipts[-1]["cpu_interval"]["contaminants"]
        self.assertEqual([entry["pid"] for entry in entries], [43])


if __name__ == "__main__":
    unittest.main()
