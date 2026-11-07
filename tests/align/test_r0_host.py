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
from joulewise.align.r0_host import QuietGuard, Refused, disk_census, w1_disk_gate, host_snapshot, host_identity, inventory, smc_enumeration, swap_bytes, softwareupdate_scan_forecast
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

    def test_softwareupdate_forecast_is_advisory_and_missing_is_unknown(self):
        from datetime import datetime
        start = datetime(2026, 11, 7, 0, 0)
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "install.log"
            log.write_text("2026-11-06 23:09:00 AutoBackgroundScanFinished\n")
            result = softwareupdate_scan_forecast(start, datetime(2026, 11, 7, 12), log_path=log)
            self.assertEqual(result["predicted"], ["2026-11-07T05:09:00", "2026-11-07T11:09:00"])
            self.assertEqual(softwareupdate_scan_forecast(start, start, log_path=log.with_name("missing"))["status"],
                             "unknown")

    def test_softwareupdate_forecast_reads_install_log_lines_and_never_raises(self):
        from datetime import datetime
        start, deadline = datetime(2026, 11, 7, 6, 0), datetime(2026, 11, 7, 20, 0)
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "install.log"
            # The layout seen in this Mac's /var/log/install.log (with the
            # zone offset); the latest finished scan wins.
            log.write_text(
                "2026-11-06 22:45:25-08 host softwareupdated[1635]: softwareupdated: Posting "
                "com.apple.softwareupdate.AutoBackgroundScanFinished notification\n"
                "2026-11-07 04:45:00-08 host softwareupdated[1635]: softwareupdated: Posting "
                "com.apple.softwareupdate.AutoBackgroundScanFinished notification\n"
                "2026-11-07 05:00:00-08 host softwareupdated[1635]: unrelated line\n")
            result = softwareupdate_scan_forecast(start, deadline, log_path=log)
            self.assertEqual(result["status"], "forecast")
            self.assertEqual(result["last_finished"], "2026-11-07T04:45:00")
            self.assertEqual(result["predicted"], ["2026-11-07T10:45:00", "2026-11-07T16:45:00"])
            self.assertEqual(result["window"], ["2026-11-07T06:00:00", "2026-11-07T20:00:00"])
            for path, args in ((Path(tmp), (start, deadline)),            # unreadable: a directory
                               (log, (deadline, start)),                  # inverted window
                               (log, ("not a time", deadline))):
                self.assertEqual(softwareupdate_scan_forecast(*args, log_path=path)["status"], "unknown")
            log.write_text("no scan lines\n")
            self.assertEqual(softwareupdate_scan_forecast(start, deadline, log_path=log)["status"], "unknown")

    def test_softwareupdate_forecast_reads_only_a_bounded_tail(self):
        from datetime import datetime
        from joulewise.align import r0_host
        start, deadline = datetime(2026, 11, 7, 6, 0), datetime(2026, 11, 7, 20, 0)
        self.assertEqual(r0_host.INSTALL_LOG_TAIL_BYTES, 8 * 1024 * 1024)
        scan = ("2026-11-07 04:45:00-08 host softwareupdated[1635]: softwareupdated: Posting "
                "com.apple.softwareupdate.AutoBackgroundScanFinished notification\n")
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "install.log"
            log.write_text(scan + "x" * 99 + "\n")
            self.assertEqual(softwareupdate_scan_forecast(start, deadline, log_path=log,
                                                          tail_bytes=100)["status"], "unknown")
            # A tail that cuts into the scan line drops that partial line.
            self.assertEqual(softwareupdate_scan_forecast(start, deadline, log_path=log,
                                                          tail_bytes=140)["status"], "unknown")
            self.assertEqual(softwareupdate_scan_forecast(start, deadline, log_path=log,
                                                          tail_bytes=len(scan) + 100)["last_finished"],
                             "2026-11-07T04:45:00")


