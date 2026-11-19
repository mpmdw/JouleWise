from pathlib import Path
from types import SimpleNamespace
import json
import hashlib
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
from tests.align.test_smc_classifier_v4 import jittered_capture

# D4/D5 fixture: fast tau 2 <=60 s; slow tau 100 >60 s, with
# 100*ln(10) <300 s band hold and residual noise below 0.15 degC.
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
                           clock=clock, sleep=clock.sleep, host_reader=None)
        self.addCleanup(guard.close)
        guard.check(force=True)
        self.assertEqual(calls, [{"parents": [self.default_parent, explicit], "strict": True}] * 2)
        self.assertEqual(len(guard.receipts), 1)

    def test_missing_configured_parent_refuses_with_path_and_errno(self):
        missing = self.default_parent / "typo"
        guard = QuietGuard([missing], run=self.runner)
        with self.assertRaises(Refused):
            guard.check(force=True)
        self.assertIn(str(missing), guard.receipts[-1]["refusal"])
        self.assertIn("errno 2", guard.receipts[-1]["refusal"])

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
            entry = SimpleNamespace(name="restricted", path=str(root / "restricted"))
            with patch("joulewise.align.r0_host.os.scandir") as scan:
                scan.return_value.__enter__.return_value = [entry]
                with self.assertRaisesRegex(ValueError, "refusing restricted path"):
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
            self.assertEqual(result["smc_step_budget"]["capture_seconds"], 2700)  # 1200 idle cap +900 load +600 recovery.

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
                # D3 cap covers the measured ~930 s median /1,038 s maximum settle.
                self.assertEqual(argv[argv.index("--idle-max-seconds") + 1], "1200")
                self.assertEqual(argv[argv.index("--recovery-seconds") + 1], "600")
                self.assertEqual(call.call_args.kwargs["timeout"], 3300)  # Maximum 2700 s capture +600 s margin.
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
                # The capture-wide block is diagnostic; D6 reads the classifier rows.
                self.assertEqual(smc_enumeration(root, output)["status"], "pass")

    def test_r0l3_sustained_contention_redoes_smc_once_then_records_contended(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts/align_smc_enumerate.py").write_text("# fake hook")
            output = root / "smc"
            episode = {"start_ns": 0, "end_ns": 60 * 10**9, "seconds": 60.0, "intervals": 7, "max_cores": 0.6}
            policies = []
            def run(argv, **kwargs):
                policies.append(argv[argv.index("--contention-policy") + 1])
                output.mkdir()
                if len(policies) == 1:
                    (output / "contention.json").write_text(json.dumps({"episodes": [episode], "contended": False}))
                    return subprocess.CompletedProcess(argv, 4, "", "R0 capture abandoned for one redo")
                payload = write_capture(output, **WP14A_STEP)
                payload["contention"] = {"policy": "flag", "flags": [], "episodes": [episode], "contended": True}
                (output / "r0.json").write_text(json.dumps(payload))
                return subprocess.CompletedProcess(argv, 0, "", "")
            with patch("subprocess.run", side_effect=run):
                result = smc_enumeration(root, output)
            self.assertEqual(policies, ["redo", "flag"])
            # The redo capture is selection data with a flag, not a refusal.
            self.assertEqual(result["status"], "pass")
            self.assertTrue(result["contended"])
            self.assertEqual(result["contention"]["episodes"], [episode])
            self.assertIn("contention_by_phase", result)
            [rejected] = result["contention_redo"]
            self.assertEqual(rejected["exit_code"], 4)
            self.assertEqual(rejected["contention"]["episodes"], [episode])
            self.assertEqual(Path(rejected["output_dir"]), root / "smc.rejected1")
            self.assertTrue((root / "smc.rejected1" / "contention.json").is_file())

    def test_r0l3_census_failure_is_not_redone(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts/align_smc_enumerate.py").write_text("# fake hook")
            with patch("subprocess.run", return_value=subprocess.CompletedProcess(
                    [], 3, "", "R0 refused/failed: NotQuiet: measurement process active")) as call:
                result = smc_enumeration(root, root / "smc")
            self.assertEqual(call.call_count, 1)
            argv = call.call_args.args[0]
            self.assertEqual(argv[argv.index("--contention-policy") + 1], "redo")
            self.assertEqual((result["status"], result["contention_redo"], result["contended"]), ("fail", [], False))

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
            # Maximum idle 1200 +load 1200 +recovery 700 +existing margin 600.
            self.assertEqual(call.call_args.kwargs["timeout"], 3700)

    def replay_capture(self, payload, samples):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            raw = ('\n'.join(json.dumps(r) for r in samples)+'\n').encode()
            payload.update(samples_journal='samples.jsonl', samples_sha256=hashlib.sha256(raw).hexdigest())
            (output/'samples.jsonl').write_bytes(raw)
            (output/'r0.json').write_text(json.dumps(payload))
            with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 0, '', '')):
                return smc_enumeration(Path(__file__).resolve().parents[2], output)

    def test_fable_f3_handshake_shift_is_not_a_sampling_hole(self):
        from tests.align.test_r0_step import synthetic_capture
        payload, samples = synthetic_capture(**WP14A_STEP)
        # receipt_variants.py: +0.75 s MLX handshake makes the cross-phase
        # interval >2 s with the last idle midpoint shifted 0.3 s earlier.
        shift = 750_000_000
        for stamp in ('started', 'finished'):
            samples[299][stamp]['monotonic_ns'] -= 300_000_000
        for phase in payload['phases'][1:]:
            phase['start_s'] += shift/1e9
            phase['end_s'] += shift/1e9
        for sample in samples:
            if sample['phase'] != 'idle':
                for stamp in ('started', 'finished'):
                    sample[stamp]['monotonic_ns'] += shift
        self.assertEqual(self.replay_capture(payload, samples)['status'], 'pass')

    def assert_ordering_flags_printed(self, payload, receipt):
        from scripts.align_smc_enumerate import markdown
        summary = markdown({**payload, 'response': receipt['response']}, 'synthetic-digest')
        for name in ('recovery_onset_gap_s', 'heat_ordering_indeterminate',
                     'heat_ordering_wide_exclusion', 'heat_ordering_exclusion_count'):
            self.assertEqual(receipt[name], receipt['response'][name])
            self.assertIn(name + ': ', summary)
        self.assertIn('reference_crossing_censored', summary)
        return summary

    def test_erratum5_delayed_onset_is_printed_and_does_not_refuse(self):
        from tests.align.test_r0_step import synthetic_capture
        payload, samples = synthetic_capture({'Tf18': 20, 'TaLP': 100}, idle_jitter=.02)
        payload['coverage']['all_keys'] = {'sample_fraction': 1}
        payload['phases'][2]['start_s'] += 25
        receipt = self.replay_capture(payload, samples)
        self.assertEqual(receipt['status'], 'pass')
        self.assertTrue(receipt['heat_ordering_indeterminate'])
        # The analytic fixture reads 0.1 s into each cell, after admission.
        self.assertAlmostEqual(receipt['recovery_onset_gap_s'], 25.1, places=9)
        self.assertTrue(next(r for r in receipt['response']['ranking'] if r['key'] == 'Tf18')['reference_crossing_censored'])
        summary = self.assert_ordering_flags_printed(payload, receipt)
        self.assertIn('heat_ordering_indeterminate: true', summary)
        self.assertIn('recovery_onset_gap_s: 25', summary)

    def test_erratum5_two_exclusions_print_count_without_refusal(self):
        from tests.align.test_r0_step import synthetic_capture
        payload, samples = synthetic_capture({'TSRC': 20, 'TEX1': 35, 'TEX2': 40, 'THEA': 100}, idle_jitter=.02)
        payload['coverage']['all_keys'] = {'sample_fraction': 1}
        for sample in samples:
            for key, factor in (('TEX1', 2), ('TEX2', 2.5)):
                sample['values']['sensors'][key] = 40 + factor*(sample['values']['sensors'][key]-40)
        receipt = self.replay_capture(payload, samples)
        self.assertEqual(receipt['status'], 'pass')
        self.assertEqual(receipt['selection'], {'s_fast': 'TSRC', 's_slow': 'THEA'})
        self.assertEqual(receipt['heat_ordering_excluded'], ['TEX1', 'TEX2'])
        self.assertTrue(receipt['heat_ordering_wide_exclusion'])
        self.assertEqual(receipt['heat_ordering_exclusion_count'], 2)
        summary = self.assert_ordering_flags_printed(payload, receipt)
        self.assertIn('heat_ordering_wide_exclusion: true', summary)
        self.assertIn('heat_ordering_exclusion_count: 2', summary)

    @unittest.skipUnless(Path('/Users/edr/night-align/r0-v4-20261107T0810Z/smc/r0.json').is_file(),
                         'recorded Mac15,9 journal is optional outside the replay bench')
    def test_erratum5_real_capture_has_uncensored_onset_and_prints_flags(self):
        # Offline replay of immutable capture bytes, never hardware collection.
        source = Path('/Users/edr/night-align/r0-v4-20261107T0810Z/smc')
        payload = json.loads((source/'r0.json').read_text())
        samples = [json.loads(line) for line in (source/'samples.jsonl').read_text().splitlines()]
        receipt = self.replay_capture(payload, samples)
        self.assertEqual(receipt['status'], 'pass')
        self.assertEqual(receipt['selection'], {'s_fast': 'Tf18', 's_slow': 'TaLP'})
        # Erratum 5's real gap is reported to two decimal places, not a new gate.
        self.assertEqual(round(receipt['recovery_onset_gap_s'], 2), .17)
        self.assertFalse(receipt['heat_ordering_indeterminate'])
        self.assertFalse(receipt['heat_ordering_wide_exclusion'])
        self.assertEqual(receipt['heat_ordering_exclusion_count'], 1)
        rows = {r['key']: r for r in receipt['response']['ranking']}
        self.assertFalse(rows['Tf18']['reference_crossing_censored'])
        summary = self.assert_ordering_flags_printed(payload, receipt)
        self.assertIn('heat_ordering_indeterminate: false', summary)

    def test_opus_f2_single_missed_tf18_read_with_unlucky_jitter_passes(self):
        from tests.align.test_r0_step import synthetic_capture
        payload, samples = synthetic_capture({'Tf18': 20, 'TaLP': 100}, idle_jitter=.02)
        # holes.py B: one failed read out of 900 (<1%) with predecessor
        # early and successor 150 ms late gives a 2.15 s midpoint interval.
        samples[700]['values']['errors']['Tf18'] = 'synthetic missed read'
        for stamp in ('started', 'finished'):
            samples[701][stamp]['monotonic_ns'] += 150_000_000
        result = self.replay_capture(payload, samples)
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['selection']['s_fast'], 'Tf18')

    def test_fable_f4_load_end_overrun_is_a_flag(self):
        from tests.align.test_r0_step import synthetic_capture
        payload, samples = synthetic_capture(**WP14A_STEP)
        # receipt_variants.py: +1.3 s quiet-probe latency at load end;
        # one trailing empty cell still clears 99% coverage (900/901).
        payload['phases'][1]['end_s'] += 1.3
        for field in ('start_s', 'end_s'):
            payload['phases'][2][field] += 1.3
        for sample in samples:
            if sample['phase'] == 'recovery':
                for stamp in ('started', 'finished'):
                    sample[stamp]['monotonic_ns'] += 1_300_000_000
        result = self.replay_capture(payload, samples)
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['phase_duration_flags'][0]['phase'], 'load')
        # Exact synthetic clock arithmetic; nine places allow only float noise.
        self.assertAlmostEqual(result['phase_duration_flags'][0]['deviation_seconds'], 1.3, places=9)

    def test_opus_exit_overrun_does_not_add_two_empty_load_cells(self):
        from tests.align.test_r0_step import synthetic_capture
        payload, samples = synthetic_capture(**WP14A_STEP)
        # Opus h.py overrun:load:1.6 extends the end without extra reads.
        # Nearest-cell rounding adds two empty cells at +1.6 s (>1.5 s),
        # falsely failing D6 even though every configured load cell exists.
        payload['phases'][1]['end_s'] += 1.6
        for field in ('start_s', 'end_s'):
            payload['phases'][2][field] += 1.6
        for sample in samples:
            if sample['phase'] == 'recovery':
                for stamp in ('started', 'finished'):
                    sample[stamp]['monotonic_ns'] += 1_600_000_000
        result = self.replay_capture(payload, samples)
        self.assertEqual(result['status'], 'pass')
        # Exact synthetic clock arithmetic; nine places allow only float noise.
        self.assertAlmostEqual(result['phase_duration_flags'][0]['deviation_seconds'], 1.6, places=9)
        for row in result['selected_key_readability'].values():
            self.assertEqual(row['phase_max_empty_cells']['load'], 0)
            self.assertEqual(row['phase_seconds']['load'], 900)  # Configured D3 load.
        for field in ('heat_ordering_reference', 'heat_ordering_reference_rise', 'heat_ordering_excluded'):
            self.assertEqual(result[field], result['response'][field])

    def test_receipt_prints_exact_aliases_of_each_selected_key(self):
        from tests.align.test_r0_step import synthetic_capture
        payload, samples = synthetic_capture({'TC0P': 20, 'TCOP': 20, 'TH0P': 100}, idle_jitter=.02)
        result = self.replay_capture(payload, samples)
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['selected_key_aliases'], {'TC0P': ['TCOP'], 'TH0P': []})

    def test_receipt_rechecks_consecutive_empty_cells(self):
        from joulewise.align.apple.smc_enumeration import rank
        from tests.align.test_r0_step import synthetic_capture
        payload, samples = synthetic_capture(**WP14A_STEP)
        classification = rank({**payload, 'samples': samples})
        # Keep the classifier's selection/pass result but forge two empty
        # load cells: the independent receipt must still refuse that pick.
        next(r for r in classification['ranking'] if r['key'] == 'TC0P')['phase_max_empty_cells']['load'] = 2
        with patch('joulewise.align.r0_host.classify_smc', return_value=classification):
            result = self.replay_capture(payload, samples)
        self.assertEqual(result['status'], 'inconclusive')
        self.assertFalse(result['readability_bar_met'])

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

    def test_smc_receipt_reads_per_phase_jitter_and_refuses_actual_hole(self):
        for hole in (False, True):
            with self.subTest(hole=hole), tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp)
                data = jittered_capture()
                if hole:
                    # Drop t=500 and move its successor midpoint to 501.55;
                    # predecessor midpoint 499.05 => genuine 2.5 s hole.
                    data['samples'] = [r for r in data['samples'] if int(r['elapsed_s']) != 500]
                    for r in data['samples']:
                        t = int(r['elapsed_s'])
                        if t in (499, 501):
                            start = t + (0.5 if t == 501 else 0)
                            r['started']['monotonic_ns'] = round(start*1e9)
                            r['finished']['monotonic_ns'] = round((start+.1)*1e9)
                raw = ('\n'.join(json.dumps(r) for r in data.pop('samples'))+'\n').encode()
                (output/'samples.jsonl').write_bytes(raw)
                data.update(schema='joulewise.align_smc_r0.v1', gpu_step=True,
                            samples_journal='samples.jsonl', samples_sha256=hashlib.sha256(raw).hexdigest(),
                            response={}, coverage={'period_ns': 1_000_000_000,
                            'all_keys': {'sample_fraction': .02}})
                (output/'r0.json').write_text(json.dumps(data))
                with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 0, '', '')):
                    result = smc_enumeration(Path(__file__).resolve().parents[2], output)
                self.assertEqual(result['selection'], {'s_fast': None, 's_slow': None} if hole else
                                 {'s_fast': 'TDIE', 's_slow': 'THEA'})
                self.assertEqual(result['status'], 'inconclusive' if hole else 'pass')
                for row in result['response']['ranking']:
                    # Midpoint shifted across the half-cell boundary leaves
                    # two adjacent empty cells, while coverage remains >99%.
                    self.assertGreaterEqual(min(row['phase_coverage'].values()), .99)
                    self.assertEqual(row['phase_max_empty_cells']['load'], 2 if hole else 0)


def fake_pmset(displaysleep="0", log="", *, fail=False):
    """A fake pmset: `-g` settings and `-g log` (RUN_STATE 206 shapes)."""
    calls = []
    def run(argv, **kwargs):
        calls.append(tuple(argv))
        if fail:
            raise FileNotFoundError("pmset")
        if tuple(argv[1:]) == ("-g",):
            return subprocess.CompletedProcess(argv, 0, f"System-wide power settings:\n displaysleep         {displaysleep}\n", "")
        if tuple(argv[1:]) == ("-g", "log"):
            return subprocess.CompletedProcess(argv, 0, log, "")
        raise AssertionError(argv)
    return run, calls


PMSET_LOG = (
    "2026-11-05 23:41:00 -0800 Notification        \tDisplay is turned on                \t\n"
    "2026-11-07 18:08:12 -0800 Notification        \tDisplay is turned off               \t\n"
    "2026-11-07 18:40:00 -0800 Sleep               \tEntering Sleep state                 \t\n"
    "2026-11-07 18:50:00 -0800 Notification        \tDisplay is turned on                \t\n"
    "2026-11-07 18:50:30 -0800 Notification        \tDisplay is turned off               \t\n"
    "2026-11-07 22:00:00 -0800 Notification        \tDisplay is turned on                \t\n")


class R0DisplayCensusTest(unittest.TestCase):
    def epoch(self, text):
        from datetime import datetime
        return datetime.strptime(text, "%Y-%m-%d %H:%M:%S %z").timestamp()

    def test_display_census_records_setting_state_and_transitions_in_the_run(self):
        from joulewise.align.r0_host import display_census
        run, calls = fake_pmset("0", PMSET_LOG)
        start, end = self.epoch("2026-11-07 18:30:00 -0800"), self.epoch("2026-11-07 19:30:00 -0800")
        record = display_census(start, end, run=run)
        self.assertEqual(calls, [("/usr/bin/pmset", "-g"), ("/usr/bin/pmset", "-g", "log")])
        self.assertEqual(record["displaysleep_minutes"], 0)
        self.assertEqual(record["display_at_start"], "off")
        self.assertEqual([(t["state"], t["epoch_s"]) for t in record["transitions"]],
                         [("on", self.epoch("2026-11-07 18:50:00 -0800")),
                          ("off", self.epoch("2026-11-07 18:50:30 -0800"))])
        self.assertTrue(record["display_woke_during_run"])

    def test_unavailable_pmset_is_recorded_never_raised(self):
        from joulewise.align.r0_host import display_census
        run, _ = fake_pmset(fail=True)
        record = display_census(0, 1, run=run)
        self.assertIn("FileNotFoundError", record["pmset_g_error"])
        self.assertIn("FileNotFoundError", record["pmset_log_error"])
        self.assertIsNone(record["display_woke_during_run"])