class R0QuietIntervalTest(unittest.TestCase):
    # CPU fixtures derive from the 0.05 CPU-s/s bar and 30 s interval:
    # 0.06 / 0.04 straddle the bar by 0.01; 1.80 / 1.20 are their
    # 30 s counters. 0.60 = 60 TIME quanta, hence 0.02 over 30 s.
    # Scenario times 45 / 60 are 1.5 / 2 intervals; short-call offsets
    # 0.1 / 0.2 are 10 / 20 TIME quanta. One CPU-s is 100 quanta.
    setUp = R0HostTest.setUp
    runner = R0HostTest.runner

    def guard(self, snapshots, *, diagnostic="", clock=None, driven=True, mid_baseline=None):
        """``snapshots`` are the admission's first and last tables, then the
        daemon's. The admission's mid-baseline table (at 15 s) repeats the
        first unless ``mid_baseline`` gives it."""
        clock = clock or GuardClock()
        snapshots = list(snapshots)
        if snapshots:
            snapshots.insert(1, snapshots[0] if mid_baseline is None else mid_baseline)
        samples = iter(snapshots)
        calls = []
        def run(argv, **kwargs):
            if argv == contention.PS_ARGV:
                calls.append(clock())
                self.assertEqual(kwargs["env"]["LC_ALL"], "C")
                self.assertEqual(kwargs["timeout"], contention.PROBE_TIMEOUT_S)
                sample = next(samples)
                if isinstance(sample, Exception):
                    raise sample
                if isinstance(sample, tuple):
                    code, stdout = sample
                else:
                    code, stdout = 0, sample
                return subprocess.CompletedProcess(argv, code, stdout, "")
            if argv == prewindow.PS_ARGV:
                args = diagnostic(clock()) if callable(diagnostic) else diagnostic
                return subprocess.CompletedProcess(argv, 0, "1 0.0 /sbin/launchd\n" + args, "")
            return self.runner(argv, **kwargs)
        class DrivenGuard(QuietGuard):
            """Drive the daemon's tick deterministically for legacy unit cases."""
            def check(self, **kwargs):
                if self._sampler is not None and not self.failure:
                    self._background_snapshot()
                return super().check(**kwargs)

            def _cpu_interval(self, receipt):
                # Direct accounting tests historically represented the next
                # daemon tick by calling this helper.
                if self._sampler is not None and receipt == {}:
                    self._background_snapshot()
                return super()._cpu_interval(receipt)
        guard_type = DrivenGuard if driven else QuietGuard
        guard = guard_type([], run=run, inspect_custody=lambda **kw: Census(),
                           clock=clock, sleep=clock.sleep)
        # The real daemon thread never fires during a test; ticks are driven.
        guard.SNAPSHOT_CADENCE_S = 3600
        self.addCleanup(guard.close)
        return guard, clock, calls

    def threaded(self, counter_at, *, until):
        """A guard whose real daemon thread runs at a 1 ms real cadence. Each
        daemon cycle advances the fake clocks by one SNAPSHOT_CADENCE_S (at
        its first probe, so a snapshot itself takes no fake time). The daemon
        blocks before passing ``until`` and sets ``reached``."""
        import threading
        from datetime import datetime
        wall0 = datetime(2026, 11, 6, 18, 0, 0).timestamp()
        clock = GuardClock()
        reached, release = threading.Event(), threading.Event()
        ps_threads = []
        def run(argv, **kwargs):
            daemon = threading.current_thread().name == "joulewise-quiet-snapshots"
            if daemon and "launchctl" in argv[0]:
                if clock.now + QuietGuard.SNAPSHOT_CADENCE_S > until:
                    reached.set()
                    release.wait(5)
                    raise RuntimeError("fixture released")
                clock.now += QuietGuard.SNAPSHOT_CADENCE_S
            if argv == contention.PS_ARGV:
                ps_threads.append(threading.current_thread().name)
                value = counter_at(clock.now)
                return subprocess.CompletedProcess(argv, 0, cpu_table(
                    (42, OLD_START, f"{int(value // 60)}:{value % 60:05.2f}", "mdworker_shared")), "")
            if argv == prewindow.PS_ARGV:
                return subprocess.CompletedProcess(argv, 0, "1 0.0 /sbin/launchd\n", "")
            return self.runner(argv, **kwargs)
        guard = QuietGuard([], run=run, inspect_custody=lambda **kw: Census(), clock=clock,
                           sleep=clock.sleep, wall_clock_ns=lambda: int((wall0 + clock()) * 1e9),
                           host_reader=None)
        guard.SNAPSHOT_CADENCE_S = 0.001
        guard.JOIN_TIMEOUT_S = 0.05  # a refusal's close() must not wait on the blocked fixture
        def stop():
            release.set()
            guard.close()
        self.addCleanup(stop)
        return guard, clock, reached, ps_threads

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
                self.assertEqual(len(calls), 4)  # 3 admission + 1 daemon
                self.assertFalse(guard.receipts[-1]["busy"])
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
        # 0.05 +/- 0.01 CPU-s/s over 30 s gives 1.80 / 1.20 CPU-s.
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
                self.assertEqual(len(calls), 3)  # 0 s, mid-baseline 15 s, 30 s
                self.assertGreaterEqual(calls[2] - calls[0], prewindow.INTERVAL_S)
                self.assertEqual(clock.sleeps, [prewindow.INTERVAL_S / 2] * 2)
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

    def test_each_snapshot_closes_a_window_from_the_newest_30_second_opening_and_prunes(self):
        def snapshot(cpu):
            return cpu_table((42, OLD_START, cpu, "mdworker_shared"))
        guard, clock, calls = self.guard([snapshot("0:00.00"), snapshot("0:00.00"),
                                         snapshot("0:01.00"), snapshot("0:01.00"),
                                         snapshot("0:01.00")])
        guard.check(force=True)
        clock.now = 30.1
        guard.check(force=True)  # 1 CPU-s / 30.1 s, rather than / 0.1 s.
        interval = guard.receipts[-1]["cpu_interval"]
        self.assertEqual((interval["start_monotonic_s"], interval["end_monotonic_s"]), (0, 30.1))
        self.assert_rate(interval["contaminants"][0]["cpu_s_per_s"], 1 / 30.1, 30.1)
        clock.now = 45
        guard.check(force=True)
        # The admission's mid-baseline snapshot opens the first daemon window.
        self.assertEqual(guard.receipts[-1]["cpu_interval"]["start_monotonic_s"], 15)
        clock.now = 60.2
        guard.check(force=True)
        # The newest opening at least 30 s before 60.2 is 30.1 (= 30 + 10
        # TIME quanta), not 30: the window slides one snapshot at a time.
        opening = guard.receipts[-1]["cpu_interval"]["start_monotonic_s"]
        self.assertEqual(opening, 30.1)
        # History before the newest opening is pruned; the guard keeps 3.
        self.assertEqual(len(guard._snapshots), 3)
        self.assertEqual(len(calls), 6)  # 3 admission + 3 daemon

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

    def test_contaminant_regression_between_short_forced_calls_is_recorded(self):
        # 100 TIME quanta / 30 s is below 0.05. A later drop of ten
        # quanta, seen ten quanta of wall time later, adds no refusal.
        def snapshot(cpu):
            return cpu_table((42, OLD_START, cpu, "mdworker_shared"))
        guard, clock, _ = self.guard([snapshot("0:01.00"), snapshot("0:02.00"), snapshot("0:01.90")])
        guard.check(force=True)
        clock.now = 30.1
        guard.check(force=True)
        self.assertFalse(guard.receipts[-1]["busy"])
        recorded = guard.receipts[-1]["cpu_interval"]["regressed_counters"]
        self.assertEqual([(row["pid"], row["contaminant"]) for row in recorded], [(42, True)])

    def test_failed_and_unparsable_initial_snapshots_refuse(self):
        for sample in ((1, ""), "", "PID PPID\ninvalid\n", RuntimeError("ps failed")):
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

    def test_report_floor_filters_only_the_receipt(self):
        # 0.005 * 30 = 0.15 CPU-s; 0.14 / 0.16 are one TIME quantum
        # below / above that receipt floor, not extra acceptance margins.
        guard, _, _ = self.guard([
            cpu_table((42, OLD_START, "0:00.00", "mdworker_shared"),
                      (43, OLD_START, "0:00.00", "photoanalysisd")),
            cpu_table((42, OLD_START, "0:00.14", "mdworker_shared"),
                      (43, OLD_START, "0:00.16", "photoanalysisd"))])
        guard.check(force=True)
        entries = guard.receipts[-1]["cpu_interval"]["contaminants"]
        self.assertEqual([entry["pid"] for entry in entries], [43])

    def test_noncontaminant_zombie_is_recorded_and_other_rows_are_judged(self):
        # Zombie TIME 5.00 -> 0.00 is 500 TIME quanta -> zero. The other
        # row uses (0.05 +/- 0.01) * 30 = 1.80 / 1.20 CPU-s.
        for cpu, refuses in (("0:01.20", False), ("0:01.80", True)):
            with self.subTest(cpu=cpu):
                guard, _, _ = self.guard([
                    cpu_table((42, OLD_START, "0:05.00", "Safari"),
                              (43, OLD_START, "0:00.00", "mdworker_shared")),
                    cpu_table((42, OLD_START, "0:00.00", "Safari"),
                              (43, OLD_START, cpu, "mdworker_shared"))])
                if refuses:
                    with self.assertRaisesRegex(Refused, "43 mdworker_shared.*CPU-s/s"):
                        guard.check(force=True)
                else:
                    guard.check(force=True)
                recorded = guard.receipts[-1]["cpu_interval"]["regressed_noncontaminant"]
                self.assertEqual([row["pid"] for row in recorded], [42])

    def test_noncontaminant_regression_between_short_calls_is_recorded(self):
        # Initial delta 1.00 = 100 TIME quanta is below 0.05 * 30.
        # The 0.01 s regression is seen 0.1 s (10 TIME quanta) later;
        # the retained opening still has a positive interval delta.
        guard, clock, _ = self.guard([
            cpu_table((42, OLD_START, "0:05.00", "Safari")),
            cpu_table((42, OLD_START, "0:06.00", "Safari")),
            cpu_table((42, OLD_START, "0:05.99", "Safari"))])
        guard.check(force=True)
        clock.now += 10 * contention.PS_TIME_QUANTUM_S
        guard.check(force=True)
        self.assertEqual(guard.receipts[-1]["cpu_interval"]["regressed_noncontaminant"][0]["pid"], 42)

    def test_zombie_regressions_are_recorded_for_both_contaminant_match_sources(self):
        # 300 TIME quanta = 3.00 CPU-s -> zero, with no prior interval
        # over 0.05. Exercise ucomm, args-only, and non-contaminant rows.
        for name, args, contaminant in (("mdworker_shared", "", True),
                                        ("python", "42 0.0 python mdworker_task.py\n", True),
                                        ("Safari", "", False)):
            with self.subTest(name=name):
                guard, _, _ = self.guard([
                    cpu_table((42, OLD_START, "0:03.00", name)),
                    cpu_table((42, OLD_START, "0:00.00", name))], diagnostic=args)
                guard.check(force=True)
                interval = guard.receipts[-1]["cpu_interval"]
                self.assertFalse(guard.receipts[-1]["busy"])
                self.assertEqual([(row["pid"], row["contaminant"]) for row in interval["regressed_counters"]],
                                 [(42, contaminant)])

    def test_interval_regression_after_missing_snapshot_is_recorded_for_every_identity(self):
        # Opening at 30 s, missing at 1.5 * 30, reappearing at 2 * 30:
        # the consecutive comparison cannot see the 500-quanta -> zero
        # regression, but the selected 30 s interval must still handle it.
        for name, contaminant in (("Safari", False), ("mdworker_shared", True)):
            with self.subTest(name=name):
                sample = cpu_table((42, OLD_START, "0:05.00", name))
                guard, clock, _ = self.guard([
                    sample, sample, cpu_table(), cpu_table((42, OLD_START, "0:00.00", name))])
                guard.check(force=True)
                clock.now = 1.5 * prewindow.INTERVAL_S
                guard.check(force=True)
                clock.now = 2 * prewindow.INTERVAL_S
                guard.check(force=True)
                recorded = guard.receipts[-1]["cpu_interval"]["regressed_counters"]
                self.assertEqual([(row["pid"], row["contaminant"]) for row in recorded], [(42, contaminant)])

    # Daemon-sampler tests. Background ticks are driven by calling the
    # daemon's own cycle (_background_snapshot) at fake times, except where
    # a real thread is the point. CADENCE = the guard's one constant.

    def tick(self, guard, clock, *times):
        for t in times:
            clock.now = t
            guard._background_snapshot()

    def test_300_second_caller_gap_daemon_thread_refuses_60_second_contender(self):
        # Measured failure (cold review should-fix 1): 0.2 CPU-s/s for 60 s
        # inside a 300 s caller gap (model load / prefill) passed with a
        # long_interval flag. The real daemon thread snapshots through the
        # gap; the first post-gap check judges 30 s windows and refuses.
        def counter(t):
            return min(max(t - 120, 0), 60) * 0.2
        guard, clock, reached, ps_threads = self.threaded(counter, until=330)
        guard.check(force=True)
        self.assertTrue(reached.wait(2), "daemon did not reach the end of the caller gap")
        self.assertEqual(clock.now, 330)
        with self.assertRaisesRegex(Refused, "42 mdworker_shared 0.1 CPU-s/s"):
            guard.check(force=True)
        windows = guard.receipts[-1]["cpu_intervals"]
        self.assertLessEqual(max(w["elapsed_s"] for w in windows),
                             prewindow.INTERVAL_S + QuietGuard.SNAPSHOT_CADENCE_S)
        # Admission's two snapshots ran on the caller; every later ps ran on
        # the daemon, and the caller never slept again.
        self.assertEqual(set(ps_threads[3:]), {"joulewise-quiet-snapshots"})
        self.assertEqual(clock.sleeps, [prewindow.INTERVAL_S / 2] * 2)

    def test_calls_29_seconds_apart_with_a_2_cpu_second_burst_refuse(self):
        # Measured failure (cold review should-fix 2): forced calls 29 s
        # apart made a 58 s window and a 2.0 CPU-s burst passed (2/58 <
        # 0.05). The burst (85-95 s) straddles the 90 s snapshot, so
        # back-to-back 30 s windows from 30 s would also split it (1.0 +
        # 1.0); the sliding 75-105 s window holds all of it: 2/30 > 0.05.
        def snapshot(cpu):
            return cpu_table((42, OLD_START, cpu, "mdworker_shared"))
        guard, clock, calls = self.guard([snapshot("0:00.00")] * 5 + [
            snapshot("0:01.00"), snapshot("0:02.00")], driven=False)
        guard.check(force=True)
        self.tick(guard, clock, 45)
        clock.now = 59
        guard.check(force=True)
        self.tick(guard, clock, 60, 75)
        clock.now = 88
        guard.check(force=True)
        self.tick(guard, clock, 90, 105)
        clock.now = 117
        with self.assertRaisesRegex(Refused, "42 mdworker_shared 0.0666667 CPU-s/s"):
            guard.check(force=True)
        windows = [w for receipt in guard.receipts for w in receipt.get("cpu_intervals", ())]
        self.assertEqual((windows[-1]["start_monotonic_s"], windows[-1]["end_monotonic_s"]), (75, 105))
        self.assertLessEqual(max(w["elapsed_s"] for w in windows),
                             prewindow.INTERVAL_S + QuietGuard.SNAPSHOT_CADENCE_S)
        # Windows are contiguous: each opening is at or before the last end.
        for previous, current in zip(windows, windows[1:]):
            self.assertLessEqual(current["start_monotonic_s"], previous["end_monotonic_s"])
        self.assertEqual(len(calls), 8)  # 3 admission + 5 daemon; checks ran none

    def test_repeated_short_startup_bursts_do_not_refuse(self):
        # Proportionality: mdworker_shared / photoanalysisd respawns, each
        # ~0.6 CPU-s (60 TIME quanta, 0.02 CPU-s/s over 30 s), a new pair
        # born in every 15 s cadence slot for ten minutes and gone at the
        # next snapshot. Per-process judgement keeps them below 0.05.
        from datetime import datetime
        wall0 = datetime(2026, 11, 6, 18, 0, 0).timestamp()
        def lstart(t):
            d = datetime.fromtimestamp(wall0 + t)
            return d.strftime("%a %b ") + f"{d.day:2d}" + d.strftime(" %H:%M:%S %Y")
        times = [0, 30] + list(range(45, 631, 15))
        tables = [cpu_table()] * 2 + [
            cpu_table((20000 + 2 * t, lstart(t - 5), "0:00.60", "mdworker_shared"),
                      (20001 + 2 * t, lstart(t - 3), "0:00.60", "photoanalysisd"))
            for t in times[2:]]
        guard, clock, _ = self.guard(tables, driven=False)
        guard.wall_clock_ns = lambda: int((wall0 + clock()) * 1e9)
        guard.check(force=True)
        for t in times[2:]:
            self.tick(guard, clock, t)
            guard.check()
        windows = [w for receipt in guard.receipts for w in receipt.get("cpu_intervals", ())]
        self.assertEqual(len(windows), len(times) - 1)
        rates = [c["cpu_s_per_s"] for w in windows for c in w["contaminants"]]
        # 0.6 CPU-s over a 30 s window (0.02), or over the first 45 s one.
        self.assert_rate(max(rates), 0.02, prewindow.INTERVAL_S)
        self.assertIsNone(guard.failure)

    def test_no_sleep_or_process_on_caller_after_first_admission(self):
        guard, clock, calls = self.guard([cpu_table()] * 4, driven=False)
        guard.check(force=True)
        guard.sleep = lambda seconds: self.fail("caller slept after admission")
        self.tick(guard, clock, 45)
        run = guard.run
        guard.run = lambda *a, **k: self.fail("caller launched a process after admission")
        # Per-token checks, forced boundaries and windows judged on stored data.
        for step in range(1, 200):
            clock.now = 45 + step * 0.05
            guard.check(force=step % 50 == 0)
        guard.run = run
        self.tick(guard, clock, 60)
        guard.run = lambda *a, **k: self.fail("caller launched a process after admission")
        clock.now = 61
        guard.check(force=True)
        self.assertEqual(guard.receipts[-1]["cpu_interval"]["end_monotonic_s"], 60)
        self.assertEqual(guard.receipts[-1]["background_snapshots_monotonic_s"], [60])
        self.assertEqual(len(calls), 5)  # 3 admission + 2 daemon

    def test_background_snapshot_failure_refuses_next_check_and_stops(self):
        guard, clock, _ = self.guard([cpu_table(), cpu_table(), RuntimeError("ps failed")], driven=False)
        guard.check(force=True)
        self.tick(guard, clock, 45)
        self.assertTrue(guard._stop_sampler.is_set())
        clock.now = 45.1  # inside the 15 s throttle: still refuses
        with self.assertRaisesRegex(Refused, "background sampler.*cumulative CPU snapshot: ps failed"):
            guard.check()
        guard._sampler.join(1)
        self.assertFalse(guard._sampler.is_alive())

    def test_background_census_refusal_fails_closed(self):
        # The census moved off the caller with the snapshots: a window armed
        # after admission refuses at the next check, as it did per check.
        guard, clock, _ = self.guard([cpu_table()] * 3, driven=False)
        guard.check(force=True)
        agents = self.default_parent / "Library/LaunchAgents"
        agents.mkdir(parents=True)
        (agents / "com.joulewise.night.future.plist").write_text("synthetic")
        self.tick(guard, clock, 45)
        with self.assertRaisesRegex(Refused, "background sampler.*measurement window armed"):
            guard.check()

    def test_stalled_sampler_refuses(self):
        guard, clock, _ = self.guard([cpu_table()] * 2, driven=False)
        guard.check(force=True)
        # The stall bound is the window bound: 30 + 15 + 5 = 50 s.
        clock.now = 30 + 49
        guard.check(force=True)  # no new snapshot yet, within bound
        clock.now = 30 + 51
        guard.check()  # per-token calls stay throttled to one judgement per 15 s
        with self.assertRaisesRegex(Refused, "background snapshots stalled \\(51.0 s since the last\\)"):
            guard.check(force=True)

    def test_window_longer_than_interval_plus_cadence_and_margin_refuses(self):
        # Cold MEDIUM-2: snapshots 0, 30, 45, 60, 119 (and the 15 s
        # mid-baseline). A daemon slip leaves the 60-119 s window, 59 s, and
        # a 2.0 CPU-s burst inside it reads 0.034: judged, it would pass.
        # Beyond 30 + 15 + 5 = 50 s it is indeterminate instead.
        self.assertEqual(QuietGuard.MAX_WINDOW_S, 50)
        def snapshot(cpu):
            return cpu_table((42, OLD_START, cpu, "mdworker_shared"))
        guard, clock, _ = self.guard([snapshot("0:00.00")] * 4 + [snapshot("0:02.00")], driven=False)
        guard.check(force=True)
        self.tick(guard, clock, 45, 60)
        clock.now = 61
        guard.check(force=True)
        self.tick(guard, clock, 119)
        with self.assertRaisesRegex(Refused, "judged CPU window of 59.0 s exceeds 50 s"):
            guard.check(force=True)
        self.assertTrue(guard.receipts[-1]["cpu_intervals"][-1]["long_interval"])

    def test_burst_straddling_the_admission_end_is_judged_in_a_30_second_window(self):
        # Cold MEDIUM-1: 2.0 CPU-s from 20 to 35 s straddles the admission's
        # 30 s snapshot. Without the mid-baseline snapshot the first daemon
        # window is 0-45 s (0.044) and [0, 30] / [30, 60] split it; with it
        # the 15-45 s window holds all of it: 2.0 / 30 > 0.05.
        def counter(t):
            return 2.0 * min(max(t - 20, 0), 15) / 15
        guard, clock, reached, _ = self.threaded(counter, until=45)
        guard.check(force=True)
        self.assertTrue(reached.wait(2))
        with self.assertRaisesRegex(Refused, "42 mdworker_shared 0.0666667 CPU-s/s"):
            guard.check(force=True)
        window = guard.receipts[-1]["cpu_intervals"][-1]
        self.assertEqual((window["start_monotonic_s"], window["end_monotonic_s"]), (15, 45))

    def test_background_census_summary_is_receipted_per_cycle(self):
        # Cold MEDIUM-3: what each daemon census saw reaches the next receipt.
        guard, clock, _ = self.guard([cpu_table()] * 4, driven=False,
                                     diagnostic="77 9.0 /System/Library/mdworker_shared\n")
        guard.check(force=True)
        self.tick(guard, clock, 45, 60)
        clock.now = 61
        guard.check(force=True)
        summaries = guard.receipts[-1]["background_census"]
        self.assertEqual([row["monotonic_s"] for row in summaries], [45, 60])
        self.assertEqual(summaries[0], {
            "monotonic_s": 45, "resolved_custody_parents": [str(self.default_parent.resolve())],
            "installed_night_agents": [], "launchctl_exit_code": 113, "agent_exit_code": 1,
            "agent_hits": 0, "custody_clear": True, "custody_warnings": [], "chains": [],
            "pcpu_diagnostic": [(77, 9.0, "/System/Library/mdworker_shared")]})
        self.assertEqual(guard.receipts[-1]["background_snapshots_monotonic_s"], [45, 60])

    def test_refusal_stops_the_daemon_thread(self):
        guard, clock, _ = self.guard([cpu_table(), cpu_table(),
                                      cpu_table((42, OLD_START, "0:01.80", "mdworker_shared"))],
                                     driven=False)
        guard.check(force=True)
        self.assertTrue(guard._sampler.is_alive())
        self.tick(guard, clock, 60)
        with self.assertRaises(Refused):
            guard.check(force=True)
        self.assertTrue(guard._stop_sampler.is_set())
        guard._sampler.join(1)
        self.assertFalse(guard._sampler.is_alive())

    def test_real_daemon_thread_join_is_bounded(self):
        import time as real_time
        guard, clock, reached, _ = self.threaded(lambda t: 0, until=45)
        guard.JOIN_TIMEOUT_S = 0.05
        guard.check(force=True)
        self.assertTrue(reached.wait(2))  # daemon now blocked inside a probe
        started = real_time.monotonic()
        with guard:
            pass  # context exit closes
        self.assertLess(real_time.monotonic() - started, 1.0)
        self.assertTrue(guard._stop_sampler.is_set())
        self.assertTrue(guard._sampler.is_alive())  # still blocked; join gave up

    def test_both_cpu_snapshot_tables_use_the_module_probe_timeout(self):
        guard, _, _ = self.guard([cpu_table(), cpu_table()])
        run = guard.run
        calls = []
        def recorded(argv, **kwargs):
            calls.append((argv, kwargs))
            return run(argv, **kwargs)
        guard.run = recorded
        guard.check(force=True)
        for i, (argv, kwargs) in enumerate(calls):
            if argv == contention.PS_ARGV:
                self.assertEqual(kwargs["timeout"], contention.PROBE_TIMEOUT_S)
                self.assertEqual(calls[i + 1][0], prewindow.PS_ARGV)
                self.assertEqual(calls[i + 1][1]["timeout"], contention.PROBE_TIMEOUT_S)

    def test_args_ps_time_does_not_stretch_cpu_denominator(self):
        clock = GuardClock()
        samples = iter([cpu_table((42, OLD_START, "0:00.00", "mdworker_shared")),
                        cpu_table((42, OLD_START, "0:00.90", "mdworker_shared")),
                        cpu_table((42, OLD_START, "0:01.80", "mdworker_shared"))])
        args_calls = 0
        def run(argv, **kwargs):
            nonlocal args_calls
            if argv == contention.PS_ARGV:
                return subprocess.CompletedProcess(argv, 0, next(samples), "")
            if argv == prewindow.PS_ARGV:
                args_calls += 1
                if args_calls == 4:  # census, then the 0 / 15 / 30 s snapshots
                    clock.now += 5
                return subprocess.CompletedProcess(argv, 0, "1 0.0 /sbin/launchd\n", "")
            return self.runner(argv, **kwargs)
        guard = QuietGuard([], run=run, inspect_custody=lambda **kw: Census(), clock=clock,
                           sleep=clock.sleep, host_reader=None)
        with self.assertRaisesRegex(Refused, "0.06 CPU-s/s"):
            guard.check(force=True)
        self.assertEqual(guard.receipts[-1]["cpu_interval"]["elapsed_s"], 30)

    def test_host_aggregate_is_flagged_but_never_judged(self):
        hosts = iter([[[0, 0, 0, 0]], [[150, 0, 1350, 0]], [[300, 0, 2700, 0]]])
        guard, _, _ = self.guard([cpu_table(), cpu_table()])
        guard.host_reader = lambda: next(hosts)
        guard.check(force=True)
        interval = guard.receipts[-1]["cpu_interval"]
        self.assertAlmostEqual(interval["outside_aggregate_cpu_s_per_s"], .1)
        self.assertTrue(interval["aggregate_above_0_05"])
        self.assertFalse(guard.receipts[-1]["busy"])

    def test_args_only_contaminant_born_during_startup_is_judged(self):
        from datetime import datetime
        # Born 30 / 3 = 10 s into startup, burns 2 * 0.05 for the
        # remaining 20 s: 2 CPU-s / 30 > 0.05 on the first admission.
        wall = datetime(2026, 11, 6, 18, 5, 0).timestamp()
        birth = "Fri Nov  6 18:05:10 2026"
        guard, clock, _ = self.guard([
            cpu_table(), cpu_table((42, birth, "0:02.00", "python"))],
            diagnostic=lambda now: "42 0.0 python mdworker_task.py\n" if now else "")
        with patch("joulewise.align.r0_host.time.time_ns",
                   side_effect=lambda: int((wall + clock()) * 1e9)):
            with self.assertRaisesRegex(Refused, "python.*CPU-s/s"):
                guard.check(force=True)
        self.assertEqual(guard.receipts[-1]["cpu_interval"]["contaminants"][0]["matched_on"], ["args"])

    def test_backwards_wall_step_is_flagged_without_changing_monotonic_rate(self):
        # A backwards step of one TIME quantum; the monotonic interval
        # remains 30 s and 1.20 CPU-s / 30 = 0.05 - 0.01 is clean.
        guard, _, _ = self.guard([
            cpu_table((42, OLD_START, "0:00.00", "mdworker_shared")),
            cpu_table((42, OLD_START, "0:01.20", "mdworker_shared"))])
        # An arbitrary wall origin four 30 s intervals after epoch keeps the
        # one-quantum backwards step positive; it is not a judgment threshold.
        wall = 4 * prewindow.INTERVAL_S * 1_000_000_000
        backwards = wall - int(contention.PS_TIME_QUANTUM_S * 1e9)
        with patch("joulewise.align.r0_host.time.time_ns", side_effect=[wall] * 4 + [backwards] * 2):
            guard.check(force=True)
        self.assertTrue(guard.receipts[-1]["wall_clock_backwards"])
        entry = guard.receipts[-1]["cpu_interval"]["contaminants"][0]
        self.assertEqual(entry["matched_on"], ["ucomm"])
        self.assert_rate(entry["cpu_s_per_s"], 0.04, prewindow.INTERVAL_S)

    def test_large_backwards_wall_step_charges_new_process_from_zero(self):
        guard, _, _ = self.guard([
            cpu_table(), cpu_table((42, OLD_START, "0:01.80", "mdworker_shared"))])
        wall = 2_000_000_000_000_000_000
        with patch("joulewise.align.r0_host.time.time_ns",
                   side_effect=[wall] * 4 + [wall - 2_000_000_000] * 2):
            with self.assertRaisesRegex(Refused, "mdworker_shared 0.06 CPU-s/s"):
                guard.check(force=True)
        self.assertNotIn("missed by the first snapshot",
                         [row["reason"] for row in guard.receipts[-1]["cpu_interval"]["unaccounted"]])


if __name__ == "__main__":
    unittest.main()