class R0SamplerAdmissionSpec(unittest.TestCase):
    setUp = R0HostTest.setUp
    runner = R0HostTest.runner

    def admission(self, *, busy=True):
        clock = GuardClock()
        cpu = "0:00.00"
        launchctl_at = []
        bad_census_at = set()
        def run(argv, **kwargs):
            if argv == contention.PS_ARGV:
                return subprocess.CompletedProcess(
                    argv, 0, cpu_table((42, OLD_START, cpu, "mdworker_shared")), "")
            if argv[0] == "/bin/launchctl":
                launchctl_at.append(clock.now)
                if clock.now in bad_census_at:
                    return subprocess.CompletedProcess(argv, 1, "", "fixture failure")
            return self.runner(argv, **kwargs)
        guard = QuietGuard([], run=run, inspect_custody=lambda **kw: Census(),
                           clock=clock, sleep=clock.sleep)
        guard.host_reader = None
        guard.wall_clock_ns = lambda: 1_800_000_000_000_000_000 + int(clock.now * 1e9)
        guard.SNAPSHOT_CADENCE_S = 3600  # Only the fixture advances the sampler.
        close = getattr(guard, "close", None)
        if close is not None:
            self.addCleanup(close)

        def advance(at, *, census_ok=True):
            nonlocal cpu
            clock.now = at
            cpu = "0:01.80" if busy and at >= 45 else "0:00.00"
            if not census_ok:
                bad_census_at.add(at)
            sample = getattr(guard, "_background_snapshot", None)
            if sample is not None:
                sample()
        return guard, clock, advance, launchctl_at

    def test_early_busy_window_cannot_mask_a_queued_excessive_interval(self):
        guard, _, advance, launchctl_at = self.admission()
        guard.check(force=True)
        for at in (45, 105, 120):
            advance(at)
        with self.assertRaisesRegex(Refused, "judged CPU window of 60.0 s exceeds"):
            guard.check(force=True)
        receipt = guard.receipts[-1]
        self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in guard.contention_flags],
                         [45])
        self.assertEqual([window["end_monotonic_s"] for window in receipt["cpu_intervals"]],
                         [45, 105])
        self.assertEqual(launchctl_at, [0, 30, 45, 105, 120])

    def test_early_busy_window_allows_later_windows_and_their_censuses(self):
        guard, _, advance, launchctl_at = self.admission()
        guard.check(force=True)
        for at in (45, 60, 75, 90):
            advance(at)
        guard.check(force=True)
        receipt = guard.receipts[-1]
        self.assertEqual([window["end_monotonic_s"] for window in receipt.get("cpu_intervals", ())],
                         [45, 60, 75, 90])
        self.assertEqual([entry["monotonic_s"] for entry in receipt["background_census"]],
                         [45, 60, 75, 90])
        self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in guard.contention_flags],
                         [45, 60])
        self.assertEqual(launchctl_at, [0, 30, 45, 60, 75, 90, 90])
        self.assertIsNone(guard.failure)

    def test_invalid_background_census_still_refuses_after_contention(self):
        guard, _, advance, _ = self.admission()
        guard.check(force=True)
        advance(45)
        guard.check(force=True)
        self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in guard.contention_flags], [45])
        advance(60, census_ok=False)
        with self.assertRaisesRegex(Refused, "background sampler: .*LaunchAgent census indeterminate"):
            guard.check()
        self.assertIn("LaunchAgent census indeterminate", guard.receipts[-1]["refusal"])

    def test_stalled_sampler_still_refuses_after_contention(self):
        guard, clock, advance, _ = self.admission()
        guard.check(force=True)
        advance(45)
        guard.check(force=True)
        self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in guard.contention_flags], [45])
        clock.now = 96
        with self.assertRaisesRegex(Refused, "background snapshots stalled"):
            guard.check(force=True)

    def test_caller_gap_retains_contention_and_quiet_control(self):
        for busy in (True, False):
            with self.subTest(busy=busy):
                guard, clock, advance, launchctl_at = self.admission(busy=busy)
                guard.check(force=True)
                for at in range(45, 331, 15):
                    advance(at)
                guard.check(force=True)
                self.assertEqual(launchctl_at, [0, 30, *range(45, 331, 15), 330])
                self.assertEqual(sum(clock.sleeps), prewindow.INTERVAL_S)
                self.assertEqual(len(guard.receipts[-1]["cpu_intervals"]), 20)
                self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in guard.contention_flags],
                                 [45, 60] if busy else [])
                self.assertIsNone(guard.failure)

    def test_execute_reports_guard_flag_before_a_later_refusal(self):
        from contextlib import nullcontext
        from joulewise.align import r0_runner
        from tests.align.test_r0_checks import FakeBackend

        for last, reason, expected_flags in ((60, "R0-L3 contention flagged", 2), (105, "exceeds", 1)):
            with self.subTest(last=last), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                guard, _, advance, _ = self.admission()
                def host():
                    advance(45)
                    advance(last)
                    return {"status": "pass"}
                with patch.object(r0_runner, "host_snapshot", side_effect=host), \
                        patch.object(r0_runner, "deadline", return_value=nullcontext()), \
                        patch.object(r0_runner, "command", return_value="synthetic-head"), \
                        patch.object(r0_runner, "softwareupdate_scan_forecast", create=True,
                                     return_value={"status": "unknown"}):
                    report = r0_runner.execute(config_at(root), root, ["host"], ["D"],
                                               guard=guard, backend_factory=FakeBackend)
                self.assertEqual(report["status"], "refused")
                self.assertEqual(report["checks"][0]["status"], "refused")
                self.assertIn(reason, report["refusal"])
                self.assertEqual(report["checks"][0]["contention_flags"][0]["interval"]["end_monotonic_s"], 45)
                self.assertEqual(report["contention"]["guard_flags"], expected_flags)
                self.assertEqual(json.loads((root / "report.json").read_text())["status"], "refused")
                self.assertTrue(guard._stop_sampler.is_set())

    def execute_host(self, guard, host, output):
        from contextlib import nullcontext
        from joulewise.align import r0_runner
        from tests.align.test_r0_checks import FakeBackend

        with patch.object(r0_runner, "host_snapshot", side_effect=host), \
                patch.object(r0_runner, "deadline", return_value=nullcontext()), \
                patch.object(r0_runner, "command", return_value="synthetic-head"), \
                patch.object(r0_runner, "softwareupdate_scan_forecast", return_value={"status": "unknown"}):
            return r0_runner.execute(config_at(output), output, ["host"], ["D"],
                                     guard=guard, backend_factory=FakeBackend)

    def test_execute_refuses_census_failure_during_final_check(self):
        import threading

        guard, clock, _, _ = self.admission()
        guard.SNAPSHOT_CADENCE_S = 0.001
        host_started = threading.Event()
        probing = threading.Event()
        finish_probe = threading.Event()
        self.addCleanup(finish_probe.set)
        run = guard.run

        def invalid_census(argv, **kwargs):
            if argv[0] == "/bin/launchctl" and threading.current_thread() is not threading.main_thread():
                self.assertTrue(host_started.wait(3))
                probing.set()
                self.assertTrue(finish_probe.wait(3))
                return subprocess.CompletedProcess(argv, 1, "", "invalid synthetic census")
            return run(argv, **kwargs)

        def host():
            clock.now = 45
            host_started.set()
            self.assertTrue(probing.wait(3))
            return {"status": "pass"}

        def release_at_final_check():
            if threading.current_thread() is threading.main_thread() and host_started.is_set():
                finish_probe.set()
                self.assertTrue(guard._stop_sampler.wait(3))
            return clock()

        guard.run = invalid_census
        guard.clock = release_at_final_check
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            report = self.execute_host(guard, host, output)
            published = json.loads((output / "report.json").read_text())
        self.assertEqual(report["status"], "refused")
        self.assertEqual(published["status"], "refused")
        self.assertEqual(published["checks"][0]["status"], "refused")
        self.assertIn("LaunchAgent census indeterminate", published["refusal"])
        self.assertFalse(published["complete_r0"])

    def test_execute_finishes_inflight_census_before_publishing(self):
        import threading

        for outcome in ("valid", "invalid", "stalled"):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory() as tmp:
                guard, clock, _, _ = self.admission()
                guard.SNAPSHOT_CADENCE_S = 0.001
                guard.JOIN_TIMEOUT_S = 0.05 if outcome == "stalled" else 1.0
                host_started = threading.Event()
                probing = threading.Event()
                release = threading.Event()
                run = guard.run

                def census(argv, **kwargs):
                    if threading.current_thread() is not threading.main_thread():
                        if argv[0] == "/bin/launchctl":
                            if not host_started.wait(3):
                                raise AssertionError("fixture host never started")
                            probing.set()
                            ready = release if outcome == "stalled" else guard._stop_sampler
                            if not ready.wait(3):
                                raise AssertionError("fixture census never released")
                            if outcome == "invalid":
                                return subprocess.CompletedProcess(argv, 1, "", "invalid synthetic census")
                        if argv == contention.PS_ARGV:
                            return subprocess.CompletedProcess(
                                argv, 0, cpu_table((42, OLD_START, "0:01.80", "mdworker_shared")), "")
                    return run(argv, **kwargs)

                def host():
                    clock.now = 45
                    host_started.set()
                    self.assertTrue(probing.wait(3))
                    return {"status": "pass"}

                guard.run = census
                output = Path(tmp)
                try:
                    self.execute_host(guard, host, output)
                    published = json.loads((output / "report.json").read_text())
                finally:
                    release.set()
                    guard.close()
                row = published["checks"][0]
                if outcome == "valid":
                    self.assertEqual((published["status"], row["status"]), ("refused", "refused"))
                    self.assertIn("R0-L3 contention flagged", published["refusal"])
                    self.assertEqual([flag["interval"]["end_monotonic_s"]
                                      for flag in row.get("contention_flags", ())], [45])
                    self.assertEqual(published["census"][-1]["background_census"][0]["monotonic_s"], 45)
                else:
                    self.assertEqual((published["status"], row["status"]), ("refused", "refused"))
                    message = ("LaunchAgent census indeterminate" if outcome == "invalid"
                               else "background sampler did not stop")
                    self.assertIn(message, published["refusal"])
                    self.assertFalse(published["complete_r0"])

    def test_inventory_refuses_census_failure_at_eof(self):
        from contextlib import contextmanager, redirect_stderr
        from io import StringIO
        from joulewise.align.r0_runner import main

        guard, _, advance, _ = self.admission()
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            inputs = work / "inputs"
            inputs.mkdir()
            payload = inputs / "blob"
            payload.write_bytes(b"fixture")
            config = work / "config.json"
            config.write_text(json.dumps(config_at(work)))
            published = work / "inventory.json"
            open_path = Path.open

            @contextmanager
            def inventory_input():
                with open_path(payload, "rb") as handle:
                    class DelayedEOF:
                        def read(self, size):
                            chunk = handle.read(size)
                            if not chunk:
                                advance(45, census_ok=False)
                            return chunk
                    yield DelayedEOF()

            def fixture_open(path, *args, **kwargs):
                return inventory_input() if path == payload else open_path(path, *args, **kwargs)

            stderr = StringIO()
            with patch.object(Path, "open", fixture_open), redirect_stderr(stderr):
                status = main(["--config", str(config), "--output", str(published), "--inventory", str(inputs)],
                              guard_factory=lambda _: guard, lock_path=work / "lock")
            self.assertEqual(status, 2)
            self.assertIn("LaunchAgent census indeterminate", stderr.getvalue())
            self.assertFalse(published.exists())

    def test_inventory_census_refusal_takes_precedence_over_input_read_error(self):
        from contextlib import contextmanager, redirect_stderr
        import errno
        from io import StringIO
        import os
        from joulewise.align.r0_runner import main
        from joulewise.measurement_liveness import census

        for input_error in (False, True):
            with self.subTest(input_error=input_error), tempfile.TemporaryDirectory() as tmp:
                work = Path(tmp).resolve()
                required, inputs = work / "required", work / "inputs"
                required.mkdir()
                inputs.mkdir()
                payload = inputs / "blob"
                payload.write_bytes(b"fixture")
                config = work / "config.json"
                config.write_text(json.dumps({**config_at(work), "custody_parents": [str(required)]}))
                output = work / "inventory.json"
                guard, clock, advance, _ = self.admission(busy=False)
                guard.parents = [required]
                guard.inspect_custody = census
                open_path, scandir = Path.open, os.scandir
                root_stat = required.stat()

                def scan(value):
                    if clock.now == 45 and isinstance(value, int) and os.path.samestat(root_stat, os.fstat(value)):
                        raise OSError(errno.EIO, "synthetic census failure", str(required))
                    return scandir(value)

                @contextmanager
                def opened(path, *args, **kwargs):
                    with open_path(path, *args, **kwargs) as handle:
                        if path != payload:
                            yield handle
                            return

                        class Input:
                            def read(self, size):
                                if clock.now < 45:
                                    advance(45)
                                    if input_error:
                                        raise OSError(errno.EIO, "synthetic inventory failure", str(payload))
                                return handle.read(size)

                        yield Input()

                stderr = StringIO()
                with patch.object(Path, "open", opened), patch.object(os, "scandir", scan), redirect_stderr(stderr):
                    status = main(["--config", str(config), "--output", str(output), "--inventory", str(inputs)],
                                  guard_factory=lambda _: guard, lock_path=work / "lock")
                self.assertEqual(status, 2)
                self.assertIn(f"{required} (errno {errno.EIO})", stderr.getvalue())
                self.assertFalse(output.exists())

    def test_inventory_rechecks_agents_after_serializing_before_publication(self):
        from contextlib import redirect_stderr
        from io import StringIO
        from joulewise import agent_identity
        from joulewise.align.r0_runner import main

        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp).resolve()
            inputs = work / "inputs"
            inputs.mkdir()
            (inputs / "blob").write_bytes(b"fixture")
            config = work / "config.json"
            config.write_text(json.dumps(config_at(work)))
            output = work / "inventory.json"
            guard, _, _, _ = self.admission(busy=False)
            normal = guard.run
            executable = "/Applications/Codex.app/Contents/MacOS/Codex"
            encoded = False

            def run(argv, **kwargs):
                if encoded and argv[0] == "/usr/bin/pgrep":
                    return subprocess.CompletedProcess(argv, 0, f"42 {executable}\n", "")
                return normal(argv, **kwargs)

            dumps = json.dumps

            def encode(rows, **kwargs):
                nonlocal encoded
                result = dumps(rows, **kwargs)
                encoded = True
                return result

            filter_census = agent_identity.filter_census
            info = agent_identity.ProcessInfo(42, 1, 42, executable, (executable,))
            guard.run = run
            stderr = StringIO()
            with (patch.object(json, "dumps", side_effect=encode),
                  patch.object(agent_identity, "filter_census",
                               lambda stdout, **kwargs: filter_census(stdout, inspector=lambda _: info, **kwargs)),
                  redirect_stderr(stderr)):
                status = main(["--config", str(config), "--output", str(output), "--inventory", str(inputs)],
                              guard_factory=lambda _: guard, lock_path=work / "lock")
            self.assertTrue(encoded)
            self.assertEqual(status, 2)
            self.assertIn(executable, stderr.getvalue())
            self.assertFalse(output.exists())

    def test_queued_contention_survives_census_failure_or_stall(self):
        for reason, message in (("census", "LaunchAgent census indeterminate"),
                                ("stall", "background snapshots stalled")):
            with self.subTest(reason=reason):
                guard, clock, advance, _ = self.admission()
                guard.check(force=True)
                advance(45)
                if reason == "census":
                    advance(60, census_ok=False)
                else:
                    clock.now = 96
                with self.assertRaisesRegex(Refused, message):
                    guard.check(force=True)
                self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in guard.contention_flags], [45])
                self.assertIn("contention_flag", guard.receipts[-1])

    def test_execute_refuses_when_background_launchagent_directory_is_unreadable(self):
        import errno
        import os
        import threading

        agents = self.default_parent / "Library" / "LaunchAgents"
        agents.mkdir(parents=True)
        plist = agents / "com.joulewise.night.future.plist"
        scandir = os.scandir
        for denied in (False, True):
            with self.subTest(denied=denied), tempfile.TemporaryDirectory() as tmp:
                guard, clock, _, _ = self.admission()
                guard.SNAPSHOT_CADENCE_S = 0.001
                ready = threading.Event()
                sampled = threading.Event()
                cycle = guard._background_snapshot

                def watch_cycle():
                    if ready.wait(3):
                        cycle()
                        sampled.set()

                def fixture_scandir(path):
                    if denied and ready.is_set() and Path(path) == agents:
                        raise PermissionError(errno.EACCES, "fixture LaunchAgents listing denied")
                    return scandir(path)

                def host():
                    plist.write_text("synthetic installed future window")
                    clock.now = 45
                    ready.set()
                    self.assertTrue(sampled.wait(3))
                    return {"status": "pass"}

                guard._background_snapshot = watch_cycle
                output = Path(tmp)
                with patch("joulewise.align.r0_host.os.scandir", side_effect=fixture_scandir):
                    self.execute_host(guard, host, output)
                plist.unlink()
                published = json.loads((output / "report.json").read_text())
                self.assertEqual(published["status"], "refused")
                self.assertEqual(published["checks"][0]["status"], "refused")
                if denied:
                    self.assertIn(f"{agents} (errno {errno.EACCES})", published["refusal"])
                else:
                    self.assertIn("measurement window armed", published["refusal"])
                self.assertEqual([entry for receipt in published["census"]
                                  for entry in receipt.get("background_census", ())], [])

    def test_launchagent_enumeration_errors_after_presence_is_observed_refuse_at_admission(self):
        from contextlib import contextmanager
        import errno
        import os

        agents = self.default_parent / "Library" / "LaunchAgents"
        agents.mkdir(parents=True)
        scandir = os.scandir
        for error in (FileNotFoundError(errno.ENOENT, "fixture directory vanished"),
                      OSError(errno.EIO, "fixture enumeration failed")):
            for partial in (False, True):
                with self.subTest(error=error.errno, partial=partial):
                    guard, _, _, launchctl_at = self.admission()

                    def entries():
                        yield SimpleNamespace(path=str(agents / "unrelated.plist"), name="unrelated.plist")
                        raise error

                    @contextmanager
                    def partial_listing():
                        yield entries()

                    def fixture_scandir(path):
                        if Path(path) != agents:
                            return scandir(path)
                        if partial:
                            return partial_listing()
                        raise error

                    with patch("joulewise.align.r0_host.os.scandir", side_effect=fixture_scandir):
                        with self.assertRaisesRegex(Refused, f"errno {error.errno}"):
                            guard.check(force=True)
                    self.assertEqual(launchctl_at, [])
                    self.assertNotIn("installed_night_agents", guard.receipts[-1])

    def test_execute_retains_sampler_refusal_and_contention_when_host_check_fails(self):
        guard, _, advance, _ = self.admission()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)

            def host():
                advance(45)
                advance(60, census_ok=False)
                raise RuntimeError("injected host failure")

            self.execute_host(guard, host, output)
            published = json.loads((output / "report.json").read_text())
        row = published["checks"][0]
        self.assertEqual((published["status"], row["status"]), ("fail", "fail"))
        self.assertEqual(row["error"], "RuntimeError: injected host failure")
        self.assertIn("LaunchAgent census indeterminate", published.get("refusal", ""))
        self.assertEqual(published["contention"]["guard_flags"], 1)
        self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in row["contention_flags"]], [45])

    def test_cli_refuses_when_required_background_census_root_cannot_be_enumerated(self):
        from contextlib import nullcontext
        import os
        import threading
        from joulewise.align import r0_runner
        from joulewise.measurement_liveness import census
        from tests.align.test_r0_checks import FakeBackend

        open_directory = os.open
        for mode in ("quiet", "before", "during", "transient"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                work = Path(tmp).resolve()
                required = work / "required-parent"
                required.mkdir()
                detached = work / "detached-parent"
                config = config_at(work)
                config["custody_parents"] = [str(required)]
                config_file = work / "config.json"
                config_file.write_text(json.dumps(config))
                output = work / "output"
                guard, clock, _, _ = self.admission()
                guard.SNAPSHOT_CADENCE_S = 0.001
                ready = threading.Event()
                sampled = threading.Event()
                cycle, run = guard._background_snapshot, guard.run

                def guarded_cycle():
                    if ready.wait(3) and not sampled.is_set():
                        cycle()
                        sampled.set()

                def fake_command(argv, **kwargs):
                    if (mode == "during" and argv[0] == "/bin/launchctl"
                            and threading.current_thread() is not threading.main_thread()):
                        required.rename(detached)
                    return run(argv, **kwargs)

                def fixture_open(directory, flags, *, dir_fd=None):
                    if mode == "transient" and Path(directory) == required and ready.is_set():
                        required.rename(detached)
                        try:
                            return open_directory(directory, flags, dir_fd=dir_fd)
                        finally:
                            detached.rename(required)
                    return open_directory(directory, flags, dir_fd=dir_fd)

                def host():
                    if mode == "before":
                        required.rename(detached)
                    clock.now = 45
                    ready.set()
                    self.assertTrue(sampled.wait(3))
                    return {"status": "pass"}

                def unexpected_identity(_):
                    self.fail("unexpected process identity lookup")

                def factory(parents):
                    guard.parents = list(map(Path, parents))
                    guard._background_snapshot = guarded_cycle
                    guard.run = fake_command
                    guard.inspect_custody = lambda **kw: census(**kw, observer=unexpected_identity)
                    return guard

                with patch.object(os, "open", fixture_open), \
                        patch.object(r0_runner, "host_snapshot", side_effect=host), \
                        patch.object(r0_runner, "deadline", return_value=nullcontext()), \
                        patch.object(r0_runner, "command", return_value="synthetic-head"), \
                        patch.object(r0_runner, "softwareupdate_scan_forecast", return_value={"status": "unknown"}):
                    status = r0_runner.main(
                        ["--config", str(config_file), "--output", str(output), "--checks", "host"],
                        guard_factory=factory, backend_factory=FakeBackend, display_probe=None,
                        lock_path=work / "lock")
                if mode == "quiet":
                    record = output
                else:
                    self.assertFalse(output.exists())
                    record, = work.glob(".output.r0-*")
                published = json.loads((record / "report.json").read_text())
                cycles = [entry for receipt in published["census"]
                          for entry in receipt.get("background_census", ())]
                outcome = (status, published["status"], published["checks"][0]["status"])
                if mode == "quiet":
                    self.assertEqual(outcome, (0, "pass", "pass"))
                    self.assertEqual([entry["custody_clear"] for entry in cycles], [True])
                else:
                    self.assertEqual(outcome, (2, "refused", "refused"))
                    self.assertIn(f"{required} (errno 2)", published["refusal"])
                    self.assertEqual(cycles, [])

    def test_window_flags_proven_cpu_from_worker_seen_only_at_an_interior_snapshot(self):
        from datetime import datetime

        for birth, cpu, flagged in ((35, "0:01.80", [45, 60]),
                                    (20, "0:01.80", [45]),
                                    (35, "0:01.40", [])):
            with self.subTest(birth=birth, cpu=cpu), tempfile.TemporaryDirectory() as tmp:
                guard, clock, advance, _ = self.admission()
                run = guard.run
                wall = datetime(2026, 11, 6, 18, 0).timestamp()
                guard.wall_clock_ns = lambda: int((wall + clock.now) * 1e9)

                def command(argv, **kwargs):
                    if argv != contention.PS_ARGV:
                        return run(argv, **kwargs)
                    rows = []
                    if clock.now == 45:
                        rows.append((42, f"Fri Nov  6 18:00:{birth:02d} 2026", cpu, "mdworker_shared"))
                    return subprocess.CompletedProcess(argv, 0, cpu_table(*rows), "")

                def host():
                    advance(45)
                    advance(60)
                    return {"status": "pass"}

                guard.run = command
                report = self.execute_host(guard, host, Path(tmp))
                self.assertEqual(report["status"], "refused" if flagged else "pass")
                self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in guard.contention_flags], flagged)
                if 60 in flagged:
                    evidence = guard.contention_flags[-1]["busy"][0]
                    self.assertAlmostEqual(evidence["cpu_s_per_s"], 0.06)
                    self.assertIn("lower bound", evidence["basis"])

    def run_synthetic_host_cli(self, configured, guard, host):
        from contextlib import nullcontext, redirect_stderr, redirect_stdout
        from io import StringIO
        from joulewise.align import r0_runner
        from tests.align.test_r0_checks import FakeBackend

        work = configured.parent
        config = config_at(work)
        config["custody_parents"] = [str(configured)]
        config_file = work / "config.json"
        config_file.write_text(json.dumps(config))
        output = work / "output"
        guard.parents = [configured]
        stderr = StringIO()
        with (patch.object(r0_runner, "host_snapshot", side_effect=host),
              patch.object(r0_runner, "deadline", return_value=nullcontext()),
              patch.object(r0_runner, "command", return_value="synthetic-head"),
              patch.object(r0_runner, "softwareupdate_scan_forecast", return_value={"status": "unknown"}),
              redirect_stderr(stderr), redirect_stdout(StringIO())):
            status = r0_runner.main(["--config", str(config_file), "--output", str(output), "--checks", "host"],
                                    guard_factory=lambda _: guard, backend_factory=FakeBackend,
                                    display_probe=None, lock_path=work / "lock")
        return status, output, stderr.getvalue()

    def test_r0_cli_refuses_desktop_agents_in_its_own_census(self):
        import re
        from joulewise import agent_identity
        from joulewise.measurement_liveness import census

        claude = "/Applications/Claude.app/Contents/MacOS/Claude"
        codex = "/Applications/Codex.app/Contents/MacOS/Codex"
        for executable, args, start, refuses in (
                (None, (), 0, False), ("/usr/local/bin/claude", (), 45, True),
                (claude, (), 45, True), (codex, (), 45, True), (claude, (), 0, True),
                ("/bin/echo", (claude,), 45, False)):
            with self.subTest(executable=executable, args=args, start=start), tempfile.TemporaryDirectory() as tmp:
                required = Path(tmp).resolve() / "required"
                required.mkdir()
                guard, clock, advance, _ = self.admission(busy=False)
                guard.inspect_custody = census
                normal = guard.run
                candidate_times = []
                process_argv = (executable, *args) if executable else ()
                command_line = " ".join(process_argv)

                def run(argv, **kwargs):
                    active = bool(executable) and clock.now >= start
                    if argv[0] == "/usr/bin/pgrep":
                        flags = "".join(argv[1:-1])
                        self.assertTrue(set("alf") <= set(flags))
                        pattern = re.compile(argv[-1], re.I if "i" in flags else 0)
                        self.assertIsNone(pattern.search(" ".join(argv)))
                        hits = active and pattern.search(command_line)
                        if hits:
                            candidate_times.append(clock.now)
                        return subprocess.CompletedProcess(argv, 0 if hits else 1,
                                                           f"42 {command_line}\n" if hits else "", "")
                    if argv == prewindow.PS_ARGV:
                        return subprocess.CompletedProcess(argv, 0, "1 0.0 /sbin/launchd\n" +
                                                           (f"42 0.0 {command_line}\n" if active else ""), "")
                    if argv == contention.PS_ARGV:
                        workers = [(42, OLD_START, "0:01.00", Path(executable).name)] if active else []
                        return subprocess.CompletedProcess(argv, 0, cpu_table(*workers), "")
                    return normal(argv, **kwargs)

                def host():
                    for at in (45, 60, 75):
                        advance(at)
                        if guard._background_failure:
                            break
                    return {"status": "pass"}

                filter_census = agent_identity.filter_census

                def filter_fixture(stdout, **kwargs):
                    info = agent_identity.ProcessInfo(42, 1, 42, executable, process_argv)
                    return filter_census(stdout, inspector=lambda _: info, **kwargs)

                guard.run = run
                with patch.object(agent_identity, "filter_census", filter_fixture):
                    status, output, diagnostic = self.run_synthetic_host_cli(required, guard, host)
                self.assertEqual((status, output.exists()), (2, False) if refuses else (0, True), diagnostic)
                if refuses:
                    self.assertEqual(candidate_times, [start])
                    self.assertIn(command_line, diagnostic)
                else:
                    self.assertEqual(candidate_times, [45, 60, 75, 75, 75, 75] if args else [])

    def test_r0_rechecks_agents_at_baseline_close_later_admission_and_publication(self):
        import re
        from joulewise import agent_identity
        from joulewise.align import r0_runner
        from joulewise.measurement_liveness import census

        executable = "/Applications/Claude.app/Contents/MacOS/Claude"
        for mode in ("quiet", "baseline-close", "later-admission", "publication"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                required = Path(tmp).resolve() / "required"
                required.mkdir()
                guard, clock, _, _ = self.admission(busy=False)
                guard.inspect_custody = census
                normal = guard.run
                arrival = {"later-admission": 35, "publication": 40}.get(mode, float("inf"))
                queries, host_times, pass_saves = [], [], []
                closing_snapshot_returned = False

                def run(argv, **kwargs):
                    nonlocal closing_snapshot_returned
                    present = closing_snapshot_returned or clock.now >= arrival
                    if argv[0] == "/usr/bin/pgrep":
                        flags = "".join(argv[1:-1])
                        hit = present and re.search(argv[-1], executable, re.I if "i" in flags else 0)
                        queries.append((clock.now, bool(hit)))
                        return subprocess.CompletedProcess(argv, 0 if hit else 1, f"42 {executable}\n" if hit else "", "")
                    if argv == prewindow.PS_ARGV:
                        table = "1 0.0 /sbin/launchd\n" + (f"42 0.0 {executable}\n" if present else "")
                        if mode == "baseline-close" and clock.now == 30:
                            # The agent arrives after the closing sample and
                            # before the dedicated admission census.
                            closing_snapshot_returned = True
                        return subprocess.CompletedProcess(argv, 0, table, "")
                    return normal(argv, **kwargs)

                def host():
                    host_times.append(clock.now)
                    if mode == "later-admission":
                        clock.now = 40
                    return {"status": "pass"}

                save_report = r0_runner.save_report

                def save(output, report):
                    save_report(output, report)
                    if report["status"] == "pass":
                        pass_saves.append(clock.now)
                        if mode == "publication" and len(pass_saves) == 2:
                            clock.now = 40

                filter_census = agent_identity.filter_census
                info = agent_identity.ProcessInfo(42, 1, 42, executable, (executable,))
                guard.run = run
                with (patch.object(agent_identity, "filter_census",
                                   lambda stdout, **kwargs: filter_census(stdout, inspector=lambda _: info, **kwargs)),
                      patch.object(r0_runner, "save_report", side_effect=save)):
                    status, output, diagnostic = self.run_synthetic_host_cli(required, guard, host)
                if mode == "quiet":
                    self.assertEqual((status, output.exists()), (0, True))
                    self.assertTrue(all(not hit for _, hit in queries))
                else:
                    self.assertEqual((status, output.exists()), (2, False), diagnostic)
                    self.assertIn(executable, diagnostic)
                    self.assertEqual([at for at, hit in queries if hit], [30 if mode == "baseline-close" else 40])
                    self.assertEqual(host_times, [] if mode == "baseline-close" else [30])
                    private, = output.parent.glob(".output.r0-*")
                    self.assertEqual(json.loads((private / "report.json").read_text())["status"], "refused")

    def test_r0_baseline_flags_cpu_delta_of_worker_that_exits_mid_window(self):
        from joulewise.measurement_liveness import census

        for first, midpoint, last, flagged in (
                ("0:00.00", "0:01.80", None, True), ("0:05.00", "0:06.80", None, True),
                ("0:05.00", "0:06.20", None, False), ("0:05.00", "0:00.00", None, False),
                ("0:00.00", "0:01.80", "0:00.00", True), ("0:05.00", "0:06.80", "0:05.20", True),
                ("0:00.00", "0:01.80", "0:01.80", True)):
            with self.subTest(first=first, midpoint=midpoint, last=last), tempfile.TemporaryDirectory() as tmp:
                required = Path(tmp).resolve() / "required"
                required.mkdir()
                guard, clock, _, _ = self.admission(busy=False)
                guard.inspect_custody = census
                normal = guard.run
                samples = []

                def run(argv, **kwargs):
                    if argv == contention.PS_ARGV:
                        cpu = {0: first, 15: midpoint, 30: last}[clock.now]
                        samples.append(clock.now)
                        workers = [(42, OLD_START, cpu, "mdworker_shared")] if cpu is not None else []
                        return subprocess.CompletedProcess(argv, 0, cpu_table(*workers), "")
                    return normal(argv, **kwargs)

                guard.run = run
                status, output, diagnostic = self.run_synthetic_host_cli(required, guard, lambda: {"status": "pass"})
                self.assertEqual((status, output.exists()), (2, False) if flagged else (0, True), diagnostic)
                self.assertEqual(samples[:3], [0, 15, 30])
                self.assertTrue(all(at == 30 for at in samples[3:]))
                record = output if output.exists() else next(output.parent.glob(".output.r0-*"))
                report = json.loads((record / "report.json").read_text())
                self.assertEqual(report["contention"]["guard_flags"], int(flagged))
                if flagged:
                    event, = guard.contention_flags
                    evidence, = event["busy"]
                    self.assertAlmostEqual(evidence["cpu_s_per_s"], 0.06)
                    if last is None:
                        self.assertIn("lower bound", evidence["basis"])


    def run_background_census(self, configured, prepare, *, just_before_census=lambda: None):
        from joulewise import measurement_liveness as live

        guard, clock, advance, _ = self.admission(busy=False)
        command = guard.run

        def observe(pid):
            self.assertEqual(pid, 42)
            return live.Identity("LIVE", OLD_START)

        def run(argv, **kwargs):
            if clock.now == 45 and argv[0] == "/bin/launchctl":
                just_before_census()
            return command(argv, **kwargs)

        def host():
            prepare()
            advance(45)
            return {"status": "pass"}

        guard.run = run
        guard.inspect_custody = lambda **kwargs: live.census(**kwargs, observer=observe)
        status, output, diagnostic = self.run_synthetic_host_cli(configured, guard, host)
        return status, output.exists(), diagnostic

    def test_background_census_resolves_configured_alias_at_scan_time(self):
        import os

        for mode, reason in (("quiet", ""), ("removed", "errno 2"), ("retargeted", "live measurement owner")):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                work = Path(tmp).resolve()
                original, active, configured = (work / name for name in ("original", "active", "configured"))
                original.mkdir()
                night = active / "plan" / "night"
                night.mkdir(parents=True)
                (night / "chain.started").write_text(json.dumps({"pid": 42, "start_time": OLD_START}))
                configured.symlink_to(original, target_is_directory=True)

                def swap():
                    if mode != "quiet":
                        configured.unlink()
                    if mode == "retargeted":
                        configured.symlink_to(active, target_is_directory=True)

                with patch.object(os.path, "realpath", wraps=os.path.realpath) as resolve:
                    rc, published, diagnostic = self.run_background_census(
                        configured, lambda: None, just_before_census=swap)
                self.assertEqual((rc, published), (0, True) if mode == "quiet" else (2, False), diagnostic)
                self.assertIn(reason, diagnostic)
                configured_calls = [call for call in resolve.call_args_list if Path(call.args[0]) == configured]
                self.assertEqual([call.kwargs for call in configured_calls], [{"strict": True}] * (8 if mode == "quiet" else 5))

    def test_background_census_refuses_symlink_substituted_before_root_open(self):
        import os

        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp).resolve()
            configured, original, moved = (work / name for name in ("configured", "original", "moved"))
            original.mkdir()
            configured.symlink_to(original, target_is_directory=True)
            replaced = False
            ready = False
            open_path = os.open

            def before_open(path, flags, *, dir_fd=None):
                nonlocal replaced
                if Path(path) == original and ready and not replaced:
                    original.rename(moved)
                    original.symlink_to(moved, target_is_directory=True)
                    replaced = True
                    self.assertEqual(flags, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                return open_path(path, flags, dir_fd=dir_fd)

            def prepare():
                nonlocal ready
                ready = True

            with patch.object(os, "open", side_effect=before_open):
                rc, published, diagnostic = self.run_background_census(configured, prepare)
            self.assertTrue(replaced)
            self.assertEqual((rc, published), (2, False), diagnostic)
            self.assertIn(f"{original} (errno ", diagnostic)

    def test_background_census_keeps_open_root_when_its_path_is_replaced(self):
        import os

        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp).resolve()
            configured, original, moved = (work / name for name in ("configured", "original", "moved"))
            original.mkdir()
            configured.symlink_to(original, target_is_directory=True)
            root_stat = original.stat()
            swapped = False
            scandir = os.scandir

            def prepare():
                night = original / "plan" / "night"
                night.mkdir(parents=True)
                (night / "chain.started").write_text(json.dumps({"pid": 42, "start_time": OLD_START}))

            def swap_at_scan(value):
                nonlocal swapped
                if isinstance(value, int) and not swapped and (original / "plan").is_dir():
                    if os.path.samestat(os.fstat(value), root_stat):
                        original.rename(moved)
                        original.mkdir()
                        swapped = True
                return scandir(value)

            with patch.object(os, "scandir", side_effect=swap_at_scan):
                rc, published, diagnostic = self.run_background_census(configured, prepare)
            self.assertTrue(swapped, "the census must enumerate the held root descriptor")
            self.assertEqual((rc, published), (2, False), diagnostic)
            self.assertIn("live measurement owner", diagnostic)

    def test_background_census_matches_folded_names_and_refuses_collisions(self):
        import os

        for mode in ("night", "chain", "registry", "collision"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                configured = Path(tmp).resolve() / "configured"
                configured.mkdir()
                record = {"pid": 42, "start_time": OLD_START}
                night = configured / "plan" / ("Night" if mode == "night" else "night")

                def prepare():
                    if mode == "registry":
                        registry = configured / "Active-Campaigns"
                        registry.mkdir()
                        (registry / "worker.json").write_text(json.dumps({
                            **record, "schema": "joulewise.active_campaign.v1",
                            "nonce": "fixture", "runs_root": str(configured)}))
                    else:
                        night.mkdir(parents=True)
                        name = "CHAIN.STARTED" if mode == "chain" else "chain.started"
                        (night / name).write_text(json.dumps(record))

                if mode == "collision":
                    # Inject the two spellings as directory entries on either
                    # case-sensitive or case-insensitive test filesystems.
                    from contextlib import contextmanager
                    scandir = os.scandir

                    @contextmanager
                    def with_collision(value):
                        with scandir(value) as entries:
                            if night.is_dir() and (value == night or (isinstance(value, int)
                                    and os.path.samestat(os.fstat(value), night.stat()))):
                                yield iter([*entries, SimpleNamespace(name="CHAIN.STARTED")])
                            else:
                                yield entries

                    with patch.object(os, "scandir", side_effect=with_collision):
                        rc, published, diagnostic = self.run_background_census(configured, prepare)
                    expected = "case-folded name collision"
                else:
                    rc, published, diagnostic = self.run_background_census(configured, prepare)
                    expected = "live measurement owner"
                self.assertEqual((rc, published), (2, False), diagnostic)
                self.assertIn(expected, diagnostic)

    def test_census_filesystem_calls_are_confined_to_the_helper(self):
        import ast
        from joulewise import measurement_liveness
        from joulewise.align import r0_host

        raw = {
            "access", "exists", "expanduser", "fdopen", "fstat", "fwalk", "glob", "home", "iglob", "is_dir",
            "is_file", "is_symlink", "isdir", "isfile", "islink", "iterdir", "lexists",
            "listdir", "lstat", "open", "read", "read_bytes", "read_text", "readlink",
            "realpath", "resolve", "rglob", "samefile", "scandir", "stat", "walk",
        }
        filesystem_errors = {"OSError", "IOError", "FileNotFoundError", "NotADirectoryError", "PermissionError"}
        process_probes = {"observe_identity", "_pending_group_gone"}
        for module, include, exclude in (
                (measurement_liveness, None, {"census_fs", "publish_campaign", "remove_campaign"}),
                (r0_host, {"QuietGuard", "_installed_night_agents"}, set())):
            source = ast.parse(Path(module.__file__).read_text())
            aliases = {alias.asname or alias.name for node in source.body
                       if isinstance(node, ast.ImportFrom)
                       for alias in node.names if alias.name in raw} | {"open"}
            definitions = {node.name: node for node in source.body
                           if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
            remaining = set(definitions) - exclude if include is None else set(include)
            checked = set()
            while remaining:
                name = remaining.pop()
                checked.add(name)
                definition = definitions[name]
                for node in ast.walk(definition):
                    location = f"{module.__name__}:{node.lineno}" if hasattr(node, "lineno") else module.__name__
                    if isinstance(node, ast.Attribute):
                        self.assertNotIn(node.attr, raw, location)
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                        called = node.func.id
                        self.assertNotIn(called, aliases, location)
                        if called in definitions and called not in checked | exclude:
                            remaining.add(called)
                    if (isinstance(node, ast.ExceptHandler) and node.type is not None
                            and definition.name not in process_probes):
                        caught = {part.id for part in ast.walk(node.type) if isinstance(part, ast.Name)}
                        caught.update(part.attr for part in ast.walk(node.type) if isinstance(part, ast.Attribute))
                        self.assertFalse(caught & filesystem_errors, location)

    def test_full_r0_refuses_every_census_filesystem_call_fault(self):
        from contextlib import contextmanager, nullcontext, redirect_stderr, redirect_stdout
        import errno
        from io import StringIO
        import os
        from joulewise import measurement_liveness as live
        from joulewise.align import r0_runner
        from tests.align.test_r0_checks import FakeBackend, patch_references

        patch_references(self)
        (self.default_parent / "Library" / "LaunchAgents").mkdir(parents=True)
        path_operations = {"expanduser": "expanduser", "home": "home", "lstat": "lstat",
                           "list": "iterdir", "read": "read_text", "stat": "stat"}
        fd_operations = {"lstat": "lstat", "list": "scandir", "read": "open", "stat": "stat"}
        original = live.census_fs
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp).resolve()
            actual = work / "required"
            root = work / "configured-root"
            root.symlink_to(actual, target_is_directory=True)
            night = actual / "finished-plan" / "night"
            night.mkdir(parents=True)
            (night / "launch.pending").write_text("{}")
            (night / "chain.started").write_text("{}")
            (night / "chain.exited").write_text(json.dumps({"exit_code": 0, "epoch_s": 1, "monotonic_ns": 2}))
            open_night = actual / "dead-plan" / "night"
            open_night.mkdir(parents=True)
            (open_night / "chain.started").write_text(json.dumps({"pid": 41, "start_time": OLD_START}))
            (open_night / "launch.pending").write_text(json.dumps(
                {"pid": 43, "pgid": 43, "start_time": OLD_START}))
            registry = actual / "active-campaigns"
            registry.mkdir()
            entry = registry / "worker.json"
            entry.write_text(json.dumps({"schema": live.REGISTRY_SCHEMA, "pid": 42,
                                         "nonce": "fixture", "runs_root": str(work), "start_time": None}))
            os.utime(entry, (1, 1))
            extra = work / "extra"
            extra.mkdir()
            for name in ("D", "anchor"):
                model = work / name
                model.mkdir()
                (model / "weight").write_bytes(b"synthetic model")
            config = config_at(work)
            config["custody_parents"] = [str(root)]
            config_file = work / "config.json"
            config_file.write_text(json.dumps(config))

            def observer(pid):
                return live.Identity("LIVE", OLD_START) if pid == 42 else live.Identity("DEAD")

            def run(target=None, number=None, *, inventory_mode=False, readlink=False):
                trace = []
                stdout, stderr = StringIO(), StringIO()
                output = work / "output"
                guard, _, advance, _ = self.admission(busy=False)
                guard.parents = [root]
                guard.inspect_custody = lambda **kw: live.census(**kw, observer=observer)

                def host():
                    advance(45)
                    return {"status": "pass"}

                def smc(repo, directory, profile):
                    self.assertFalse(output.exists())
                    directory.mkdir()
                    (directory / "fixture").write_text("synthetic SMC artifact")
                    rejected = directory.with_name("smc.rejected1")
                    rejected.mkdir()
                    return {"status": "pass", "contention_redo": [{"output_dir": str(rejected)}]}

                def inject(path, operation, *, dir_fd=None):
                    trace.append((path, operation))
                    if len(trace) != target:
                        return original(path, operation, dir_fd=dir_fd)
                    error = OSError(number, "synthetic census operation failed", str(path))
                    if operation == "directory":
                        @contextmanager
                        def failed_directory():
                            with patch.object(os, "open", side_effect=error):
                                with original(path, operation, dir_fd=dir_fd) as fd:
                                    yield fd
                        return failed_directory()
                    if readlink:
                        # Exercise the nested syscall inside strict resolution.
                        read = os.readlink
                        def fail_readlink(value, *args, **kwargs):
                            if Path(value) == root:
                                raise error
                            return read(value, *args, **kwargs)
                        with patch.object(os, "readlink", fail_readlink):
                            return original(path, operation)
                    if operation == "resolve":
                        module, name = os.path, "realpath"
                    elif dir_fd is not None:
                        module, name = os, fd_operations[operation]
                    else:
                        module, name = Path, path_operations[operation]
                    with patch.object(module, name, side_effect=error):
                        return original(path, operation, dir_fd=dir_fd)

                args = ["--config", str(config_file), "--output", str(output)]
                if inventory_mode:
                    args += ["--inventory", str(work / "D")]
                # The quiet control exercises real report serialization.
                # Fault trials assert the CLI verdict and the public path.
                save_report = r0_runner.save_report if target is None else lambda *_: None
                try:
                    with (patch.object(live, "census_fs", inject),
                          patch.object(r0_runner, "save_report", save_report),
                          patch.object(r0_runner, "host_snapshot", side_effect=host),
                          patch.object(r0_runner, "host_identity", return_value={"status": "pass"}),
                          patch.object(r0_runner, "smc_enumeration", side_effect=smc),
                          patch.object(r0_runner, "deadline", return_value=nullcontext()),
                          patch.object(r0_runner, "command", return_value="synthetic-head"),
                          patch.object(r0_runner, "softwareupdate_scan_forecast", return_value={"status": "unknown"}),
                          patch("shutil.disk_usage", return_value=SimpleNamespace(free=66_000_000_000)),
                          patch.object(os, "killpg", side_effect=ProcessLookupError()),
                          redirect_stderr(stderr), redirect_stdout(stdout)):
                        status = r0_runner.main(args, backend_factory=FakeBackend, guard_factory=lambda _: guard,
                                                display_probe=None, lock_path=work / "lock")
                    if target is None:
                        self.assertEqual(status, 0, stderr.getvalue())
                        if not inventory_mode:
                            published = json.loads((output / "report.json").read_text())
                            self.assertEqual(published["status"], "pass")
                            self.assertEqual(published["selected_checks"][0], "smc")
                            self.assertEqual(set(published["selected_checks"]), set(r0_runner.CHECKS))
                            self.assertTrue((output / "smc" / "fixture").is_file())
                            rejected = published["checks"][0]["contention_redo"][0]["output_dir"]
                            self.assertEqual(Path(rejected), output / "smc.rejected1")
                            self.assertTrue(Path(rejected).is_dir())
                            self.assertTrue(any(row.get("background_census") for row in published["census"]))
                    else:
                        self.assertEqual(status, 2, stderr.getvalue())
                        path, _ = trace[target - 1]
                        self.assertIn(f"{path} (errno {number})", stderr.getvalue())
                        self.assertFalse(output.exists())
                        self.assertNotIn("pass:", stdout.getvalue())
                    return trace
                finally:
                    guard.close()
                    if target is None and output.exists():
                        output.rename(work / ("inventory-control" if inventory_mode else "report-control"))

            with patch.dict("os.environ", {live.ADDITIONAL_PARENTS_ENV: json.dumps([str(extra)])}):
                full_trace = run()
                self.assertEqual({op for _, op in full_trace}, set(path_operations) | {"directory", "resolve"})
                for target, (path, operation) in enumerate(full_trace, 1):
                    for number in (errno.EIO, errno.ENOENT, errno.EACCES):
                        with self.subTest(call=target, operation=operation, error=number):
                            run(target, number, readlink=path == root and operation == "resolve")
                inventory_trace = run(inventory_mode=True)
                for target, (path, operation) in enumerate(inventory_trace, 1):
                    for number in (errno.EIO, errno.ENOENT, errno.EACCES):
                        with self.subTest(inventory_call=target, operation=operation, error=number):
                            run(target, number, inventory_mode=True,
                                readlink=path == root and operation == "resolve")


class R0PublicationAuditTest(unittest.TestCase):
    def trial(self, case, *, publication_delay=0, probe_delay=0, command=None, wall_offset_ns=0):
        from datetime import datetime
        from joulewise.align import r0_runner
        from tests.align import test_r0_vs_l3_differential as fixture

        class LocalPsTime(datetime):
            @classmethod
            def fromtimestamp(cls, value, tz=None):
                # The frozen worker sets TZ=UTC. Here ps and the parser
                # must agree on the current process's local timezone.
                return super().fromtimestamp(value)

        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp).resolve()
            root = work / "trial"
            root.mkdir()
            provenance = work / "provenance"
            for name in ("joulewise/align/r0_host.py", "joulewise/align/r0_mlx.py",
                         "joulewise/align/r0_step.py", "scripts/align_r0_checks.py",
                         r0_runner.LOAD_REFERENCE_NOTE, "reference.json"):
                path = provenance / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("synthetic provenance\n")

            def move(model, end):
                if model.phase == "publication" and end == 58:
                    end += publication_delay
                return original_move(model, end)

            def run(model, argv, **kwargs):
                if probe_delay and model.phase == "publication" and argv[0] == "/bin/launchctl":
                    original_move(model, 58 + probe_delay)
                if command is not None:
                    return command(original_run, model, argv, **kwargs)
                return original_run(model, argv, **kwargs)

            def wall(model):
                return original_wall(model) + wall_offset_ns

            original_move, original_run = fixture.Fixture.move, fixture.Fixture.run
            original_wall = fixture.Fixture.wall_ns
            with (patch.object(fixture, "datetime", LocalPsTime), patch.object(fixture.Fixture, "move", move),
                  patch.object(fixture.Fixture, "run", run), patch.object(fixture.Fixture, "wall_ns", wall)):
                return fixture.run_case(case, root, provenance, oracle=False)

    def assert_withheld(self, result):
        self.assertEqual((result["rc"], result["status"], result["published"]), (2, "refused", False), result)

    def test_publication_refuses_stale_background_samples(self):
        from tests.align import test_r0_vs_l3_differential as fixture

        quiet = fixture.Case("quiet", schedule="multi", end=56)
        self.assertEqual(self.trial(quiet)["rc"], 0)
        transient = fixture.Case("transient_agent", (fixture.Process(fixture.CLAUDE, 60, 110),),
                                 schedule="multi", end=56)
        for case, delays in ((quiet, {"publication_delay": 60}),
                             (transient, {"publication_delay": 60}), (quiet, {"probe_delay": 60})):
            with self.subTest(case=case.name, **delays):
                result = self.trial(case, **delays)
                self.assert_withheld(result)
                self.assertIn("background snapshots stalled", result["reason"])

    def test_baseline_snapshot_refuses_agent_or_chain_that_leaves_before_admission(self):
        from tests.align import test_r0_vs_l3_differential as fixture

        for command in (fixture.CLAUDE, fixture.APP, fixture.CHAIN, f"/bin/echo {fixture.APP}"):
            with self.subTest(command=command):
                case = fixture.Case("baseline_mid", (fixture.Process(command, 10, 20),), schedule="multi", end=56)
                result = self.trial(case)
                if command.startswith("/bin/echo"):
                    self.assertEqual(result["rc"], 0, result)
                else:
                    self.assert_withheld(result)
                    self.assertEqual(result["work_started"], [])
                    self.assertEqual(result["refused_at"], 15)

    def test_background_window_keeps_contender_seen_only_at_caller_admission(self):
        from tests.align import test_r0_vs_l3_differential as fixture

        for gone in (41, 47):
            with self.subTest(gone=gone):
                process = fixture.Process(fixture.WORKER, 34, gone, 40, 180)
                case = fixture.Case("observed_worker", (process,), schedule="multi", end=56)
                result = self.trial(case)
                self.assert_withheld(result)
                self.assertTrue(any(flag[:3] == (15.0, 45.0, fixture.PID) for flag in result["flags"]), result)
                self.assertIn((15.0, 45.0), result["report_intervals"])

    def test_midpoint_accounting_refuses_agent_that_exits_before_args_read(self):
        from tests.align import test_r0_vs_l3_differential as fixture

        for command in (fixture.CLAUDE, "/Applications/Codex.app/Contents/MacOS/CoDeX"):
            with self.subTest(command=command):
                queries = []

                def run(original, model, argv, **kwargs):
                    if 15 <= model.now < 16:
                        queries.append(tuple(argv))
                        if tuple(argv) == prewindow.PS_ARGV:
                            model.now = 15.25
                    return original(model, argv, **kwargs)

                process = fixture.Process(command, 10, 15.125, 15, 180)
                case = fixture.Case("accounting_only_agent", (process,), schedule="multi", end=56)
                result = self.trial(case, command=run)
                self.assert_withheld(result)
                self.assertEqual(result["work_started"], [])
                self.assertEqual(result["refused_at"], 15)
                self.assertEqual(queries, [contention.PS_ARGV])

    def test_args_and_pgrep_agent_sightings_do_not_query_process_identity(self):
        from joulewise.align.r0_host import R0_AGENT_CENSUS_ARGV
        from tests.align import test_r0_vs_l3_differential as fixture

        for source in (prewindow.PS_ARGV, R0_AGENT_CENSUS_ARGV):
            with self.subTest(source=source):
                inspected = []
                original_identity = fixture.Fixture.identity

                def identity(model, pid):
                    inspected.append(pid)
                    return original_identity(model, pid)

                def run(original, model, argv, **kwargs):
                    if tuple(argv) != source:
                        return original(model, argv, **kwargs)
                    if source == prewindow.PS_ARGV and model.now == 15:
                        # The process is absent from the accounting sample.
                        model.now = 15.125
                    result = original(model, argv, **kwargs)
                    if any(line.startswith(f"{fixture.PID} ") for line in result.stdout.splitlines()):
                        # The recorded agent exits before any identity read.
                        model.now = 15.25
                    return result

                born = 15.125 if source == prewindow.PS_ARGV else 0
                agent = fixture.Process("/Applications/Claude.app/Contents/MacOS/ClAuDe", born, 15.25)
                case = fixture.Case("transient_agent_in_args", (agent,), schedule="multi", end=56)
                with patch.object(fixture.Fixture, "identity", identity):
                    result = self.trial(case, command=run)
                self.assert_withheld(result)
                self.assertEqual(result["work_started"], [])
                self.assertNotIn(fixture.PID, inspected)

    def test_background_cpu_table_refuses_measurement_chain_before_args_read(self):
        from tests.align import test_r0_vs_l3_differential as fixture

        for gone in (46.5, 48):
            with self.subTest(gone=gone):
                reads = []

                def run(original, model, argv, **kwargs):
                    if 45 <= model.now < 48:
                        if tuple(argv) == contention.PS_ARGV:
                            model.now = 46
                        elif tuple(argv) == prewindow.PS_ARGV and model.now >= 46:
                            model.now = 47
                        reads.append((model.now, tuple(argv)))
                    return original(model, argv, **kwargs)

                probe = fixture.Process("/usr/bin/powermetrics", 45.125, gone, 46, 20)
                case = fixture.Case("sampled_chain", (probe,), schedule="multi", end=56)
                result = self.trial(case, command=run)
                self.assert_withheld(result)
                self.assertIn("powermetrics", result["reason"])
                self.assertIn((46, contention.PS_ARGV), reads)
                self.assertNotIn((47, prewindow.PS_ARGV), reads)

    def test_every_census_name_refuses_from_any_process_table_without_confirmation(self):
        from itertools import product
        from joulewise.align.r0_host import R0_AGENT_CENSUS_ARGV
        from tests.align import test_r0_vs_l3_differential as fixture

        names = (
            "/usr/local/bin/ClAuDe", "/Applications/Codex.app/Contents/MacOS/CoDeX",
            "/usr/bin/PoWeRmEtRiCs", "/synthetic/run_campaign.py", "/synthetic/run_night.zsh",
            "/synthetic/window-chain", "/synthetic/window_chain", "/synthetic/align_r1_rehearsal.py",
            "/synthetic/align_r0_checks.py", "/synthetic/run_b5_analysis.py", "/synthetic/chain.sh",
        )
        for command, source in product(names, ("accounting", "census_ps", "cpu_args", "agent_query")):
            with self.subTest(command=command, source=source):
                reads = []
                inspected = []
                accounting_started = False
                original_identity = fixture.Fixture.identity

                def identity(model, pid):
                    inspected.append(pid)
                    return original_identity(model, pid)

                def run(original, model, argv, **kwargs):
                    nonlocal accounting_started
                    if tuple(argv) == contention.PS_ARGV:
                        accounting_started = True
                        table = "accounting"
                    elif tuple(argv) == prewindow.PS_ARGV:
                        table = "cpu_args" if accounting_started else "census_ps"
                    elif tuple(argv) == R0_AGENT_CENSUS_ARGV:
                        table = "agent_query"
                    else:
                        table = "other"
                    if reads or table != source:
                        if reads:
                            reads.append(table)
                        return original(model, argv, **kwargs)
                    reads.append(table)
                    if table == "agent_query":
                        return subprocess.CompletedProcess(argv, 0, f"{fixture.PID} {command}\n", "")
                    row = fixture.Process(command).row(model.now)
                    # Only this returned table contains the process. No later
                    # table or live identity lookup can observe it again.
                    with patch.object(model, "processes", return_value=[*model.processes(), row]):
                        return original(model, argv, **kwargs)

                case = fixture.Case("single_process_sighting", schedule="multi", end=56)
                with patch.object(fixture.Fixture, "identity", identity):
                    result = self.trial(case, command=run)
                self.assert_withheld(result)
                self.assertEqual(result["work_started"], [])
                self.assertIn(Path(command).name, result["reason"])
                self.assertEqual(reads, [source])
                self.assertNotIn(fixture.PID, inspected)

    def test_single_sighting_of_exited_worker_counts_at_either_side_of_birth_tick(self):
        from tests.align import test_r0_vs_l3_differential as fixture

        for born, centiseconds, busy in ((0.1, 180, True), (1.1, 180, True), (0.1, 140, False)):
            with self.subTest(born=born, centiseconds=centiseconds):
                worker = fixture.Process(fixture.WORKER, born, 20, 15, centiseconds)
                case = fixture.Case("single_worker_sighting", (worker,), schedule="multi", end=56)
                result = self.trial(case, wall_offset_ns=1_000_000)
                if busy:
                    self.assert_withheld(result)
                    self.assertTrue(any(flag[:3] == (0.0, 30.0, fixture.PID) for flag in result["flags"]), result)
                else:
                    self.assertEqual((result["rc"], result["published"], result["flags"]), (0, True, []), result)

    def test_exited_worker_retains_measured_growth_across_fractional_window_open(self):
        from tests.align import test_r0_vs_l3_differential as fixture

        # At the 15.500 opening, the 15.1 birth is displayed by ps as
        # 15.000. The entry then grows from 0 at 32 s to 1.80 CPU-s at 40 s
        # before disappearing before the 45.500 closing sample.
        for born, cpu_at in ((15.1, 40), (16.1, 40), (15.1, 30)):
            with self.subTest(born=born, cpu_at=cpu_at):
                process = fixture.Process(fixture.WORKER, born, 44.5, cpu_at, 180)
                case = fixture.Case("fractional_open", (process,), schedule="multi", end=56)
                result = self.trial(case, wall_offset_ns=500_000_000)
                self.assert_withheld(result)
                self.assertTrue(any(flag[:3] == (15.0, 45.0, fixture.PID) for flag in result["flags"]), result)
                if cpu_at == 30:
                    # CPU from this lifetime also overlaps the earlier window.
                    self.assertTrue(any(flag[:3] == (0.0, 30.0, fixture.PID) for flag in result["flags"]), result)

    def test_worker_still_present_at_close_retains_growth_after_missing_open_sample(self):
        from tests.align import test_r0_vs_l3_differential as fixture

        def run(original, model, argv, **kwargs):
            result = original(model, argv, **kwargs)
            if tuple(argv) == contention.PS_ARGV and model.now == 15:
                result.stdout = "".join(line for line in result.stdout.splitlines(keepends=True)
                                        if not line.startswith(f"{fixture.PID} "))
            return result

        worker = fixture.Process(fixture.WORKER, 14.1, 46.5, 40, 180)
        case = fixture.Case("worker_missed_at_fractional_open", (worker,), schedule="multi", end=56)
        result = self.trial(case, command=run, wall_offset_ns=500_000_000)
        self.assert_withheld(result)
        self.assertTrue(any(flag[:3] == (15.0, 45.0, fixture.PID) for flag in result["flags"]), result)


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
        first unless ``mid_baseline`` gives it. Caller admissions see the
        latest table without advancing the daemon's fixture schedule."""
        import threading

        clock = clock or GuardClock()
        snapshots = list(snapshots)
        if snapshots:
            snapshots.insert(1, snapshots[0] if mid_baseline is None else mid_baseline)
        samples = iter(snapshots)
        calls = []
        latest = None
        sampling = threading.local()

        def run(argv, **kwargs):
            nonlocal latest
            if argv == contention.PS_ARGV:
                self.assertEqual(kwargs["env"]["LC_ALL"], "C")
                self.assertEqual(kwargs["timeout"], contention.PROBE_TIMEOUT_S)
                if not sampling.admission:
                    calls.append(clock())
                    latest = next(samples)
                sample = latest
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
        class FixtureGuard(QuietGuard):
            def _cpu_snapshot(self, *, census_summary=None, admission=False):
                sampling.admission = admission
                return super()._cpu_snapshot(census_summary=census_summary, admission=admission)

        class DrivenGuard(FixtureGuard):
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
        guard_type = DrivenGuard if driven else FixtureGuard
        guard = guard_type([], run=run, inspect_custody=lambda **kw: Census(),
                           clock=clock, sleep=clock.sleep, host_reader=None)
        # The real daemon thread never fires during a test; ticks are driven.
        guard.SNAPSHOT_CADENCE_S = 3600
        self.addCleanup(guard.close)
        return guard, clock, calls

    def assert_flagged(self, guard, pattern):
        """R0-L3: contaminant contention is a receipt flag, never a refusal."""
        guard.check(force=True)
        self.assertRegex(guard.receipts[-1]["contention_flag"], pattern)
        self.assertRegex(guard.contention_flags[-1]["flag"], pattern)
        self.assertIsNone(guard.failure)

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
        for cpu, rate, flags in (("0:01.80", 0.06, True), ("0:01.20", 0.04, False)):
            with self.subTest(rate=rate):
                guard, clock, calls = self.guard([
                    cpu_table((42, OLD_START, "0:00.00", "mdworker_shared")),
                    cpu_table((42, OLD_START, cpu, "mdworker_shared"))])
                if flags:
                    self.assert_flagged(guard, "42 mdworker_shared 0.06 CPU-s/s")
                else:
                    guard.check(force=True)
                    self.assertNotIn("contention_flag", guard.receipts[-1])
                    self.assertEqual(guard.contention_flags, [])
                self.assertEqual(len(calls), 3)  # 0 s, mid-baseline 15 s, 30 s
                self.assertGreaterEqual(calls[2] - calls[0], prewindow.INTERVAL_S)
                self.assertEqual(clock.sleeps, [prewindow.INTERVAL_S / 2] * 2)
                interval = guard.receipts[-1]["cpu_interval"]
                self.assertGreaterEqual(interval["elapsed_s"], prewindow.INTERVAL_S)
                self.assert_rate(interval["contaminants"][0]["cpu_s_per_s"], rate, interval["elapsed_s"])

    def test_r0l3_flagged_contention_never_latches_and_census_refusals_still_refuse(self):
        guard, clock, _ = self.guard([
            cpu_table((42, OLD_START, "0:00.00", "softwareupdated")),
            cpu_table((42, OLD_START, "0:02.10", "softwareupdated")),
            cpu_table((42, OLD_START, "0:02.10", "softwareupdated"))])
        # Synthetic 0.07 CPU-s/s softwareupdated scan.
        self.assert_flagged(guard, "42 softwareupdated 0.07 CPU-s/s")
        clock.now = 60
        guard.check(force=True)  # the next quiet interval passes: no latch
        self.assertNotIn("contention_flag", guard.receipts[-1])
        agents = self.default_parent / "Library/LaunchAgents"
        agents.mkdir(parents=True)
        (agents / "com.joulewise.night.plist").write_text("armed")
        with self.assertRaisesRegex(Refused, "measurement window armed"):
            guard.check(force=True)

    def test_burst_above_interval_budget_is_flagged(self):
        # 1.60 CPU-s exceeds 0.05 * 30 = 1.50 by ten TIME quanta.
        guard, _, _ = self.guard([cpu_table(), cpu_table((42, NEW_START, "0:01.60", "photoanalysisd"))])
        from datetime import datetime
        with patch("joulewise.align.r0_host.time.time_ns",
                   return_value=int(datetime(2026, 11, 6, 18, 5, 15).timestamp() * 1e9)):
            self.assert_flagged(guard, "photoanalysisd.*CPU-s/s")

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
                    if refuses:  # R0-L3: flagged, not refused
                        self.assert_flagged(guard, "mdworker_shared.*CPU-s/s")
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
                if refuses:  # R0-L3: flagged, not refused
                    self.assert_flagged(guard, "python.*CPU-s/s")
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
        # Exercise accounting directly to prove the retained exit rule.
        guard, clock, _ = self.guard([
            cpu_table((42, OLD_START, "0:00.00", "mdworker_shared")),
            cpu_table((42, OLD_START, "0:01.80", "mdworker_shared")), cpu_table()])
        self.assert_flagged(guard, "mdworker_shared")
        clock.now = 60
        receipt = {}
        busy = guard._cpu_interval(receipt)
        self.assertEqual(busy[0]["pid"], 42)
        self.assertIn("previous interval", busy[0]["basis"])
        self.assert_rate(busy[0]["cpu_s_per_s"], 0.06, 30)

    def test_exit_delta_replaces_previous_interval_evidence_for_same_worker(self):
        guard, clock, _ = self.guard([
            cpu_table((42, OLD_START, "0:00.00", "mdworker_shared")),
            cpu_table((42, OLD_START, "0:01.80", "mdworker_shared")),
            cpu_table((42, OLD_START, "0:03.90", "mdworker_shared")),
            cpu_table(),
        ], driven=False)
        guard.check(force=True)
        self.tick(guard, clock, 45, 60)
        guard.check(force=True)
        interval = guard.receipts[-1]["cpu_intervals"][-1]
        evidence, = interval["exited_over_limit"]
        self.assertIn("opening counter", evidence["basis"])
        self.assertAlmostEqual(evidence["cpu_s_per_s"], 0.07)
        self.assertEqual(guard.contention_flags[-1]["busy"], [evidence])

    def test_lower_opening_counter_cannot_recount_cpu_in_a_later_window(self):
        snapshots = [cpu_table((42, OLD_START, cpu, "mdworker_shared"))
                     for cpu in ("0:05.00", "0:06.80", "0:00.00", "0:01.80", "0:01.80")]
        guard, clock, _ = self.guard(snapshots, driven=False)
        guard.check(force=True)
        self.tick(guard, clock, 45, 60, 75)
        guard.check(force=True)
        self.assertEqual(guard.receipts[-1]["cpu_interval"]["start_monotonic_s"], 45)
        final, = [flag for flag in guard.contention_flags if flag["interval"]["end_monotonic_s"] == 75]
        self.assertEqual(final["interval"]["start_monotonic_s"], 30)
        self.assertIn("previous interval", final["busy"][0]["basis"])

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
                if refuses:  # R0-L3: flagged, not refused
                    self.assert_flagged(guard, "43 mdworker_shared.*CPU-s/s")
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

    def test_contaminant_regression_with_previous_over_limit_is_still_flagged(self):
        # (0.05 + 0.01) * 30 = 1.80 CPU-s, then TIME -> zero. Under R0-L3
        # the next public check judges the regressed interval and flags it.
        guard, clock, _ = self.guard([
            cpu_table((42, OLD_START, "0:00.00", "mdworker_shared")),
            cpu_table((42, OLD_START, "0:01.80", "mdworker_shared")),
            cpu_table((42, OLD_START, "0:00.00", "mdworker_shared"))])
        self.assert_flagged(guard, "mdworker_shared 0.06 CPU-s/s")
        clock.now += prewindow.INTERVAL_S
        self.assert_flagged(guard, "42 mdworker_shared")
        interval = guard.receipts[-1]["cpu_interval"]
        self.assertEqual(interval["exited_over_limit"][0]["pid"], 42)
        self.assertTrue(interval["regressed_counters"][0]["contaminant"])
        self.assertEqual(len(guard.contention_flags), 2)

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

    def test_300_second_caller_gap_daemon_thread_flags_60_second_contender(self):
        # Cold review should-fix 1: a 60 s synthetic burst during a 300 s
        # caller gap. The daemon snapshots through the gap so the next
        # check can flag the burst in 30 s windows.
        def counter(t):
            return min(max(t - 120, 0), 60) * 0.2
        guard, clock, reached, ps_threads = self.threaded(counter, until=330)
        guard.check(force=True)
        self.assertTrue(reached.wait(2), "daemon did not reach the end of the caller gap")
        self.assertEqual(clock.now, 330)
        self.assert_flagged(guard, "42 mdworker_shared 0.1 CPU-s/s")
        windows = guard.receipts[-1]["cpu_intervals"]
        self.assertLessEqual(max(w["elapsed_s"] for w in windows),
                             prewindow.INTERVAL_S + QuietGuard.SNAPSHOT_CADENCE_S)
        # The caller only sampled at baseline and the next admission, while
        # the daemon sampled throughout the gap.
        self.assertEqual(ps_threads.count("joulewise-quiet-snapshots"), 20)
        self.assertEqual(len(ps_threads), 24)
        self.assertEqual(clock.sleeps, [prewindow.INTERVAL_S / 2] * 2)

    def test_calls_29_seconds_apart_flag_a_2_cpu_second_burst(self):
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
        self.assert_flagged(guard, "42 mdworker_shared 0.0666667 CPU-s/s")
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

    def test_caller_repeats_full_census_at_admission_boundaries(self):
        guard, clock, calls = self.guard([cpu_table()] * 4, driven=False)
        guard.check(force=True)
        guard.sleep = lambda seconds: self.fail("caller slept after admission")
        self.tick(guard, clock, 45)
        run = guard.run
        admissions = []

        def record_census(argv, **kwargs):
            if argv[0] == "/bin/launchctl":
                admissions.append(clock.now)
            return run(argv, **kwargs)

        guard.run = record_census
        # Per-token checks, forced boundaries and windows judged on stored data.
        for step in range(1, 200):
            clock.now = 45 + step * 0.05
            guard.check(force=step % 50 == 0)
        guard.run = run
        self.tick(guard, clock, 60)
        guard.run = record_census
        clock.now = 61
        guard.check(force=True)
        self.assertEqual(guard.receipts[-1]["cpu_interval"]["end_monotonic_s"], 60)
        self.assertEqual(guard.receipts[-1]["background_snapshots_monotonic_s"], [60])
        self.assertEqual(len(calls), 5)  # 3 admission + 2 daemon
        self.assertEqual(admissions, [45.05, 47.5, 50, 52.5, 61])

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
        clock.now = 30 + 50
        guard.check(force=True)  # the stall bound is inclusive
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
        self.assert_flagged(guard, "42 mdworker_shared 0.0666667 CPU-s/s")
        window = guard.receipts[-1]["cpu_intervals"][-1]
        self.assertEqual((window["start_monotonic_s"], window["end_monotonic_s"]), (15, 45))

    def test_background_census_summary_is_receipted_per_cycle(self):
        # Cold MEDIUM-3: what each daemon census saw reaches the next receipt.
        from joulewise.measurement_liveness import census

        guard, clock, _ = self.guard([cpu_table()] * 4, driven=False,
                                     diagnostic="77 9.0 /System/Library/mdworker_shared\n")
        guard.inspect_custody = census
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
        guard, clock, _ = self.guard([cpu_table(), cpu_table(), cpu_table()], driven=False)
        guard.check(force=True)
        self.assertTrue(guard._sampler.is_alive())
        self.tick(guard, clock, 90)
        with self.assertRaisesRegex(Refused, "judged CPU window"):
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
        self.addCleanup(guard.close)
        self.assert_flagged(guard, "0.06 CPU-s/s")
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
            self.assert_flagged(guard, "python.*CPU-s/s")
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
            self.assert_flagged(guard, "mdworker_shared 0.06 CPU-s/s")
        self.assertNotIn("missed by the first snapshot",
                         [row["reason"] for row in guard.receipts[-1]["cpu_interval"]["unaccounted"]])


if __name__ == "__main__":
    unittest.main()
