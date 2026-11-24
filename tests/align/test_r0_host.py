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


def rule_flags(guard):
    """Flags of the sliding rule windows (R0-L3): not the exact 30 s check, not the wall clock."""
    return [flag for flag in guard.contention_flags if flag.get("kind") is None]


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
            self.assertEqual(result["predicted"], ["2026-11-07T05:09:00+00:00", "2026-11-07T11:09:00+00:00"])
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
            self.assertEqual(result["last_finished"], "2026-11-07T12:45:00+00:00")
            self.assertEqual(result["predicted"], ["2026-11-07T18:45:00+00:00"])
            self.assertEqual(result["window"], ["2026-11-07T06:00:00+00:00", "2026-11-07T20:00:00+00:00"])
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
                             "2026-11-07T12:45:00+00:00")

    def test_softwareupdate_forecast_accepts_whitespace_before_the_offset(self):
        # Audit r3 compare_forecast.py: "04:45:00 -0800" was read as UTC and
        # forecast 16:45 UTC instead of 18:45 UTC.
        from datetime import datetime
        start, deadline = datetime(2026, 11, 7, 6, 0), datetime(2026, 11, 7, 20, 0)
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "install.log"
            for stamp in ("2026-11-07 04:45:00-0800", "2026-11-07 04:45:00 -0800", "2026-11-07 04:45:00  -08:00",
                          "2026-11-07T04:45:00\t-08", "2026-11-07 12:45:00 Z", "2026-11-07 12:45:00 +0000"):
                with self.subTest(stamp=stamp):
                    log.write_text(f"{stamp} host softwareupdated[1635]: softwareupdated: Posting "
                                   "com.apple.softwareupdate.AutoBackgroundScanFinished notification\n")
                    result = softwareupdate_scan_forecast(start, deadline, log_path=log)
                    self.assertEqual((result["status"], result["last_finished"], result["predicted"]),
                                     ("forecast", "2026-11-07T12:45:00+00:00", ["2026-11-07T18:45:00+00:00"]))

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
        self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in rule_flags(guard)],
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
        self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in rule_flags(guard)],
                         [45, 60])
        self.assertEqual(launchctl_at, [0, 30, 45, 60, 75, 90, 90])
        self.assertIsNone(guard.failure)

    def test_invalid_background_census_still_refuses_after_contention(self):
        guard, _, advance, _ = self.admission()
        guard.check(force=True)
        advance(45)
        guard.check(force=True)
        self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in rule_flags(guard)], [45])
        advance(60, census_ok=False)
        with self.assertRaisesRegex(Refused, "background sampler: .*LaunchAgent census indeterminate"):
            guard.check()
        self.assertIn("LaunchAgent census indeterminate", guard.receipts[-1]["refusal"])

    def test_stalled_sampler_still_refuses_after_contention(self):
        guard, clock, advance, _ = self.admission()
        guard.check(force=True)
        advance(45)
        guard.check(force=True)
        self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in rule_flags(guard)], [45])
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
                self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in rule_flags(guard)],
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
                # The exact 30 s check adds its own flags; the rule windows are these.
                self.assertEqual(report["contention"]["guard_flags"], len(guard.contention_flags))
                self.assertEqual(len(rule_flags(guard)), expected_flags)
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
                                      for flag in row.get("contention_flags", ()) if flag.get("kind") is None], [45])
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
                self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in rule_flags(guard)], [45])
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
        self.assertEqual(published["contention"]["guard_flags"], len(guard.contention_flags))
        self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in row["contention_flags"]
                          if flag.get("kind") is None], [45])

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
        from datetime import datetime, timezone

        # The 30 s table proves absence for both printed birth times.
        for birth, cpu, flagged in ((35, "0:01.80", [45, 60]),
                                    (20, "0:01.80", [45, 60]),
                                    (35, "0:00.50", [])):
            with self.subTest(birth=birth, cpu=cpu), tempfile.TemporaryDirectory() as tmp:
                guard, clock, advance, _ = self.admission()
                run = guard.run
                wall = datetime(2026, 11, 6, 18, 0, tzinfo=timezone.utc).timestamp()
                guard.wall_clock_ns = lambda: int((wall + clock.now) * 1e9)

                def command(argv, **kwargs):
                    if argv == prewindow.PS_ARGV and clock.now == 45:
                        return subprocess.CompletedProcess(argv, 0, "1 0.0 /sbin/launchd\n42 0.0 mdworker_shared\n", "")
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
                self.assertEqual([flag["interval"]["end_monotonic_s"] for flag in rule_flags(guard)], flagged)
                if 60 in flagged:
                    evidence = rule_flags(guard)[-1]["busy"][0]
                    self.assertAlmostEqual(evidence["cpu_s_per_s"], 1.8 / (60 - max(30, birth)))
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
                    if argv == prewindow.PS_ARGV:
                        present = {0: first, 15: midpoint, 30: last}[clock.now] is not None
                        args = "1 0.0 /sbin/launchd\n" + ("42 0.0 mdworker_shared\n" if present else "")
                        return subprocess.CompletedProcess(argv, 0, args, "")
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
                self.assertEqual(report["contention"]["guard_flags"], len(guard.contention_flags))
                self.assertEqual(len(rule_flags(guard)), int(flagged))
                if flagged:
                    event, = rule_flags(guard)
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
    def trial(self, case, *, publication_delay=0, probe_delay=0, command=None, wall_offset_ns=0, factory=None):
        from joulewise.align import r0_runner
        from tests.align import test_r0_vs_l3_differential as fixture

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
            with (patch.object(fixture.Fixture, "move", move),
                  patch.object(fixture.Fixture, "run", run), patch.object(fixture.Fixture, "wall_ns", wall)):
                if factory is None:
                    return fixture.run_case(case, root, provenance, oracle=False)
                return fixture.run_case(case, root, provenance, oracle=False, fixture_factory=factory)

    def assert_withheld(self, result):
        self.assertEqual((result["rc"], result["status"], result["published"]), (2, "refused", False), result)

    def test_background_resident_rate_excludes_arguments_read_latency(self):
        from tests.align import test_r0_vs_l3_differential as fixture

        class Resident(fixture.Process):
            def row(self, now):
                pid, born, cpu, command, argv = super().row(now)
                return pid, born, 75 if 45 <= now < 60 else cpu, command, argv

        # The quiet control sits one TIME quantum below 1.50 CPU-s: at least
        # the limit within 30 s flags (lead ruling after audit 5).
        for delay, cpu, busy in ((0, 151, True), (0.5, 151, True), (2, 151, True), (0.5, 149, False)):
            with self.subTest(delay=delay, cpu=cpu):
                paired = False

                def run(original, model, argv, **kwargs):
                    nonlocal paired
                    result = original(model, argv, **kwargs)
                    if paired and tuple(argv) == prewindow.PS_ARGV and model.now == 60:
                        model.now += delay
                    paired = tuple(argv) == contention.PS_ARGV
                    return result

                worker = Resident(fixture.WORKER, cpu_at=60, centiseconds=cpu)
                result = self.trial(fixture.Case("background_args_latency", (worker,), end=65), command=run)
                if busy:
                    self.assert_withheld(result)
                    self.assertTrue(any(flag[:3] == (30.0, 60.0, fixture.PID) for flag in result["flags"]), result)
                    self.assertIn((30.0, 60.0), result["report_intervals"])
                else:
                    self.assertEqual((result["rc"], result["published"], result["flags"]), (0, True, []), result)

    def test_contaminant_substrings_keep_admitted_cpu_flags(self):
        from tests.align import test_r0_vs_l3_differential as fixture

        commands = ["corespotlightd"]
        for name in prewindow.CONTAMINANTS.split("|"):
            commands.extend((f"core{name.swapcase()}helper", f"python3 /fixture/core{name}helper/work.py"))
        for command in commands:
            with self.subTest(command=command):
                worker = fixture.Process(command, cpu_at=30, centiseconds=180)
                result = self.trial(fixture.Case("admitted_contaminant_substring", (worker,), end=60))
                self.assert_withheld(result)
                self.assertTrue(any(flag[:3] == (0.0, 30.0, fixture.PID) for flag in result["flags"]), result)
                self.assertIn((0.0, 30.0), result["report_intervals"])

        # One TIME quantum below the limit stays quiet; ties flag (lead ruling after audit 5).
        for command, centiseconds in (("corespotlightd", 149), ("neutral-worker", 180)):
            with self.subTest(command=command, centiseconds=centiseconds):
                worker = fixture.Process(command, cpu_at=30, centiseconds=centiseconds)
                result = self.trial(fixture.Case("admitted_contaminant_control", (worker,), end=60))
                self.assertEqual((result["rc"], result["published"], result["flags"]), (0, True, []), result)

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

    def test_distinct_cpu_observations_on_window_edges_are_retained(self):
        from joulewise.align.r0_host import _window_reads

        before, opening, same_open, interior, same_close, current, after = (
            SimpleNamespace(midpoint_ns=stamp, index=index)
            for index, stamp in enumerate((9, 10, 10, 15, 20, 20, 21))
        )
        observations = [before, opening, same_open, interior, same_close, current, after]
        self.assertEqual(_window_reads(observations, opening, current), [opening, same_open, interior, same_close, current])

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


class R0LatchedCensusAdmissionTest(unittest.TestCase):
    """Audit round 2 HIGH: no clear verdict after the sampler latched a failure."""
    setUp = R0HostTest.setUp
    runner = R0HostTest.runner
    trial = R0PublicationAuditTest.trial

    def fixture_type(self, *, fail_when, on_probe=None):
        """A frozen-suite fixture whose sampler fails to list the required root."""
        from contextlib import contextmanager
        import errno
        import os
        import threading
        from tests.align import test_r0_vs_l3_differential as fixture

        class RequiredRootFault(fixture.Fixture):
            def __init__(self, case, root):
                super().__init__(case, root)
                self.timeline = []
                self.probes = 0

            def run(self, argv, **kwargs):
                if on_probe is not None and threading.current_thread() is threading.main_thread():
                    on_probe(self, argv)
                return super().run(argv, **kwargs)

            @contextmanager
            def io_faults(self):
                real = os.scandir
                required = self.parent.stat()

                def scandir(fd="."):
                    if (fail_when(self) and threading.current_thread() is not threading.main_thread()
                            and isinstance(fd, int) and os.path.samestat(os.fstat(fd), required)):
                        self.timeline.append(("required root enumeration fails", errno.EIO))
                        raise OSError(errno.EIO, "fixture read fault", str(self.parent))
                    return real(fd)

                with super().io_faults(), patch.object(os, "scandir", scandir):
                    yield

            def disk(self, *args):
                self.timeline.append(("disk work starts", bool(self.guard._background_failure)))
                return super().disk(*args)

        return RequiredRootFault

    def test_audit2_forced_disk_admission_refuses_eio_latched_during_its_own_census(self):
        # Audit round 2 census_overlap.py. "during": the sampler's 45 s cycle
        # fails while the disk unit's forced admission waits on launchctl.
        from tests.align import test_r0_vs_l3_differential as fixture

        def overlap(model, argv):
            if (model.case.name == "during" and model.phase == "disk_unit" and model.now == 44
                    and argv[0] == "/bin/launchctl"):
                model.move(45)
                model.timeline.append(("foreground probe resumes", bool(model.guard._background_failure)))

        base = self.fixture_type(fail_when=lambda model: model.case.name != "quiet" and model.now == 45,
                                 on_probe=overlap)

        class Overlap(base):
            def move(self, end):
                if self.phase == "disk_unit" and end == 44 and self.case.name == "before":
                    end = 45
                super().move(end)

        admissions = ["baseline", "host_admit", "host_unit", "host_return", "disk_admit"]
        for name in ("quiet", "before", "during"):
            with self.subTest(case=name):
                models = []

                def factory(case, root):
                    models.append(Overlap(case, root))
                    return models[-1]

                result = self.trial(fixture.Case(name, schedule="multi", end=56), factory=factory)
                timeline = models[0].timeline
                if name == "quiet":
                    self.assertEqual((result["rc"], result["status"], result["published"]), (0, "pass", True), result)
                    self.assertEqual(result["work_started"], ["host", "disk"])
                    self.assertEqual(result["accepted"], [*admissions, "disk_unit", "last_forced"])
                    self.assertEqual(timeline, [("disk work starts", False)])
                    continue
                self.assertEqual((result["rc"], result["status"], result["published"]), (2, "refused", False), result)
                self.assertEqual(result["work_started"], ["host"], timeline)
                self.assertEqual(result["accepted"], admissions, timeline)
                self.assertIn("background sampler", result["reason"])
                self.assertIn("errno 5", result["reason"])
                expected = [("required root enumeration fails", 5)]
                if name == "during":
                    expected.append(("foreground probe resumes", True))
                self.assertEqual(timeline, expected)

    def test_sampler_failure_at_any_foreground_probe_admits_nothing_afterwards(self):
        # The class, not the case: move the same fault to every probe the
        # runner's thread makes once the sampler exists.
        from tests.align import test_r0_vs_l3_differential as fixture

        target = None

        def latch(model, argv):
            if model.guard._sampler is None:
                return
            index, model.probes = model.probes, model.probes + 1
            if index == target:
                model.armed = True
                stopped = model.timer.is_set()
                model.timer.pulse()  # one whole sampler cycle inside this probe
                model.latched = dict(phase=model.phase, accepted=list(model.accepted),
                                     work=list(model.work_started), stopped=stopped,
                                     failure=model.guard._background_failure)

        base = self.fixture_type(fail_when=lambda model: getattr(model, "armed", False), on_probe=latch)
        case = fixture.Case("latch_sweep", schedule="multi", end=56)

        def run():
            models = []

            def factory(case, root):
                models.append(base(case, root))
                return models[-1]

            return self.trial(case, factory=factory), models[0]

        result, model = run()
        self.assertEqual((result["rc"], result["published"]), (0, True), result)
        probes = model.probes
        # Five probes for each of six forced admissions after the baseline,
        # then two publication censuses.
        self.assertEqual(probes, 40)
        refused_in = {}
        for target in range(probes):
            with self.subTest(probe=target):
                result, model = run()
                latched = getattr(model, "latched", None)
                self.assertIsNotNone(latched)
                if latched["failure"] is None:
                    # A publication census: finish() had stopped the sampler.
                    self.assertTrue(latched["stopped"])
                    self.assertGreaterEqual(target, 30)
                    self.assertEqual((result["rc"], result["published"]), (0, True), result)
                    continue
                self.assertFalse(latched["stopped"])
                self.assertEqual((result["rc"], result["status"], result["published"]), (2, "refused", False), result)
                self.assertEqual(result["accepted"], latched["accepted"], latched)
                self.assertEqual(result["work_started"], latched["work"], latched)
                self.assertIn("errno 5", result["reason"])
                refused_in[latched["phase"]] = refused_in.get(latched["phase"], 0) + 1
        self.assertEqual(refused_in, dict.fromkeys(
            ("host_admit", "host_unit", "host_return", "disk_admit", "disk_unit", "last_forced"), 5))

    def admitted_guard(self):
        import threading

        clock = GuardClock()
        failing = threading.local()

        def custody(**kwargs):
            if getattr(failing, "now", False):
                raise OSError(5, "fixture read fault")
            return Census()

        guard = QuietGuard([], run=self.runner, inspect_custody=custody, clock=clock, sleep=clock.sleep,
                           host_reader=None)
        guard.wall_clock_ns = lambda: 1_800_000_000_000_000_000 + int(clock.now * 1e9)
        guard.SNAPSHOT_CADENCE_S = 3600  # the fixture runs every sampler cycle
        self.addCleanup(guard.close)
        guard.check(force=True)

        def fail_sampler_cycle():
            def cycle():
                failing.now = True
                guard._background_snapshot()
            thread = threading.Thread(target=cycle)
            thread.start()
            thread.join(5)
            self.assertFalse(thread.is_alive())
        return guard, clock, fail_sampler_cycle

    def test_every_verdict_refuses_a_failure_latched_at_any_of_its_probes(self):
        import threading

        for verdict in ("check", "verify_publication"):
            counted = []
            guard, clock, _ = self.admitted_guard()
            guard.run = lambda argv, **kwargs: counted.append(argv) or self.runner(argv, **kwargs)
            clock.now += 1
            (guard.verify_publication if verdict == "verify_publication" else lambda: guard.check(force=True))()
            self.assertGreaterEqual(len(counted), 5)
            for target in range(len(counted)):
                with self.subTest(verdict=verdict, probe=target):
                    guard, clock, fail_sampler_cycle = self.admitted_guard()
                    seen = []

                    def run(argv, **kwargs):
                        if threading.current_thread() is threading.main_thread():
                            seen.append(argv)
                            if len(seen) - 1 == target:
                                fail_sampler_cycle()
                        return self.runner(argv, **kwargs)

                    guard.run = run
                    clock.now += 1
                    receipts = len(guard.receipts)
                    with self.assertRaisesRegex(Refused, r"background sampler: OSError: \[Errno 5\]"):
                        (guard.verify_publication if verdict == "verify_publication"
                         else lambda: guard.check(force=True))()
                    # The verdict's own probes all ran; only its end refused.
                    self.assertEqual(len(seen), len(counted))
                    self.assertIn("Errno 5", guard.failure)
                    self.assertIn("Errno 5", guard.receipts[-1]["refusal"])
                    self.assertEqual(len(guard.receipts), receipts + 1)
                    with self.assertRaisesRegex(Refused, "Errno 5"):
                        guard.check()

    def test_throttled_check_refuses_a_latched_failure_before_the_sampler_stops(self):
        # The sampler latches its failure, then sets its stop flag. A tick
        # between the two must not ride the 15 s throttle.
        guard, clock, _ = self.admitted_guard()
        clock.now += 1
        guard.check()
        self.assertIsNone(guard.failure)
        with guard._snapshot_lock:
            guard._background_failure = "OSError: [Errno 5] fixture read fault"
        self.assertFalse(guard._stop_sampler.is_set())
        clock.now += 1
        with self.assertRaisesRegex(Refused, r"background sampler: OSError: \[Errno 5\]"):
            guard.check()
        self.assertIn("Errno 5", guard.receipts[-1]["refusal"])
        self.assertTrue(guard._stop_sampler.is_set())

    def test_refusal_without_a_message_still_latches(self):
        # str(MemoryError()) is empty. The refusal it causes must still
        # refuse every later verdict, for a caller that caught the first.
        for error in (MemoryError(), OSError(), TimeoutError()):
            with self.subTest(error=type(error).__name__):
                fault = [error]
                guard, clock, _ = self.admitted_guard()
                clear = guard.inspect_custody
                guard.inspect_custody = lambda **kwargs: (_ for _ in ()).throw(fault.pop()) if fault else clear(**kwargs)
                clock.now += 1
                with self.assertRaises(Refused):
                    guard.check(force=True)
                self.assertEqual(guard.failure, type(error).__name__)
                self.assertEqual(guard.receipts[-1]["refusal"], type(error).__name__)
                clock.now += 1
                for verdict in (lambda: guard.check(force=True), guard.check, guard.finish, guard.verify_publication):
                    with self.assertRaisesRegex(Refused, type(error).__name__):
                        verdict()

    def test_finish_refuses_a_failure_latched_after_its_windows_were_judged(self):
        guard, clock, _ = self.admitted_guard()
        judged = guard._cpu_interval

        def late(receipt):
            busy = judged(receipt)
            with guard._snapshot_lock:
                guard._background_failure = "OSError: [Errno 5] fixture read fault"
            return busy

        guard._cpu_interval = late
        with self.assertRaisesRegex(Refused, r"background sampler: OSError: \[Errno 5\]"):
            guard.finish()
        self.assertIn("Errno 5", guard.failure)


class R0AdvisoryAdmissionTest(unittest.TestCase):
    """Lead ruling after audit 3: the final verdict is R0's only authority.

    Admission is advisory. Its last act re-reads the latch, the age of the
    newest sample and the windows completed during its own probes. Window
    arithmetic is monotonic; a window whose wall clock moves more than
    0.5 s against the monotonic clock is flagged.
    """
    setUp = R0HostTest.setUp
    runner = R0HostTest.runner
    trial = R0PublicationAuditTest.trial
    admitted_guard = R0LatchedCensusAdmissionTest.admitted_guard

    def run_model(self, case, model_type):
        models = []

        def factory(case, root):
            models.append(model_type(case, root))
            return models[-1]

        return self.trial(case, factory=factory), models[0]

    def test_audit3_admission_refuses_a_stale_sample_or_long_window_reached_during_its_probes(self):
        # Audit round 3 stall_admission.py. Only the 45 s tick fires (and
        # 105 s in the long cases), so the newest sample stays at 45 s. The
        # disk unit's admission starts at 94.9 s; "during" cases cross the
        # limit inside its launchctl probe. "boundary" ends at exactly 50.0 s.
        from tests.align import test_r0_vs_l3_differential as fixture

        class Stall(fixture.Fixture):
            def move(self, end):
                if self.phase == "disk_unit" and end == 44:
                    end = {"stale_before": 95.1, "long_before": 105}.get(self.case.name, 94.9)
                elif end in (56, 58):
                    end += 52
                super().move(end)

            def run(self, argv, **kwargs):
                if self.phase == "disk_unit" and self.now == 94.9 and argv[0] == "/bin/launchctl":
                    super().move({"boundary": 95, "stale_during": 95.1, "long_during": 105}[self.case.name])
                return super().run(argv, **kwargs)

        refused_at_disk = ["baseline", "host_admit", "host_unit", "host_return", "disk_admit"]
        for name, reason in (("stale_before", "stalled (50.1 s since the last)"),
                             ("stale_during", "stalled (50.1 s since the last)"),
                             ("long_before", "judged CPU window of 60.0 s exceeds 50 s"),
                             ("long_during", "judged CPU window of 60.0 s exceeds 50 s"),
                             ("boundary", "stalled (63.0 s since the last)")):
            with self.subTest(case=name):
                case = fixture.Case(name, schedule="multi", ticks=(45, 105) if name.startswith("long") else (45,))
                result, _ = self.run_model(case, Stall)
                # The final verdict withholds every case.
                self.assertEqual((result["rc"], result["status"], result["published"]), (2, "refused", False), result)
                self.assertIn(reason, result["reason"])
                if name == "boundary":
                    # A sample exactly 50.0 s old is within the limit: the advisory
                    # admission lets disk work start, and the final verdict refuses.
                    self.assertEqual(result["work_started"], ["host", "disk"])
                else:
                    self.assertEqual(result["work_started"], ["host"], result)
                    self.assertEqual(result["accepted"], refused_at_disk)

    def stepped(self, step_at, step_s, rows=None):
        from tests.align import test_r0_vs_l3_differential as fixture

        class Stepped(fixture.Fixture):
            def wall_ns(self):
                return super().wall_ns() + (int(step_s * 1e9) if self.now >= step_at else 0)

            def processes(self):
                return [*super().processes(), *(rows(self.case, self.now) if rows else ())]

        return Stepped

    def test_audit3_forward_wall_step_flags_the_window_and_withholds(self):
        # Audit round 3 wall_step.py. A worker born at 11 s is listed once, by
        # the 15 s accounting read, with 1.80 CPU-s, and has gone by 30 s.
        # "step": the wall clock jumps 2 s forward at 10 s, so ps prints the
        # start as 13 s. 9c01174a6 published that run with no flag.
        from tests.align import test_r0_vs_l3_differential as fixture

        def rows(case, now):
            if 11 <= now < 20:
                yield (fixture.PID, 13 if case.name == "step" else 11, 180, fixture.WORKER, "/fixture/mdworker_shared")

        for name in ("stable", "step"):
            with self.subTest(case=name):
                result, model = self.run_model(fixture.Case(name, end=40),
                                               self.stepped(10, 2 if name == "step" else 0, rows))
                self.assertEqual((result["rc"], result["status"], result["published"]), (2, "refused", False), result)
                clock = [f for f in model.guard.contention_flags if f.get("kind") == "wall_clock"]
                if name == "step":
                    # The 0-30 s sampler window and the 0-40 s admission window
                    # both contain the step; E1 can flag the CPU at 15 s first.
                    self.assertEqual([(f["interval"]["start_monotonic_s"], f["interval"]["end_monotonic_s"])
                                      for f in clock], [(0.0, 30.0), (0.0, 40.0)])
                    self.assertTrue(all("wall clock moved 2 s" in f["flag"] for f in clock), result)
                else:
                    self.assertEqual(clock, [])
                    self.assertIn((0.0, 30.0, fixture.PID), [flag[:3] for flag in result["flags"]], result)
                self.assertEqual(result["recorded"], result["guard_count"])

    def test_wall_clock_divergence_flags_a_window_only_above_half_a_second(self):
        # A quiet host. The wall clock steps at 10 s, inside the 0-30 s window.
        # The window rule flags only above 0.5 s. Since lead K1 the series'
        # stability precondition withholds every step above 1 ms first, as
        # clock_unstable; a 0.5 ms step publishes.
        from tests.align import test_r0_vs_l3_differential as fixture

        for step_s, flagged in ((0.0005, None), (-0.0005, None), (0.49, False), (-0.49, False),
                                (0.51, True), (-0.51, True)):
            with self.subTest(step_s=step_s):
                result, model = self.run_model(fixture.Case(f"step_{step_s}", end=40), self.stepped(10, step_s))
                clock = [f for f in model.guard.contention_flags if f.get("kind") == "wall_clock"]
                if flagged is None:
                    self.assertEqual((result["rc"], result["status"], result["published"], result["flags"]),
                                     (0, "pass", True, []), result)
                else:
                    self.assertEqual((result["rc"], result["status"], result["published"]), (2, "refused", False))
                    self.assertIn("clock_unstable", result["reason"])
                    self.assertIn(f"{abs(step_s) * 1e6:.3f} µs", result["reason"])
                if flagged:
                    self.assertEqual([(f["interval"]["start_monotonic_s"], f["interval"]["end_monotonic_s"])
                                      for f in clock], [(0.0, 30.0), (0.0, 40.0)])
                    self.assertTrue(all(f"wall clock moved {abs(step_s):g} s" in f["flag"] for f in clock))
                else:
                    self.assertEqual(clock, [])
                self.assertEqual(result["recorded"], result["guard_count"])

    def test_throttled_tick_does_not_skip_a_stale_sample_or_a_completed_window(self):
        # The newest sample is from 30 s. An admission at 70 s finds it 40 s
        # old and returns clear. A tick within 15 s of it used to skip.
        for case, reason in (("stale", r"background snapshots stalled \(54.0 s"),
                             ("long_window", r"judged CPU window of 51.0 s exceeds")):
            with self.subTest(case=case):
                guard, clock, _ = self.admitted_guard()
                clock.now = 70
                guard.check(force=True)
                if case == "long_window":
                    clock.now = 81
                    guard._background_snapshot()  # one sampler cycle, 51 s after the last
                    clock.now = 82
                else:
                    clock.now = 84
                self.assertLess(clock.now - guard.last, 15)
                with self.assertRaisesRegex(Refused, reason):
                    guard.check()
                self.assertRegex(guard.failure, reason)

        # A fresh sample and nothing awaiting judgment: the tick still skips.
        guard, clock, _ = self.admitted_guard()
        clock.now = 40
        guard.check(force=True)
        receipts = len(guard.receipts)
        clock.now = 50
        self.assertIsNone(guard.check())
        self.assertEqual(len(guard.receipts), receipts)


class R0FinalVerdictTest(unittest.TestCase):
    """Lead rulings after audits 4 and 5: the final verdict is self-contained.

    Its windows come only from the sample series (startup, daemon, and the
    read each publication census takes at run end). It judges every sliding
    window, including the one ending at the final read, and at every sample
    the exact check against each earlier sample at most INTERVAL_S before
    it. Admission is never its opening.
    """
    setUp = R0HostTest.setUp
    runner = R0HostTest.runner
    trial = R0PublicationAuditTest.trial

    def schedule(self, *, first_tick, cadence, burst_at=None, admission_at=None):
        """The frozen fixture with a daemon schedule and a 1.80 CPU-s burst over 4 s."""
        from tests.align import test_r0_vs_l3_differential as fixture

        class Burst(fixture.Fixture):
            def __init__(self, case, root):
                super().__init__(case, root)
                self.next_tick = first_tick

            def move(self, end):
                # The daemon wakes every `cadence` seconds after its first tick.
                while self.next_tick <= end:
                    self.now = self.next_tick
                    self.next_tick += cadence
                    self.apply_tree()
                    self.timer.pulse()
                self.now = end
                self.apply_tree()

            def processes(self):
                gain = 0 if burst_at is None else round(100 * min(1.8, max(0, self.now - burst_at) * 0.45))
                return [*super().processes(), (fixture.PID, -100, gain, fixture.WORKER, "/fixture/mdworker_shared")]

            def host(self):
                self.work_started.append("host")
                self.phase = "host_return"
                if admission_at is not None:
                    self.move(admission_at)
                    self.guard.check(force=True)
                self.move(self.case.end)
                return {"status": "pass"}

        return Burst

    def run_model(self, case, model_type):
        models = []

        def factory(case, root):
            models.append(model_type(case, root))
            return models[-1]

        return self.trial(case, factory=factory), models[0]

    @staticmethod
    def series_receipts(guard):
        return [*guard.receipts, *(r["publication_census"] for r in guard.receipts if "publication_census" in r)]

    @classmethod
    def verdict_windows(cls, guard, *, flagged=False):
        """Windows the verdict judged over the series (never admission windows).

        Exact-check pairs are recorded only when they hold at least the
        limit, so each one listed is a flagged window.
        """
        receipts = cls.series_receipts(guard)
        rule = {(w["start_monotonic_s"], w["end_monotonic_s"]) for r in receipts
                for w in r.get("cpu_intervals", ()) if w.get("contention_flag") or not flagged}
        exact = {(w["start_monotonic_s"], w["end_monotonic_s"]) for r in receipts for w in r.get("exact_windows", ())}
        return sorted(rule | exact)

    @classmethod
    def verdict_flags(cls, guard):
        """Series windows the verdict itself flagged."""
        return cls.verdict_windows(guard, flagged=True)

    def test_audit4_terminal_contention_is_judged_from_the_series_final_read(self):
        # Audit round 4 terminal_30s.py. The daemon wakes 0.5 s late each
        # cadence: samples at 45.5 and 61.0 s. The run ends at 75.5 s. A
        # worker reaches 1.80 CPU-s between 71.5 and 75.5 s. c069985cb opened
        # the last window at the 30.0 s admission (45.5 s long, 0.040 CPU-s/s)
        # and published.
        from tests.align import test_r0_vs_l3_differential as fixture

        cases = (("quiet", 75.5, None, None), ("normal", 75.5, 71.5, None),
                 ("extra_admission", 75.5, 71.5, 45.5), ("next_tick", 76.5, 71.5, None))
        for name, end, burst_at, admission_at in cases:
            with self.subTest(case=name):
                result, model = self.run_model(fixture.Case(name, end=end), self.schedule(
                    first_tick=45.5, cadence=15.5, burst_at=burst_at, admission_at=admission_at))
                if burst_at is None:
                    self.assertEqual((result["rc"], result["status"], result["published"], result["flags"]),
                                     (0, "pass", True, []), result)
                    continue
                self.assertEqual((result["rc"], result["status"], result["published"]), (2, "refused", False), result)
                # The verdict judges the series window ending at the final read,
                # and that window is flagged. An extra admission at 45.5 s can
                # flag the same window first; the verdict does not need it.
                self.assertIn((45.5, end), self.verdict_windows(model.guard))
                self.assertIn((45.5, end), [(f["interval"]["start_monotonic_s"], f["interval"]["end_monotonic_s"])
                                            for f in model.guard.contention_flags])
                if admission_at is None:
                    self.assertIn((45.5, end), self.verdict_flags(model.guard))
                self.assertEqual(result["recorded"], result["guard_count"])

    def test_a_burst_at_every_five_second_offset_flags_through_the_verdict(self):
        # 1.80 CPU-s over 4 s placed at every 5 s offset across the run. Two
        # schedules: the audit's (daemon 0.5 s late, final read at 75.5 s)
        # and the regular cadence with an off-grid final read at 74 s, whose
        # sliding window opens at 30 s (44 s long); only the window of exactly
        # 30 s ending at 74 s proves a burst in its last 30 s.
        from tests.align import test_r0_vs_l3_differential as fixture

        for first_tick, cadence, end in ((45.5, 15.5, 75.5), (45, 15, 74)):
            with self.subTest(end=end, burst=None):
                result, _ = self.run_model(fixture.Case(f"quiet_{end}", end=end),
                                           self.schedule(first_tick=first_tick, cadence=cadence))
                self.assertEqual((result["rc"], result["published"], result["flags"]), (0, True, []), result)
            for burst_at in range(0, int(end) - 4 + 1, 5):
                with self.subTest(end=end, burst=burst_at):
                    result, model = self.run_model(fixture.Case(f"burst_{end}_{burst_at}", end=end), self.schedule(
                        first_tick=first_tick, cadence=cadence, burst_at=burst_at))
                    self.assertEqual((result["rc"], result["status"], result["published"]),
                                     (2, "refused", False), result)
                    covering = [w for w in self.verdict_flags(model.guard)
                                if w[0] <= burst_at and burst_at + 4 <= w[1]]
                    self.assertTrue(covering, (burst_at, self.verdict_flags(model.guard)))

    def test_exact_check_flags_at_least_the_limit_within_any_30_s(self):
        # Regular cadence, final read at 74 s. The worker's counter jumps at
        # 70 s. The sliding window ending at 74 s opens at 30 s (44 s long);
        # the exact check pairs 74 s with the 45 s and 60 s samples, charging
        # their growth to 30 s. At least 1.50 CPU-s (the limit times 30 s)
        # flags, ties included; 1.49 stays quiet.
        from tests.align import test_r0_vs_l3_differential as fixture

        for total_cs, flagged in ((149, False), (150, True), (152, True)):
            with self.subTest(total_cs=total_cs):
                class Exact(self.schedule(first_tick=45, cadence=15)):
                    def processes(self):
                        rows = fixture.Fixture.processes(self)
                        cs = total_cs if self.now >= 70 else 0
                        return [*rows, (fixture.PID, -100, cs, fixture.WORKER, "/fixture/mdworker_shared")]

                result, model = self.run_model(fixture.Case(f"exact_{total_cs}", end=74), Exact)
                if flagged:
                    self.assertEqual((result["rc"], result["published"]), (2, False), result)
                    self.assertLessEqual({(45.0, 74.0), (60.0, 74.0)}, set(self.verdict_flags(model.guard)))
                    rates = {row["cpu_s_per_s"] for f in model.guard.contention_flags for row in f["busy"]
                             if (f["interval"]["start_monotonic_s"], f["interval"]["end_monotonic_s"]) == (45.0, 74.0)}
                    self.assertEqual(rates, {total_cs / 100 / 30})
                else:
                    self.assertEqual((result["rc"], result["published"], result["flags"]), (0, True, []), result)

    def series_fixture(self, ticks, rows, *, read_ms=0):
        """The frozen fixture with explicit daemon ticks and extra process rows."""
        from tests.align import test_r0_vs_l3_differential as fixture

        class Series(fixture.Fixture):
            def __init__(self, case, root):
                super().__init__(case, root)
                self.ticks = list(ticks)

            def move(self, end):
                if self.case.schedule == "inventory" and end == 45 and "inventory" in self.work_started:
                    end = self.case.end
                while self.ticks and self.ticks[0] <= end:
                    self.now = self.ticks.pop(0)
                    self.apply_tree()
                    self.timer.pulse()
                self.now = max(self.now, end)
                self.apply_tree()

            def processes(self):
                return [*super().processes(), *rows(self.now)]

            def run(self, argv, **kwargs):
                result = super().run(argv, **kwargs)
                if tuple(argv) == contention.PS_ARGV:
                    self.now += read_ms / 1000
                return result

        return Series

    def test_audit_r2_birth_and_absence_supply_zero_exact_openings(self):
        from tests.align import test_r0_vs_l3_differential as fixture

        for mode, size, refused in (("integer", 150, True), ("fractional", 151, True), ("reuse", 151, True),
                                    ("older", 150, True), ("older", 151, True), ("older", 149, False),
                                    ("fractional", 149, False)):
            name = f"{mode}_{size}"
            opening, end = (46.0, 76.0) if mode == "integer" else (45.5, 75.4)
            birth = -100 if mode == "older" else opening + 0.1

            def rows(now):
                if now < birth:
                    if mode == "reuse":
                        yield fixture.PID, -100, 0, "ordinary", "/fixture/ordinary"
                    return
                early = min(1, max(0, (now - 50) / 4))
                late = min(1, max(0, (now - 68) / 4))
                cpu = round(75 * early + (size - 75) * late)
                yield fixture.PID, int(birth), cpu, fixture.WORKER, "/fixture/mdworker_shared"

            with self.subTest(case=name):
                result, model = self.run_model(fixture.Case(name, end=end),
                                               self.series_fixture((opening, opening + 15.5), rows))
                self.assertEqual((result["rc"], result["published"]), (2, False) if refused else (0, True), result)
                self.assertEqual(result["recorded"], result["guard_count"])
                if refused:
                    # The exact proof at the closing read stays in the receipt.
                    # Since the birth bound also starts the lifetime overlap
                    # at the sampled absence, 1.51 CPU-s within 29.9 s can be
                    # flagged by the rule window first.
                    self.assertIn((opening, end, fixture.PID), self.exact_proofs(model.guard), result)
                    self.assertTrue(any(stop == end and pid == fixture.PID
                                        for _, stop, pid in self.verdict_flag_keys(model.guard)), result)
                else:
                    self.assertEqual(result["flags"], [], result)

    def test_audit_r2_turnover_interior_report_and_inventory(self):
        from tests.align import test_r0_vs_l3_differential as fixture

        for mode in ("reused", "fresh", "resident"):
            for size in (149, 152):
                for schedule, read_ms in (("host", 0), ("host", 10), ("inventory", 0), ("inventory", 10)):
                    name = f"{mode}_{size}_interior"
                    birth = -100 if mode == "resident" else 45.85

                    def rows(now):
                        if now < birth:
                            if mode == "reused":
                                yield fixture.PID, -100, 7, "ordinary", "/fixture/ordinary"
                            return
                        early = min(1, max(0, (now - 48) / 6))
                        late = min(1, max(0, (now - 67) / 6))
                        cpu = round(60 * early + (size - 60) * late)
                        yield fixture.PID, birth, cpu, fixture.WORKER, "/fixture/mdworker_shared"

                    with self.subTest(case=name, schedule=schedule, read_ms=read_ms):
                        ticks = (45.8, 75.7, 91.2, 106.7)
                        result, model = self.run_model(fixture.Case(name, schedule=schedule, end=ticks[-1]),
                                                       self.series_fixture(ticks, rows, read_ms=read_ms))
                        if size == 152:
                            self.assertEqual((result["rc"], result["published"]), (2, False), result)
                            closing = 75.7 + read_ms / 2000
                            if mode != "resident":
                                # A fresh PID's zero is the start of the arguments
                                # table read with the 45.8 s sample, which lists no
                                # such PID. Where another process holds the PID that
                                # table proves nothing; the accounting read's
                                # midpoint is the zero.
                                zero = 45.8 + (read_ms / 1000 if mode == "fresh" else read_ms / 2000)
                                self.assertIn((round(zero, 6), round(closing, 6), fixture.PID),
                                              self.exact_proofs(model.guard), result)
                            self.assertTrue(any(stop == closing and pid == fixture.PID
                                                for _, stop, pid in self.verdict_flag_keys(model.guard)), result)
                        else:
                            self.assertEqual((result["rc"], result["published"], result["flags"]),
                                             (0, True, []), result)

    def exact_proofs(self, guard):
        """(start, end, pid) of every exact-check proof in the series receipts, to the microsecond."""
        return {(round(window["start_monotonic_s"], 6), round(window["end_monotonic_s"], 6), row["pid"])
                for receipt in self.series_receipts(guard) for window in receipt.get("exact_windows", ())
                for row in window["busy"]}

    def verdict_flag_keys(self, guard):
        windows = set(self.verdict_windows(guard))
        return {(f["interval"]["start_monotonic_s"], f["interval"]["end_monotonic_s"], row["pid"])
                for f in guard.contention_flags for row in f["busy"]
                if (f["interval"]["start_monotonic_s"], f["interval"]["end_monotonic_s"]) in windows}

    def test_audit5_quiet_samples_appended_after_an_interior_burst_keep_its_flag(self):
        # Audit round 5 interior_burst.py. The daemon wakes 0.5 s late: samples
        # at 45.5, 61.0, 76.5 s and on. A worker accrues TOTAL centiseconds
        # between 52 and 56 s. "short" ends at 61.0 s; "extended" appends
        # quiet samples through 107.5 s. 671bd3f1d flagged short_152 and
        # short_160 and published every extended run.
        from tests.align import test_r0_vs_l3_differential as fixture

        ticks = [45.5 + 15.5 * k for k in range(5)]
        for total in (0, 150, 152, 160):
            def rows(now, total=total):
                return [(fixture.PID, -100, round(total * min(1, max(0, (now - 52) / 4))),
                         fixture.WORKER, "/fixture/mdworker_shared")]

            outcomes = {}
            for name, end in (("short", 61.0), ("extended", 107.5)):
                with self.subTest(total=total, run=name):
                    result, model = self.run_model(fixture.Case(f"{name}_{total}", end=end),
                                                   self.series_fixture(ticks, rows))
                    outcomes[name] = result, self.verdict_flag_keys(model.guard)
                    if total == 0:
                        self.assertEqual((result["rc"], result["published"], result["flags"]), (0, True, []), result)
                    else:
                        # At least 1.50 CPU-s between the 45.5 s and 61.0 s samples.
                        self.assertEqual((result["rc"], result["status"], result["published"]),
                                         (2, "refused", False), result)
                        self.assertIn((45.5, 61.0, fixture.PID), outcomes[name][1])
            with self.subTest(total=total, monotone=True):
                self.assertLessEqual(outcomes["short"][1], outcomes["extended"][1])

    def test_appending_quiet_samples_never_removes_a_verdict_flag(self):
        # Generated: burst position x size around the limit x daemon schedule
        # x appended quiet tail. Each short run ends on a daemon tick, so its
        # samples are a subset of every extended run's. Bursts accrue over 4 s.
        from tests.align import test_r0_vs_l3_differential as fixture

        schedules = {"on": [45 + 15 * k for k in range(6)],
                     "off": [45.5 + 15.5 * k for k in range(6)],
                     "jitter": [45 + 15 * k + (0.4 if k % 2 == 0 else -0.4) for k in range(6)]}
        for label, ticks in schedules.items():
            short_end = ticks[2]
            positions = {"start": 2.0, "interior": 50.0, "end": short_end - 4}
            for position, burst_at in positions.items():
                for size_cs in (149, 150, 151, 180):
                    def rows(now, burst_at=burst_at, size_cs=size_cs):
                        return [(fixture.PID, -100, round(size_cs * min(1, max(0, (now - burst_at) / 4))),
                                 fixture.WORKER, "/fixture/mdworker_shared")]

                    runs = {}
                    for tail in (0, 1, 3):
                        end = ticks[2 + tail]
                        result, model = self.run_model(
                            fixture.Case(f"{label}_{position}_{size_cs}_{tail}", end=end),
                            self.series_fixture(ticks, rows))
                        runs[tail] = result, self.verdict_flag_keys(model.guard)
                    with self.subTest(schedule=label, position=position, size_cs=size_cs):
                        short, short_keys = runs[0]
                        for tail in (1, 3):
                            longer, longer_keys = runs[tail]
                            self.assertLessEqual(short_keys, longer_keys, (tail, short_keys, longer_keys))
                            if short["rc"] == 2:
                                self.assertEqual((longer["rc"], longer["published"]), (2, False), longer)
                        if size_cs >= 150:
                            # A 4 s burst lies between two samples at most 30 s apart.
                            self.assertEqual((short["rc"], short["published"]), (2, False), short)
                            self.assertTrue(any(start <= burst_at and burst_at + 4 <= stop
                                                for start, stop, _ in short_keys), short_keys)
                        else:
                            for tail in (0, 1, 3):
                                self.assertEqual((runs[tail][0]["rc"], runs[tail][0]["published"],
                                                  runs[tail][0]["flags"]), (0, True, []), runs[tail][0])

    def test_e1_sweep_crosses_birth_openings_limits_schedules_and_quiet_tails(self):
        from tests.align import test_r0_vs_l3_differential as fixture

        # Split the burst so neither observed counter delta alone suffices
        # for a newborn. A resident also carries CPU from before the run.
        for schedule, opening, middle, end, cadence in (
                ("on", 45, 60, 75, 15), ("off", 45.5, 61, 75.4, 15.5),
                ("jitter", 45.4, 59.6, 75.3, 15.2)):
            for mode in ("resident", "born_inside", "reused", "fresh", "start_exactly_30"):
                if mode in ("born_inside", "start_exactly_30"):
                    birth = 46.1
                    close = 75.9 if mode == "born_inside" else 76
                else:
                    birth = -100 if mode == "resident" else opening + 0.09
                    close = end
                ticks = [opening, middle, *(round(close + cadence * i, 3) for i in range(4))]
                for size in (149, 150, 151, 152):
                    def worker_at(now):
                        if now < birth:
                            return None
                        early = min(1, max(0, (now - 50) / 4))
                        late = min(1, max(0, (now - 68) / 4))
                        return (230 if mode == "resident" else 0) + round(60 * early + (size - 60) * late)

                    def rows(now):
                        cpu = worker_at(now)
                        if cpu is not None:
                            yield fixture.PID, int(birth), cpu, fixture.WORKER, "/fixture/mdworker_shared"
                        elif mode == "reused":
                            yield fixture.PID, -100, 7, "ordinary", "/fixture/ordinary"

                    prior_exact, prior_flags = set(), set()
                    for tail in (0, 1, 3):
                        with self.subTest(schedule=schedule, mode=mode, size=size, tail=tail):
                            samples = [0, 15, 30, *ticks[:3 + tail]]
                            expected = set()
                            for j, stop in enumerate(samples):
                                cpu = worker_at(stop)
                                if cpu is None:
                                    continue
                                openings = [(at, worker_at(at) or 0) for at in samples[:j]]
                                if mode != "resident":
                                    openings.append((int(birth), 0))
                                expected.update((at, stop, fixture.PID) for at, baseline in openings
                                                if 0 <= stop - at <= 30 and cpu - baseline >= 150)
                            result, model = self.run_model(
                                fixture.Case(f"{mode}_{size}", end=samples[-1]), self.series_fixture(ticks, rows))
                            exact = {(window["start_monotonic_s"], window["end_monotonic_s"], row["pid"])
                                     for receipt in self.series_receipts(model.guard)
                                     for window in receipt.get("exact_windows", ()) for row in window["busy"]}
                            flags = self.verdict_flag_keys(model.guard)
                            self.assertEqual(exact, expected, result)
                            self.assertEqual((result["rc"], result["published"]),
                                             (2, False) if expected else (0, True), result)
                            self.assertLessEqual(prior_exact, exact)
                            self.assertLessEqual(prior_flags, flags)
                            prior_exact, prior_flags = exact, flags
                            if mode == "start_exactly_30" and size >= 150:
                                self.assertEqual({at for at, stop, _ in exact if stop == close}, {46})
                                if size == 150:
                                    self.assertIn({"start_monotonic_s": 46, "end_monotonic_s": close, "elapsed_s": 30},
                                                  [flag.get("proof_interval") for flag in model.guard.contention_flags])

    def test_rule_window_uses_absence_even_if_a_wall_step_dates_the_birth_earlier(self):
        from tests.align import test_r0_vs_l3_differential as fixture

        for size in (149, 160):
            def rows(now):
                if now >= 45.85:
                    cpu = round(size * min(1, max(0, (now - 70) / 4)))
                    yield fixture.PID, 45, cpu, fixture.WORKER, "/fixture/mdworker_shared"

            class Shifted(self.series_fixture((45.8, 76.3), rows)):
                def wall_ns(self):
                    return super().wall_ns() + (300_000_000 if self.now >= 46 else 0)

            with self.subTest(size=size):
                result, model = self.run_model(fixture.Case(f"wall_step_{size}", end=76.3), Shifted)
                # The 300 ms step withholds every run as clock_unstable (lead
                # K1). The rule window still uses the absence: 1.60 CPU-s
                # over 30.5 s is flagged, 1.49 is not.
                self.assertEqual((result["rc"], result["published"]), (2, False), result)
                self.assertIn("clock_unstable", result["reason"])
                if size == 160:
                    self.assertIn((45.8, 76.3), self.verdict_flags(model.guard))
                    self.assertTrue(all(flag.get("kind") is None for flag in model.guard.contention_flags), result)
                else:
                    self.assertEqual(result["flags"], [], result)

    def birth_slew_fixture(self, size, shift_ns, ticks, *, slow_read_at=None):
        """Audit r3 birth_slew.py. A worker born at 46.1 s prints start 46 s;
        the 45.5 s read proves it absent and the 61 s read lists it first.
        The wall clock gains ``shift_ns`` linearly between 61 and 76 s. With
        ``slow_read_at`` that accounting read lasts 0.5 s."""
        from tests.align import test_r0_vs_l3_differential as fixture

        def rows(now):
            if now >= 46.1:
                early = min(1, max(0, (now - 50) / 4))
                late = min(1, max(0, (now - 68) / 4))
                yield (fixture.PID, 46, round(60 * early + (size - 60) * late), fixture.WORKER,
                       "/fixture/mdworker_shared")

        class Slewed(self.series_fixture(ticks, rows)):
            def wall_ns(self):
                portion = min(1, max(0, (self.now - 61) / 15))
                return fixture.EPOCH * 10**9 + round(self.now * 10**9) + round(shift_ns * portion)

            def run(self, argv, **kwargs):
                result = super().run(argv, **kwargs)
                if tuple(argv) == contention.PS_ARGV and self.now == slow_read_at:
                    self.now += 0.5
                return result

        return Slewed

    def test_audit_r3_wall_gain_after_a_birth_is_listed_keeps_its_opening(self):
        # Audit r3 birth_slew.py and birth_slew_timed.py. 52805409d converted
        # the printed start again at the 76 s closing read; after a 150 us
        # gain that opening moved to 45.999850 s, the 30.000150 s span was
        # dropped, and 1.50 (and, with the half-second read, 1.51) CPU-s
        # published in report and inventory mode.
        from tests.align import test_r0_vs_l3_differential as fixture

        plain = [(mode, shift, size, end, None) for mode in ("host", "inventory")
                 for shift in (0, 150_000, -150_000) for size in (149, 150, 151) for end in (76, 107)]
        timed = [(mode, shift, size, 107, 75.75) for mode in ("host", "inventory")
                 for shift in (0, 150_000) for size in (149, 150, 151, 152)]
        for mode, shift, size, end, slow_read_at in plain + timed:
            ticks = [45.5, 61.0, 75.75 if slow_read_at else 76.0, 91.5, 107.0]
            name = f"{mode}_{shift}_{size}_{end}" + ("_timed" if slow_read_at else "")
            with self.subTest(case=name):
                result, model = self.run_model(
                    fixture.Case(name, end=end, schedule=mode),
                    self.birth_slew_fixture(size, shift, ticks, slow_read_at=slow_read_at))
                if size == 149:
                    self.assertEqual((result["rc"], result["published"], result["flags"]), (0, True, []), result)
                    continue
                self.assertEqual((result["rc"], result["published"]), (2, False), result)
                # The receipt keeps the printed start second's proof exactly
                # 30 s before the closing midpoint, even where a rule window
                # flagged the worker first. The birth bound is fixed at the
                # 61 s first sighting, so neither a later gain nor a later
                # loss moves it.
                proofs = [round(window["start_monotonic_s"] * 1e9)
                          for receipt in self.series_receipts(model.guard)
                          for window in receipt.get("exact_windows", ())
                          if window["end_monotonic_s"] == 76.0
                          and any(row["basis"] == "CPU since the printed start second" for row in window["busy"])]
                self.assertTrue(proofs, model.guard.contention_flags)
                self.assertEqual(set(proofs), {46_000_000_000}, model.guard.contention_flags)
                if size == 150 and not slow_read_at:
                    # At the tie no rule window flags: the exact check alone refuses.
                    self.assertTrue(any(flag.get("kind") == "exact_30s" for flag in model.guard.contention_flags),
                                    model.guard.contention_flags)
                if mode == "host":
                    self.assertEqual(result["recorded"], result["guard_count"])

    def quiet_worker_fixture(self, shape, shift_ns, rate_ppm):
        """Audit r3 quiet_clock.py, quiet_timed_reads.py and quiet_clock_paths.py.

        A worker runs at ``rate_ppm`` millionths of a core from its birth
        until its close, and its TIME is rendered as Darwin ps does:
        microseconds, plus 5000, scaled to centiseconds. ``shape``:
        "timed" (10 ms accounting and arguments reads, CPU in the last part
        of each 10 ms period, wall step at 70 s), "witness" (instantaneous
        reads at the timed reads' midpoints), "before" (wall step at 50 s,
        between birth and the first sighting) or "gentle" (a linear wall
        change from 61 s to the close).
        """
        from tests.align import test_r0_vs_l3_differential as fixture

        ns = 10**9
        birth, close = (46_000_100_000, 76_004_500_000) if shape == "gentle" else (46_010_000_000, 76_400_000_000)
        ticks = {"timed": [46.245, 61.245, 76.395, 91.695], "witness": [46.25, 61.25, 76.4, 91.7, 107],
                 "before": [45.5, 61, 76.4, 91.7, 107], "gentle": [45.5, 61, 76.0045, 91.5, 107]}[shape]

        class QuietWorker(fixture.Fixture):
            def __init__(self, case, root):
                super().__init__(case, root)
                self.ticks = list(ticks)

            def move(self, end):
                if self.case.schedule == "inventory" and end == 45 and "inventory" in self.work_started:
                    end = self.case.end
                while self.ticks and self.ticks[0] <= end:
                    self.now = self.ticks.pop(0)
                    self.apply_tree()
                    self.timer.pulse()
                self.now = end
                self.apply_tree()

            def wall_ns(self):
                now = round(self.now * ns)
                if shape == "gentle":
                    offset = shift_ns * min(max(0, now - 61 * ns), close - 61 * ns) // (close - 61 * ns)
                else:
                    offset = shift_ns if now >= (50 if shape == "before" else 70) * ns else 0
                return fixture.EPOCH * ns + now + offset

            def processes(self):
                rows = fixture.Fixture.processes(self)
                now = round(self.now * ns)
                if now >= birth and rate_ppm:
                    if shape == "timed":
                        period = 10_000_000
                        runtime = period * rate_ppm // 1_000_000
                        whole, tail = divmod(min(now, close) - birth, period)
                        cpu_us = (whole * runtime + max(0, tail - (period - runtime))) // 1000
                    else:
                        cpu_us = (min(now, close) - birth) * rate_ppm // ns
                    rows.append((fixture.PID, birth // ns, (cpu_us + 5000) // 10000, fixture.WORKER,
                                 "/fixture/mdworker_shared"))
                return rows

            def run(self, argv, **kwargs):
                result = super().run(argv, **kwargs)
                if shape == "timed":
                    if tuple(argv) == contention.PS_ARGV and self.now in ticks:
                        self.now = round(self.now + 0.01, 6)
                    elif tuple(argv) == prewindow.PS_ARGV and any(round(t + 0.01, 6) == self.now for t in ticks):
                        self.now = round(self.now + 0.01, 6)
                return result

        return QuietWorker

    def test_audit_r3_quiet_worker_after_a_wall_loss_withholds_as_clock_unstable(self):
        # Audit r3 (3e37db72a): a worker using at most 1.482 CPU-s in any
        # 30 s, observed at 0.01 CPU-s at 46.25 s, was refused after a
        # 450 ms wall loss at 70 s: the closing read converted its printed
        # start again and inferred a zero at 46.45 s. A 6 ms gradual loss
        # (true 30 s maximum 1.49985 CPU-s) and a 450 ms loss between birth
        # and the first sighting (lifetime check) refused too. Round 4 made
        # every quiet worker publish. Under lead K1 each of these clocks
        # moves by more than 1 ms, so every run withholds as clock_unstable.
        # With a stable clock every quiet worker publishes and 0.051 of a
        # core (1.53 CPU-s per 30 s) refuses.
        from tests.align import test_r0_vs_l3_differential as fixture

        cases = [(shape, shift, rate) for shape in ("timed",)
                 for shift in (-450_000_000, 0, 450_000_000) for rate in (49000, 49400, 51000)]
        cases += [(shape, sign * magnitude, rate)
                  for shape, magnitude, rates in (("before", 450_000_000, (49400, 49000, 0, 51000)),
                                                  ("witness", 450_000_000, (49400, 49000, 0, 51000)),
                                                  ("gentle", 6_000_000, (49995, 49650, 0, 51000)))
                  for sign in (-1, 0, 1) for rate in rates]
        for mode in ("host", "inventory"):
            for shape, shift, rate in cases:
                name = f"{mode}_{shape}_{shift}_{rate}"
                with self.subTest(case=name):
                    result, _ = self.run_model(fixture.Case(name, end=107, schedule=mode),
                                               self.quiet_worker_fixture(shape, shift, rate))
                    if shift:
                        self.assertEqual((result["rc"], result["published"]), (2, False), result)
                        self.assertIn("clock_unstable", result["reason"])
                    elif rate > 50_000:
                        self.assertEqual((result["rc"], result["published"]), (2, False), result)
                    else:
                        self.assertEqual((result["rc"], result["published"], result["flags"]), (0, True, []), result)

    def clock_witness_fixture(self, path, pid_kind, load_cs, magnitude_ns=450_000_000):
        """Audit r4 clock_witness.py, busy family.

        PID 7421 is absent from the accounting read at 45.450-46.050 s and
        from the arguments table read with it at 46.050-46.060 s. It is born
        at 46.10 s and first listed by the accounting read at 61.000-61.010
        s, whose arguments table follows until 61.040 s. One thread uses
        0.60 CPU-s from 50 s and the rest of ``load_cs`` from 68 s. The
        closing accounting read spans 75.999-76.001 s. ``path`` places a
        wall change of ``magnitude_ns``: "duringArgs" at 61.025 s (inside
        the arguments read after the first sighting), "lossBefore" (a gain
        that ends inside the absence read, before birth), "lossAfter" and
        "lateGain" at 68 s, "tinyInArgs" (10 us over 20 ms inside that
        arguments read) or "flat". TIME is rendered as Darwin ps does.
        """
        from tests.align import test_r0_vs_l3_differential as fixture

        ns = 10**9
        absent_start, birth, first, close = 45_450_000_000, 46_100_000_000, 61_000_000_000, 76_000_000_000

        def offset(t):
            return {"flat": 0, "lossBefore": magnitude_ns if t < 45_800_000_000 else 0,
                    "lossAfter": -magnitude_ns if t >= 68 * ns else 0,
                    "lateGain": magnitude_ns if t >= 68 * ns else 0,
                    "duringArgs": magnitude_ns if t >= first + 25_000_000 else 0,
                    "tinyInArgs": min(max(0, t - first - 11_000_000), 20_000_000) // 2000}[path]

        def overlap(t, start, size):
            return min(max(0, t - start), size)

        class Witness(fixture.Fixture):
            def __init__(self, case, root):
                super().__init__(case, root)
                self.ticks = [45.45, 61.0, 75.999, 91.55]

            def wall_ns(self):
                t = round(self.now * ns)
                return fixture.EPOCH * ns + t + offset(t)

            def processes(self):
                t = round(self.now * ns)
                rows = fixture.Fixture.processes(self)
                if t >= birth:
                    cpu_ns = overlap(t, 50 * ns, 600_000_000) + overlap(t, 68 * ns, load_cs * 10_000_000 - 600_000_000)
                    rows.append((fixture.PID, (birth + offset(birth)) // ns, (cpu_ns // 1000 + 5000) // 10000,
                                 fixture.WORKER, "/fixture/mdworker_shared"))
                elif pid_kind == "reuse" and t < absent_start + 300_000_000:
                    rows.append((fixture.PID, -100, 7, "ordinary", "/fixture/ordinary"))
                return rows

            def move(self, end):
                if self.case.schedule == "inventory" and end == 45 and "inventory" in self.work_started:
                    end = self.case.end
                while self.ticks and self.ticks[0] <= end:
                    self.now = self.ticks.pop(0)
                    self.apply_tree()
                    self.timer.pulse()
                self.now = end
                self.apply_tree()

            def run(self, argv, **kwargs):
                t = round(self.now * ns)
                result = super().run(argv, **kwargs)
                accounting, arguments = tuple(argv) == contention.PS_ARGV, tuple(argv) == prewindow.PS_ARGV
                if accounting and t == absent_start:
                    self.now = 46.05
                elif arguments and t == 46_050_000_000:
                    self.now = 46.06
                elif accounting and t == first:
                    self.now = 61.01
                elif arguments and t == 61_010_000_000:
                    self.now = 61.04
                elif accounting and t == close - 1_000_000:
                    self.now += .002
                elif arguments and t == close + 1_000_000:
                    self.now += .001
                return result

        return Witness

    def test_audit_r4_clock_witnesses_and_the_stable_clock_control(self):
        # Audit r4 (51a50a1aa) clock_witness.py. A 450 ms gain inside the
        # arguments read after the first sighting entered the birth
        # conversion, dated the start 45.550 s, and 1.51 CPU-s published in
        # both modes; a 10 us slew there published the 1.50 tie. Lead K1:
        # any change above 1 ms withholds as clock_unstable. K2: no offset
        # measured after the sighting's accounting read converts the start,
        # and the arguments table at 46.05 s that lists no PID 7421 is a zero
        # of its own (1.50 CPU-s within 29.95 s). With a stable clock (none,
        # 10 us, 0.5 ms, or exactly 1 ms) 1.49 CPU-s publishes and 1.50 and
        # 1.51 refuse.
        from tests.align import test_r0_vs_l3_differential as fixture

        cases = [(path, 450_000_000) for path in ("duringArgs", "lateGain", "lossBefore", "lossAfter")]
        cases += [("flat", 0), ("tinyInArgs", 0)]
        cases += [(path, 500_000) for path in ("duringArgs", "lateGain", "lossBefore", "lossAfter")]
        for mode in ("host", "inventory"):
            for path, magnitude in cases + [("lateGain", 1_000_000), ("lateGain", 1_001_000)]:
                for pid_kind in ("fresh", "reuse"):
                    for load in (149, 150, 151):
                        if magnitude in (1_000_000, 1_001_000) and (pid_kind, load) != ("fresh", 149):
                            continue
                        name = f"{mode}_{path}_{magnitude}_{pid_kind}_{load}"
                        with self.subTest(case=name):
                            result, model = self.run_model(
                                fixture.Case(name, end=107, schedule=mode),
                                self.clock_witness_fixture(path, pid_kind, load, magnitude))
                            if magnitude > 1_000_000:
                                self.assertEqual((result["rc"], result["published"]), (2, False), result)
                                self.assertIn("clock_unstable", result["reason"])
                                self.assertIn(f"{magnitude / 1000:.3f} µs", result["reason"])
                            elif load == 149:
                                self.assertEqual((result["rc"], result["published"], result["flags"]),
                                                 (0, True, []), result)
                            else:
                                self.assertEqual((result["rc"], result["published"]), (2, False), result)
                                self.assertNotIn("clock_unstable", result["reason"])
                                self.assertIn((46.05, 76.0, fixture.PID), self.exact_proofs(model.guard), result)

    def test_audit_r4_excursion_between_reads_is_withheld_not_published(self):
        # Audit r4 gentle_excursion.py. The wall gains at 500 ppm from 38.050 s
        # and loses it again by 53.950 s (peak 3.975 ms), between the reads
        # at 38 and 54 s, so every read measures a zero offset. The worker is
        # born at 45.9965 s while the wall reads 46.0005 s and prints start
        # 46. Two 12-thread bursts more than 30 s apart bound its true use
        # to 1.482 CPU-s in any 30 s; its counter reads 1.50 at 76 s. The
        # reads are those of a stable clock with a worker born in second 46,
        # whose 1.50 CPU-s within 30 s is a real tie (KNOWN LIMITATION
        # R0-CLOCK). The clock-stability precondition sees a zero range and
        # cannot report clock_unstable. R0 withholds on the exact check; it
        # never publishes. A stable clock publishes.
        from tests.align import test_r0_vs_l3_differential as fixture

        ns = 10**9
        segments = [(45_996_700_000, 45_998_200_000, 12), (50 * ns, 50_342_000_000, 1),
                    (68 * ns, 69_122_000_000, 1), (75_998_300_000, 75_999_800_000, 12)]

        def cpu(t):
            return sum(n * max(0, min(b, t) - a) for a, b, n in segments)

        ends = {t + d for a, b, _ in segments for t in (a, b) for d in (0, 30 * ns)}
        self.assertEqual(max(cpu(t) - cpu(t - 30 * ns) for t in ends), 1_482_000_000)
        self.assertEqual(cpu(76 * ns), 1_500_000_000)
        birth = 45_996_500_000

        for mode in ("host", "inventory"):
            for path in ("flat", "gentle", "flatTimed", "gentleTimed"):
                for pid_kind in ("fresh", "reuse"):
                    timed = path.endswith("Timed")
                    ticks = [t - .005 if timed else t for t in (38, 54, 76, 91)]
                    starts = {round(t * ns) for t in ticks}

                    def offset(t, path=path):
                        return 0 if path.startswith("flat") else max(0, min(t - 38_050_000_000, 53_950_000_000 - t)) // 2000

                    class Excursion(fixture.Fixture):
                        def __init__(self, case, root, ticks=ticks):
                            super().__init__(case, root)
                            self.ticks = list(ticks)

                        def wall_ns(self, offset=offset):
                            t = round(self.now * ns)
                            return fixture.EPOCH * ns + t + offset(t)

                        def processes(self, offset=offset, pid_kind=pid_kind):
                            t = round(self.now * ns)
                            rows = fixture.Fixture.processes(self)
                            if t >= birth:
                                rows.append((fixture.PID, (birth + offset(birth)) // ns, (cpu(t) // 1000 + 5000) // 10000,
                                             fixture.WORKER, "/fixture/mdworker_shared"))
                            elif pid_kind == "reuse" and t < 45_800_000_000:
                                rows.append((fixture.PID, -100, 7, "ordinary", "/fixture/ordinary"))
                            return rows

                        def move(self, end):
                            if self.case.schedule == "inventory" and end == 45 and "inventory" in self.work_started:
                                end = self.case.end
                            while self.ticks and self.ticks[0] <= end:
                                self.now = self.ticks.pop(0)
                                self.apply_tree()
                                self.timer.pulse()
                            self.now = end
                            self.apply_tree()

                        def run(self, argv, timed=timed, starts=starts, **kwargs):
                            t = round(self.now * ns)
                            if timed and tuple(argv) == contention.PS_ARGV and t in starts:
                                self.now = (t + 5_000_000) / ns  # the table is captured mid-read
                                result = super().run(argv, **kwargs)
                                self.now = (t + 10_000_000) / ns
                                return result
                            result = super().run(argv, **kwargs)
                            if timed and tuple(argv) == prewindow.PS_ARGV and t - 10_000_000 in starts:
                                self.now = (t + 5_000_000) / ns
                            return result

                    name = f"{mode}_{path}_{pid_kind}"
                    with self.subTest(case=name):
                        result, model = self.run_model(fixture.Case(name, end=107, schedule=mode), Excursion)
                        ranges = [r["wall_offset_range_us"] for r in self.series_receipts(model.guard)
                                  if "wall_offset_range_us" in r]
                        self.assertTrue(ranges and set(ranges) == {0.0}, ranges)
                        if path.startswith("flat"):
                            self.assertEqual((result["rc"], result["published"], result["flags"]), (0, True, []), result)
                        else:
                            self.assertEqual((result["rc"], result["published"]), (2, False), result)
                            self.assertNotIn("clock_unstable", result["reason"])
                            self.assertTrue(any(f.get("kind") == "exact_30s" for f in model.guard.contention_flags))

    def test_audit_r4_identical_observations_refuse_in_both_modes(self):
        # Audit r4 indistinguishable.py. Round 2's stable 1.50 tie (born at
        # 46.1 s, printed 46) and a single-thread quiet worker born at
        # 45.58 s while the wall was 450 ms ahead (printed 46; the offset
        # returns to zero before the next read) give identical process
        # tables, sampled wall and monotonic times, counters and flags. The
        # quiet worker's true maximum is 1.470 CPU-s in any 30 s. Both refuse
        # in both modes: R0 refuses, never publishes, in the ambiguous case
        # (KNOWN LIMITATION R0-CLOCK).
        from tests.align import test_r0_vs_l3_differential as fixture

        ns = 10**9
        quiet = [(45_650_000_000, 30_000_000), (51 * ns, 570_000_000), (70 * ns, 870_000_000),
                 (75_800_000_000, 30_000_000)]
        segments = [(start, start + length) for start, length in quiet]
        ends = {t + d for segment in segments for t in segment for d in (0, 30 * ns)}
        self.assertEqual(max(sum(max(0, min(e, at) - max(s, at - 30 * ns)) for s, e in segments) for at in ends),
                         1_470_000_000)
        ticks = [45.5, 61.0, 76.0, 91.5, 107.0]

        def recording(base):
            class Recorded(base):
                def __init__(self, case, root):
                    super().__init__(case, root)
                    self.seen = []

                def wall_ns(self):
                    wall = super().wall_ns()
                    self.seen.append(("wall", round(self.now * ns), wall))
                    return wall

                def run(self, argv, **kwargs):
                    result = super().run(argv, **kwargs)
                    if tuple(argv) in (tuple(prewindow.PS_ARGV), tuple(contention.PS_ARGV)):
                        self.seen.append(("table", round(self.now * ns), tuple(argv), result.stdout))
                    return result
            return Recorded

        busy = self.birth_slew_fixture(150, 0, ticks)

        class QuietTwin(busy):
            def wall_ns(self):
                now = round(self.now * ns)
                return (fixture.EPOCH * ns + now
                        + (450_000_000 * min(12 * ns, max(0, 59 * ns - now)) // (12 * ns) if now >= 45_550_000_000 else 0))

            def processes(self):
                rows = fixture.Fixture.processes(self)
                t = round(self.now * ns)
                if t >= 45_580_000_000:
                    used = sum(min(max(t - start, 0), length) for start, length in quiet)
                    rows.append((fixture.PID, (45_580_000_000 + 450_000_000) // ns, (used // 1000 + 5000) // 10000,
                                 fixture.WORKER, "/fixture/mdworker_shared"))
                return rows

        for mode in ("host", "inventory"):
            for end in (76, 107):
                outcomes = {}
                for label, base in (("busy", busy), ("quiet", QuietTwin)):
                    with self.subTest(mode=mode, end=end, worker=label):
                        result, model = self.run_model(fixture.Case(f"{mode}_{end}", end=end, schedule=mode),
                                                       recording(base))
                        self.assertEqual((result["rc"], result["published"]), (2, False), result)
                        self.assertNotIn("clock_unstable", result["reason"])
                        outcomes[label] = (model.seen, result["flags"], model.guard.contention_flags)
                with self.subTest(mode=mode, end=end, identical=True):
                    self.assertEqual(outcomes["busy"], outcomes["quiet"])

    def test_r5_narrow_check_pigeonhole_window_withholds(self):
        # Narrow check r5 stable_window.py (c0fc6fc75). A resident worker on
        # a stable clock used 1.48 CPU-s at 59 s, 0.11 at 69 s and 1.48 at
        # 79 s: 3.07 CPU-s inside 55-85 s. The daemon read it at 46, 62, 78
        # and 94 s (instantly, or for 10 ms each with 10 ms arguments
        # reads): 0.00, 1.48, 1.59, 3.07. No two reads at most 30 s apart
        # differ by 1.50, and every sliding window spans 32 s, so both modes
        # published. Lead P1: 3.06 CPU-s after rounding between 46 and
        # 94 s, at most 49 s apart, put at least 1.53 in one of two windows
        # of at most 30 s. The 1.49 CPU-s control publishes; 1.60 CPU-s in
        # 1.6 s refuses.
        from tests.align import test_r0_vs_l3_differential as fixture

        ns = 10**9
        work = {"split": ((59.0, 60.48), (69.0, 69.11), (79.0, 80.48)), "quiet": ((59.0, 60.48), (69.0, 69.01)),
                "busy": ((59.0, 60.6),)}
        ticks = (46, 62, 78, 94, 110, 126)

        def cpu_ns(t, schedule):
            return sum(max(0, min(t, round(end * ns)) - round(start * ns)) for start, end in schedule)

        for mode in ("host", "inventory"):
            for load, schedule in work.items():
                for timed in (False, True):
                    class Window(fixture.Fixture):
                        def __init__(self, case, root):
                            super().__init__(case, root)
                            self.ticks = list(ticks)

                        def move(self, end):
                            if self.case.schedule == "inventory" and end == 45 and "inventory" in self.work_started:
                                end = self.case.end
                            while self.ticks and self.ticks[0] <= end:
                                self.now = self.ticks.pop(0)
                                self.apply_tree()
                                self.timer.pulse()
                            self.now = end
                            self.apply_tree()

                        def processes(self, schedule=schedule):
                            cs = (cpu_ns(round(self.now * ns), schedule) + 5_000_000) // 10_000_000
                            return [*fixture.Fixture.processes(self),
                                    (fixture.PID, -100, cs, fixture.WORKER, "/fixture/mdworker_shared")]

                        def run(self, argv, timed=timed, **kwargs):
                            started = round(self.now * ns)
                            result = super().run(argv, **kwargs)
                            accounting = tuple(argv) == contention.PS_ARGV
                            starts = {tick * ns + (0 if accounting else 10_000_000) for tick in ticks[:-1]}
                            if timed and tuple(argv) in (contention.PS_ARGV, prewindow.PS_ARGV) and started in starts:
                                self.now = (started + 10_000_000) / ns
                            return result

                    name = f"{mode}_{load}_{'timed' if timed else 'instant'}"
                    with self.subTest(case=name):
                        result, model = self.run_model(fixture.Case(name, end=126, schedule=mode), Window)
                        if load == "quiet":
                            self.assertEqual((result["rc"], result["published"], result["flags"]), (0, True, []), result)
                            continue
                        self.assertEqual((result["rc"], result["published"]), (2, False), result)
                        if load == "split":
                            proven = [f for f in model.guard.contention_flags if f.get("kind") == "proven_30s"]
                            self.assertTrue(proven, model.guard.contention_flags)
                            self.assertIn("3.06 CPU-s after rounding from 46.000 s to "
                                          f"{94.01 if timed else 94.0:.3f} s: at least 1.530 CPU-s in one of "
                                          "2 windows of at most 30 s", proven[0]["flag"])
                            if mode == "host":
                                self.assertIn("at least 1.530 CPU-s in one of 2 windows", result["reason"])

    def test_publication_matches_an_independent_workload_model(self):
        # Lead r4 S4(c), rewritten for lead P2. Each worker has a true birth
        # and a true CPU curve; its printed start second is the simulated
        # wall clock's at birth. CPU accrues in whole centiseconds, so ps
        # prints the counter exactly (Darwin's rounding is covered by the
        # audit replays above). Truth: the curve uses at least 1.50 CPU-s
        # in some 30 s of the run.
        #
        # Loads: "quiet" (1 cs every 0.202 s: at most 1.49 in 30 s, 1.50 only
        # after 30.3 s), "busy" (1 cs every 0.19 s), "t150" / "t149" (0.01
        # CPU-s at birth, the rest 0.05 s before the read C, exactly 30 s
        # after the kind's proving opening), "split" (1.48, 0.11 and 1.48
        # CPU-s bursts 10 s apart: 3.07 within 21.5 s, the narrow check's
        # shape) and "spread" (a 1.48 CPU-s burst every 30 s: never more
        # than 1.48 in 30 s, however long the worker lives). Kinds: a
        # resident, a newcomer absent at the 45.5 s read, the same with
        # another process holding its PID there, and a newcomer whose last
        # absence is 30.1 s before C but whose printed second is 30 s before
        # it. Clocks: a wall step or slew, gain or loss, 1 us to 2 s,
        # between the last absence and the first sighting or after it.
        # Reads: instant at a 0.5 to 30 s cadence (C included), or sparse,
        # 10 ms accounting and 10 ms arguments reads 16 to 60 s apart. At
        # 16 s the resident "split" worker is the narrow check's replay: its
        # 3.07 CPU-s is proven only by P1, since every sliding window
        # averages 0.0497 CPU-s/s and no two reads 30 s apart differ by 1.50.
        #
        # Expectation, from the test's own reads alone, never from the guard:
        # - A gap above 50 s between daemon reads withholds as a stalled
        #   sampler (the existing fail-closed rule, which reports first).
        # - A wall change above 1 ms withholds as clock_unstable (R0-CLOCK).
        # - P1-provable contention withholds. Points are the worker's reads
        #   (their counters) and its birth bound's earliest instant
        #   (counter 0). The span runs from the earlier point's read start
        #   to the later read's end. The growth is less 0.01 CPU-s, split
        #   over ceil(span / 30 s) windows, and must reach 1.50 CPU-s.
        # - With instant reads, the narrower existing exact rule also
        #   withholds: two reads at most 30 s apart differing by 1.50, or
        #   1.50 at most 30 s after the earliest birth.
        # - Whatever withholds is true contention, a clock change, a stall,
        #   within 0.01 CPU-s of 1.50 with timed reads, or the admitted
        #   R0-L3 rate rule. That rule (docs/align/r0/R0-L3-contention-rule.md,
        #   required by frozen v3) flags an average above 0.05 CPU-s/s over a
        #   sampled window of at least 30 s, or over a newcomer's lifetime
        #   within one. A bursty worker such as "spread" can trip it without
        #   1.50 CPU-s in any 30 s. The test over-approximates where it can
        #   fire: two reads of the worker at least 30 s apart (midpoints)
        #   whose counters rise faster than 0.05 CPU-s/s, or a reading whose
        #   whole counter, from the birth bound to the end of that read,
        #   does, when any absence read lies at least 30 s before it.
        # - Any other worker publishes.
        from tests.align import test_r0_vs_l3_differential as fixture

        def ns(seconds):
            return round(seconds * 1e9)  # the fixture's monotonic stamps

        window = 30 * 10**9
        kinds = {"resident": (46.0, 76.0, None), "absence": (45.5, 75.5, 45.8),
                 "reused": (45.5, 75.5, 45.8), "birth": (45.9, 76.0, 46.1)}
        magnitudes = (1_000, 150_000, 10_000_000, 490_000_000, 510_000_000, 2_000_000_000)
        dense_clocks = [None] + [(shape, sign * magnitude, place) for shape in ("step", "slew") for sign in (1, -1)
                                 for magnitude in magnitudes for place in ("pre", "post")]
        sparse_clocks = [None, ("step", 150_000, "post"), ("step", -150_000, "post"), ("slew", 150_000, "pre"),
                         ("slew", -150_000, "pre"), ("step", 490_000_000, "pre"), ("step", -490_000_000, "post")]

        def bursts(*spans):
            return [(start + round(k * 1e7), 1) for start, length in spans for k in range(1, length + 1)]

        for kind, (anchor, close, birth) in kinds.items():
            for cadence, sparse in [(c, False) for c in (0.5, 2, 7.5, 15, 30)] + [(c, True) for c in (16, 20, 35, 50, 60)]:
                grid = [round(anchor + cadence * k, 3) for k in range(200)]
                if sparse:
                    ticks = [t for t in grid if t <= anchor + max(100, 2 * cadence)]
                else:
                    ticks = sorted({t for t in grid if t <= close + max(cadence, 3) + 1} | {close})
                # (start, end) of every series read; a sparse tick's read and
                # its arguments read take 10 ms each, and the publication
                # read follows the last.
                spans = [(ns(t), ns(t)) for t in (0, 15, 30)]
                spans += [(ns(t), ns(t) + (10_000_000 if sparse else 0)) for t in ticks]
                spans.append((spans[-1][1] + (10_000_000 if sparse else 0),) * 2)
                run_end = spans[-1][1]
                stalled = sparse and cadence > 50
                jump = close - 0.05
                if not sparse:
                    self.assertFalse([t for t in ticks if jump <= t < close])
                if birth is None:
                    later = min(t for t in ticks if t > anchor)
                    brackets = {"pre": (anchor, later), "post": (later, close)}
                else:
                    absent_index = max(i for i, (s, _) in enumerate(spans) if s < ns(birth))
                    absent, sighted = spans[absent_index], spans[absent_index + 1]
                    brackets = {"pre": (absent[0] / 1e9, sighted[0] / 1e9), "post": (sighted[0] / 1e9, close)}
                base = ns(59.0 if birth is None else birth + 13.2)
                for load in ("quiet", "busy", "t150", "t149", "split", "spread"):
                    start = ns(40.0 if birth is None else birth)
                    if load in ("quiet", "busy"):
                        spacing = 202_000_000 if load == "quiet" else 190_000_000
                        steps = [(start + spacing * k, 1) for k in range(1, (run_end - start) // spacing + 1)]
                    elif load in ("t150", "t149"):
                        steps = ([(ns(jump), int(load[1:]))] if birth is None
                                 else [(ns(birth) + 10_000_000, 1), (ns(jump), int(load[1:]) - 1)])
                    elif load == "split":
                        steps = bursts((base, 148), (base + 10 * 10**9, 11), (base + 20 * 10**9, 148))
                    else:
                        steps = bursts(*[(base + 30 * 10**9 * n, 148) for n in range(5)])
                    steps = [(q, c) for q, c in steps if q <= run_end]
                    best = max([sum(c for q, c in steps if at <= q < at + window) for at, _ in steps] or [0])
                    truth = best >= 150

                    def counter(t_ns, steps=steps, birth=birth):
                        if birth is not None and t_ns < ns(birth):
                            return None
                        return (230 if birth is None else 0) + sum(c for q, c in steps if q <= t_ns)

                    counts = [counter(s) for s, _ in spans]  # ps captures each table as its read starts
                    clocks = sparse_clocks if sparse else dense_clocks
                    for clock in clocks:
                        if clock is None:
                            def offset(seconds):
                                return 0
                        else:
                            shape, change, place = clock
                            t0, t1 = brackets[place]
                            if birth is not None and place == "pre" and shape == "step":
                                t0 = (birth + t1) / 2  # after the birth, before its first sighting
                            elif shape == "step" or t1 <= t0:
                                t0 = (t0 + t1) / 2

                            def offset(seconds, shape=shape, change=change, t0=t0, t1=t1):
                                if shape == "step" or t1 <= t0:
                                    return change if seconds >= t0 else 0
                                return change * min(max(ns(seconds) - ns(t0), 0), ns(t1) - ns(t0)) // (ns(t1) - ns(t0))

                        printed = (None if birth is None else
                                   (fixture.EPOCH * 10**9 + ns(birth) + offset(birth)) // 10**9 - fixture.EPOCH)
                        unstable = clock is not None and abs(clock[1]) > 1_000_000
                        diverged = clock is not None and abs(clock[1]) > 500_000_000

                        # P1 from the test's own reads.
                        points = [(s, c) for (s, _), c in zip(spans, counts) if c is not None]
                        lifetime_floor = exact_zero = None
                        if birth is not None:
                            # The arguments table read with the absence sample
                            # starts at that read's end and lists the PID only
                            # if another process holds it.
                            args_start = absent[1]
                            absence_start = absent[0] if kind == "reused" else max(absent[0], args_start)
                            absence_point = (sum(absent) // 2 if kind == "reused"
                                             else max(sum(absent) // 2, args_start))
                            offsets = [offset(absent[0] / 1e9), offset(absent[1] / 1e9),
                                       offset((absent[1] + (10_000_000 if sparse and absent_index >= 3 else 0)) / 1e9),
                                       offset(sighted[0] / 1e9), offset(sighted[1] / 1e9)]
                            converted = printed * 10**9 - max(offsets)
                            lifetime_floor = (max(absence_start, converted) if converted <= sighted[1]
                                              else absence_start)
                            exact_zero = (converted if absence_point < converted < sum(sighted) // 2
                                          else absence_point)
                        proven = False
                        for (b_start, b_end), b in zip(spans, counts):
                            if b is None:
                                continue
                            earlier = [(s, c) for (s, _), c in zip(spans, counts) if c is not None and s < b_start]
                            if lifetime_floor is not None:
                                earlier.append((lifetime_floor, 0))
                            for a_start, a in earlier:
                                span = b_end - a_start
                                windows = max(1, -(-span // window))
                                if span > 0 and b - a - 1 >= 150 * windows:
                                    proven = True
                        # Where the admitted R0-L3 rate rule can fire.
                        listed = [(s, e, c) for (s, e), c in zip(spans, counts) if c is not None]
                        l3_rate = any((sb + eb) // 2 - (sa + ea) // 2 >= window
                                      and (cb - ca) * 10**9 > 5 * ((sb + eb) // 2 - (sa + ea) // 2)
                                      for i, (sa, ea, ca) in enumerate(listed) for sb, eb, cb in listed[i + 1:])
                        if lifetime_floor is not None:
                            absences = [(s + e) // 2 for (s, e), c in zip(spans, counts) if c is None]
                            l3_rate = l3_rate or any(any((sb + eb) // 2 - a >= window for a in absences)
                                                     and cb * 10**9 > 5 * (eb - lifetime_floor)
                                                     for sb, eb, cb in listed)
                        exact = False
                        if not sparse:
                            exact = any(b - a >= 150 for i, (ta, a) in enumerate(points)
                                        for tb, b in points[i + 1:] if tb - ta <= window)
                            if exact_zero is not None:
                                exact = exact or any(b >= 150 and 0 <= tb - exact_zero <= window for tb, b in points)
                        if not unstable:
                            # The rules never prove contention that did not happen.
                            self.assertTrue(truth or not proven, (kind, cadence, load, clock))
                            self.assertTrue(truth or not exact, (kind, cadence, load, clock))
                        if load == "spread":
                            self.assertEqual(best, 148)
                        if load in ("busy", "split") and not sparse and not unstable:
                            self.assertTrue(proven or exact, (kind, cadence, load, clock))

                        def rows(now, counter=counter, kind=kind, printed=printed):
                            cpu = counter(ns(now))
                            if cpu is not None:
                                yield (fixture.PID, -100 if printed is None else printed, cpu, fixture.WORKER,
                                       "/fixture/mdworker_shared")
                            elif kind == "reused":
                                yield fixture.PID, -100, 7, "ordinary", "/fixture/ordinary"

                        class Clocked(self.series_fixture(ticks, rows)):
                            def wall_ns(self, offset=offset):
                                return fixture.EPOCH * 10**9 + ns(self.now) + offset(self.now)

                            def run(self, argv, sparse=sparse, **kwargs):
                                started = ns(self.now)
                                result = super().run(argv, **kwargs)
                                if sparse and started in self.reads_at.get(tuple(argv), ()):
                                    self.now = (started + 10_000_000) / 1e9
                                return result

                        Clocked.reads_at = {tuple(contention.PS_ARGV): {ns(t) for t in ticks},
                                            tuple(prewindow.PS_ARGV): {ns(t) + 10_000_000 for t in ticks}}
                        label = dict(kind=kind, cadence=cadence, load=load, clock=clock)
                        with self.subTest(**label):
                            result, model = self.run_model(fixture.Case(f"{kind}_{load}", end=ticks[-1]), Clocked)
                            withheld = (result["rc"], result["published"]) == (2, False)
                            if stalled:
                                self.assertTrue(withheld, result)
                                self.assertIn("stalled", result["reason"])
                            elif unstable:
                                self.assertTrue(withheld, result)
                                self.assertIn("clock_unstable", result["reason"])
                                self.assertEqual(bool([f for f in model.guard.contention_flags
                                                       if f.get("kind") == "wall_clock"]), diverged, result)
                            elif proven or exact:
                                self.assertTrue(withheld, result)
                            elif not (truth or l3_rate or (sparse and best >= 149)):
                                self.assertEqual((result["rc"], result["published"], result["flags"]),
                                                 (0, True, []), result)


class R0AccountingTimezoneTest(unittest.TestCase):
    trial = R0PublicationAuditTest.trial

    def in_zone(self, zone, expression):
        import os
        import sys
        import time

        if not hasattr(time, "tzset"):
            self.skipTest("requires time.tzset")
        program = ("import json, time\n"
                   "from tests.align.test_r0_host import R0AccountingTimezoneTest as Test\n"
                   "time.tzset()\n"
                   f"print(json.dumps({expression}))\n")
        output = subprocess.check_output([sys.executable, "-B", "-c", program], text=True,
                                         env={**os.environ, "TZ": zone, "LC_ALL": "C"})
        return json.loads(output)

    def test_repeated_hour_report_and_inventory_match_utc(self):
        expected = {"quiet": [0, True, 0], "worker_180": [2, False, 3], "worker_225": [2, False, 3],
                    "resident_180": [2, False, 3], "terminal_180": [2, False, 1],
                    "second_live": [2, False, 3], "local-hour": [2, False, 3]}
        for zone, utc in (("America/Los_Angeles", "2026-11-01T09:15:00+00:00"),
                          ("America/New_York", "2026-11-01T06:15:00+00:00"),
                          ("Australia/Lord_Howe", "2026-04-04T15:15:00+00:00")):
            with self.subTest(zone=zone):
                expression = f"Test().repeated_hour_cases({utc!r})"
                baseline = self.in_zone("UTC", expression)
                self.assertEqual(baseline, expected)
                self.assertEqual(self.in_zone(zone, expression), baseline)

    def repeated_hour_cases(self, utc):
        """Synthetic Darwin ps prints lstart in the environment of each call."""
        import os
        from datetime import datetime, timezone
        from zoneinfo import ZoneInfo
        from tests.align import test_r0_vs_l3_differential as fixture

        epoch = int(datetime.fromisoformat(utc).timestamp())
        self.assertEqual(datetime.fromtimestamp(epoch, ZoneInfo(os.environ["TZ"])).fold,
                         int(os.environ["TZ"] != "UTC"))
        probes = set()

        class LocalPS(fixture.Fixture):
            def wall_ns(self):
                return epoch * 10**9 + round(self.now * 10**9)

            def move(self, end):
                if self.case.schedule == "inventory" and end == 45 and "inventory" in self.work_started:
                    end = self.case.end
                super().move(end)

            def processes(self):
                rows = super().processes()
                name = self.case.name
                if name == "quiet":
                    return rows
                if name in ("second_live", "local-hour"):
                    birth, size, ramp = 35, 180, 6
                else:
                    kind, size = name.split("_")
                    birth, size, ramp = (61 if kind == "terminal" else 41), int(size), 4
                    if kind == "worker" and self.now >= 48:
                        return rows
                if self.now >= birth:
                    cpu = round(size * min(1, (self.now - birth) / ramp))
                    rows.append((fixture.PID, birth, cpu, fixture.WORKER, "/fixture/mdworker_shared"))
                return rows

            def run(self, argv, **kwargs):
                result = super().run(argv, **kwargs)
                env = kwargs.get("env", os.environ)
                probes.add((tuple(argv[:2]), env.get("TZ"), env.get("LC_ALL")))
                if tuple(argv) == contention.PS_ARGV:
                    zone = ZoneInfo(env["TZ"])
                    fmt = "%a %b %d %H:%M:%S %Y"
                    for _, born, _, _, _ in self.processes():
                        original = datetime.fromtimestamp(fixture.EPOCH + born, timezone.utc).strftime(fmt)
                        printed = datetime.fromtimestamp(epoch + born, zone).strftime(fmt)
                        result.stdout = result.stdout.replace(original, printed)
                return result

        outcomes = {}
        for name in ("quiet", "worker_180", "worker_225", "resident_180", "terminal_180",
                     "second_live", "local-hour"):
            schedule = "inventory" if name == "local-hour" else "host"
            result = self.trial(fixture.Case(name, end=65, schedule=schedule), factory=LocalPS)
            outcomes[name] = result["rc"], result["published"], result["guard_count"]
        self.assertEqual({argv[0] for argv, _, _ in probes}, {"/bin/ps", "/usr/bin/pgrep", "/bin/launchctl"})
        for argv, tz, locale in probes:
            self.assertEqual((tz, locale), ("UTC", "C"), argv)
        return outcomes

    def test_r0_parse_uses_utc_even_after_warming_the_local_caches(self):
        utc, local = self.in_zone("America/Los_Angeles", "Test().parse_fixed_utc_row()")
        self.assertEqual(utc, 1793524500)  # 2026-11-01 09:15:00 UTC
        self.assertEqual(local, utc + 8 * 3600)

    def parse_fixed_utc_row(self):
        from datetime import timezone

        start = "Sun Nov 1 09:15:00 2026"
        key = (7421, start)
        table = cpu_table((7421, start, "0:01.80", "mdworker_shared"))
        local = contention.parse(table.encode())[key]["start_epoch_s"]

        def run(argv, **kwargs):
            if argv == contention.PS_ARGV:
                self.assertEqual(kwargs["env"]["TZ"], "UTC")
                return subprocess.CompletedProcess(argv, 0, table, "")
            return subprocess.CompletedProcess(argv, 0, "1 0.0 /sbin/launchd\n", "")

        guard = QuietGuard([], run=run, clock=lambda: 0, wall_clock_ns=lambda: 1793524500 * 10**9,
                           host_reader=None)
        snapshot, _ = guard._read_cpu_snapshot(include_host=False)
        utc = snapshot.rows[key]["start_epoch_s"]
        self.assertEqual(contention.parse(table.encode())[key]["start_epoch_s"], local)
        different_line = cpu_table((7421, start, "0:01.81", "mdworker_shared"))
        self.assertEqual(contention.parse(different_line.encode(), tz=timezone.utc)[key]["start_epoch_s"], utc)
        return utc, local

    def test_command_display_and_smc_subprocesses_request_utc(self):
        from joulewise.align import r0_host

        result = subprocess.CompletedProcess([], 0, "", "")
        with tempfile.TemporaryDirectory() as tmp, patch.dict("os.environ", {"TZ": "America/New_York"}):
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts/align_smc_enumerate.py").touch()
            with patch.object(subprocess, "run", return_value=result) as run:
                r0_host.command(("fixture",))
                r0_host.display_census(0, 1, run=run)
                r0_host.smc_enumeration(root, root / "output")
            self.assertEqual(run.call_count, 4)
            for call in run.call_args_list:
                env = call.kwargs["env"]
                self.assertEqual((env["TZ"], env["LC_ALL"]), ("UTC", "C"), call.args[0])

    def test_r0_time_conversions_use_explicit_timezones(self):
        import ast
        from joulewise.align import r0_host

        def name(node):
            return node.attr if isinstance(node, ast.Attribute) else None

        for path in sorted(Path(r0_host.__file__).parent.glob("r0_*.py")) + [Path(contention.__file__)]:
            tree = ast.parse(path.read_text())
            for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
                location = f"{path.name}:{call.lineno}"
                method = name(call.func)
                self.assertNotEqual(method, "mktime", location)
                if method == "fromtimestamp":
                    self.assertTrue(len(call.args) == 2 or any(k.arg == "tz" for k in call.keywords), location)
                elif method == "timestamp":
                    receiver = call.func.value
                    self.assertIsInstance(receiver, ast.Call, location)
                    if name(receiver.func) == "strptime":
                        self.assertIn("%z", receiver.args[1].value, location)
                    else:
                        self.assertEqual(name(receiver.func), "replace", location)
                        self.assertTrue(any(k.arg == "tzinfo" for k in receiver.keywords), location)
                elif method == "parse" and isinstance(call.func.value, ast.Name) and call.func.value.id == "contention":
                    self.assertTrue(any(k.arg == "tz" and ast.unparse(k.value) == "timezone.utc"
                                        for k in call.keywords), location)


class R0ProcessIdentityTest(unittest.TestCase):
    """Audit round 2 MED: the arguments table's PID is not a process identity."""
    trial = R0PublicationAuditTest.trial
    assert_withheld = R0PublicationAuditTest.assert_withheld

    def tables(self, rows, *, slow_reads=(45, 46), wall_step=None):
        """Frozen-suite fixture with extra rows; ps reads in ``slow_reads`` take 10 ms.

        ``wall_step`` is (fixture time, seconds): the wall clock steps then.
        ``rows`` prints the start of a process born later on the stepped clock.
        """
        from tests.align import test_r0_vs_l3_differential as fixture

        def stepped(at):
            return wall_step[1] if wall_step and at >= wall_step[0] else 0

        class Tables(fixture.Fixture):
            def __init__(self, case, root):
                super().__init__(case, root)
                self.log = []

            def wall_ns(self):
                return int((fixture.EPOCH + self.now + stepped(self.now)) * 1_000_000_000)

            def processes(self):
                return [*super().processes(), *rows(self.case, self.now)]

            def run(self, argv, **kwargs):
                start = self.now
                reply = super().run(argv, **kwargs)
                if slow_reads[0] <= start < slow_reads[1] and tuple(argv) in (contention.PS_ARGV, prewindow.PS_ARGV):
                    self.log.append((round(start, 3), argv[-1], reply.stdout.strip().splitlines()[-1]))
                    self.now += 0.01
                return reply

        return Tables

    def run_tables(self, case, tables):
        models = []

        def factory(case, root):
            models.append(tables(case, root))
            return models[-1]

        return self.trial(case, factory=factory), models[0]

    def test_audit2_exited_worker_is_flagged_when_its_pid_had_an_earlier_holder(self):
        # Audit round 2 exited.py. The census sees `python3 mdworker_task.py`,
        # accounting reads 1.80 CPU-s for the PID, and the worker is gone
        # before the paired arguments read. "reused": the PID belonged to an
        # ordinary process until 20 s.
        from tests.align import test_r0_vs_l3_differential as fixture

        def rows(case, now):
            if case.name == "reused" and now < 20:
                yield (fixture.PID, -100, 0, "ordinary", "ordinary")
            if 35 <= now < 45.015:
                yield (fixture.PID, 35, 180, "python3", "python3 mdworker_task.py")

        results = {}
        for name in ("fresh", "reused"):
            with self.subTest(case=name):
                result, model = self.run_tables(fixture.Case(name, end=65), self.tables(rows))
                self.assertEqual([(at, table.split(",")[-1], row.split()[0]) for at, table, row in model.log], [
                    (45, "args=", str(fixture.PID)), (45.01, "ucomm", str(fixture.PID)), (45.02, "args=", "1")])
                self.assertIn("0:01.80 python3", model.log[1][2])
                self.assert_withheld(result)
                windows = [(start, end) for start, end, pid, _ in result["flags"] if pid == fixture.PID]
                self.assertEqual(windows, [(15.0, 45.015), (30.0, 60.0), (30.0, 65.0)], result)
                self.assertEqual(len({birth for *_, birth in result["flags"]}), 1)
                self.assertIn((15.0, 45.015), result["report_intervals"])
                results[name] = result
        self.assertEqual(results["reused"]["flags"], results["fresh"]["flags"])
        self.assertEqual(results["reused"]["judged_windows"], results["fresh"]["judged_windows"])

    def test_later_holder_of_a_pid_cannot_stretch_an_exited_workers_lifetime(self):
        # The mirror image. The worker is listed once, at the 15 s baseline
        # midpoint, with 0.60 CPU-s after a start at 5 s, and exits. A new
        # process takes the PID before the paired arguments read, so that
        # table still lists the PID. The worker's lifetime ends before the
        # holder's start second (15 s) does: 0.60 / 11 s is above 0.05.
        # Stretched to the next accounting read it would be 0.60 / 25 s.
        from tests.align import test_r0_vs_l3_differential as fixture

        def rows(case, now):
            growth = int(case.name.rsplit("_", 1)[1])
            if 5 <= now < 15.005:
                yield (fixture.PID, 5, growth if now >= 10 else 0, fixture.WORKER, fixture.WORKER)
            elif now >= 15.005 and "reused" in case.name:
                yield (fixture.PID, 15, 0, "ordinary", "ordinary")

        # reused_55: the holder's start second leaves the worker up to 16 s,
        # and 0.55 / 11 s ties the limit. lstart cannot place it more finely.
        for name, busy in (("exited_60", True), ("reused_60", True), ("reused_55", False), ("exited_50", False)):
            with self.subTest(case=name):
                result, model = self.run_tables(fixture.Case(name, end=40),
                                                self.tables(rows, slow_reads=(15, 16)))
                listed = [row.split()[0] == str(fixture.PID) for _, _, row in model.log]
                self.assertEqual(listed, [True, "reused" in name])
                if busy:
                    self.assert_withheld(result)
                    self.assertIn((0.0, 30.02, fixture.PID), [flag[:3] for flag in result["flags"]], result)
                    self.assertIn((0.0, 30.02), result["report_intervals"])
                else:
                    self.assertEqual((result["rc"], result["published"], result["flags"]), (0, True, []), result)

    def test_later_holder_bounds_the_lifetime_after_an_earlier_wall_step(self):
        # The same history after the wall clock stepped back 5 s at 10 s,
        # before the worker's only row and before the holder's birth. The
        # holder's start is dated on the clock of the worker's last row, so
        # the bound still holds. The worker printed 5 s on the clock before
        # the step; its birth bound (absent at 0 s, first listed at 15 s)
        # converts that second with the larger bracket offset, 5.0 s. So
        # 0.90 / 11 s flags and 0.55 / 11 s ties. Without the holder's
        # bound, 0.90 / 25 s would not flag.
        from tests.align import test_r0_vs_l3_differential as fixture

        def rows(case, now):
            growth = int(case.name.rsplit("_", 1)[1])
            if 5 <= now < 15.005:
                yield (fixture.PID, 5, growth if now >= 10 else 0, fixture.WORKER, fixture.WORKER)
            elif now >= 15.005 and "reused" in case.name:
                yield (fixture.PID, 15.005 - 5, 0, "ordinary", "ordinary")

        # The step itself flags the 0-30 s window and withholds every run
        # (lead ruling after audit 3). What differs is the worker's flag.
        for name, busy in (("exited_90", True), ("reused_90", True), ("reused_55", False)):
            with self.subTest(case=name):
                result, model = self.run_tables(fixture.Case(name, end=40), self.tables(
                    rows, slow_reads=(15, 16), wall_step=(10, -5)))
                self.assert_withheld(result)
                self.assertIn((0.0, 30.02), [(f["interval"]["start_monotonic_s"], f["interval"]["end_monotonic_s"])
                                             for f in model.guard.contention_flags if f.get("kind") == "wall_clock"])
                if busy:
                    self.assertIn((0.0, 30.02, fixture.PID), [flag[:3] for flag in result["flags"]], result)
                else:
                    self.assertEqual(result["flags"], [], result)

    def test_arguments_only_pid_sighting_reads_the_same_as_an_argument_change(self):
        # Resolved for PR #824: a PID listed by the arguments table alone does
        # not end the earlier worker's lifetime. The worker is listed once by
        # accounting, at the 15 s baseline midpoint, with 0.60 CPU-s after a
        # start at 5 s.
        #   transient     it exits and another process holds the PID for half
        #                 a second, so only the paired arguments read lists it
        #   same_process  it changes its arguments, keeps PID and start, and
        #                 idles until 29.9 s
        # ps -Ao pid=,pcpu=,args= prints no start, so every table is the same
        # in both. The lifetime runs to the first confirmed absence at 30 s:
        # 0.60 / 25 s is below 0.05 and both publish.
        #   confirmed     the later holder stays, and accounting lists it at
        #                 30 s with another start. Its start second ends at
        #                 16 s: 0.60 / 11 s is above 0.05.
        from tests.align import test_r0_vs_l3_differential as fixture

        def rows(case, now):
            if 5 <= now < 15.005:
                yield (fixture.PID, 5, 60 if now >= 10 else 0, fixture.WORKER, fixture.WORKER)
            elif case.name == "transient" and 15.005 <= now < 15.5:
                yield (fixture.PID, 15, 0, "ordinary", "ordinary")
            elif case.name == "same_process" and 15.005 <= now < 29.9:
                yield (fixture.PID, 5, 60, "ordinary", "ordinary")
            elif case.name == "confirmed" and now >= 15.005:
                yield (fixture.PID, 15, 0, "ordinary", "ordinary")

        class Recorded(self.tables(rows, slow_reads=(15, 16))):
            def __init__(self, case, root):
                super().__init__(case, root)
                self.replies = []

            def run(self, argv, **kwargs):
                reply = super().run(argv, **kwargs)
                self.replies.append((tuple(argv), reply.returncode, reply.stdout, reply.stderr))
                return reply

        def disclosed(model):
            return [(row["cpu_s"], row["cpu_s_per_s"]) for receipt in model.guard.receipts
                    for key in ("cpu_intervals", "admission_cpu_intervals")
                    for interval in receipt.get(key, ())
                    for row in interval["contaminants"] if row["pid"] == fixture.PID]

        outcomes = {}
        for name in ("transient", "same_process", "confirmed"):
            result, model = self.run_tables(fixture.Case(name, end=40), Recorded)
            # Accounting at 15.00 lists the worker; the arguments read at 15.01 lists the PID.
            self.assertIn("0:00.60 mdworker_shared", model.log[0][2])
            self.assertEqual(model.log[1][2], f"{fixture.PID} 0.0 ordinary")
            outcomes[name] = result, model

        (transient, first), (same_process, second), (confirmed, third) = outcomes.values()
        self.assertEqual(first.replies, second.replies)
        self.assertGreater(len(first.replies), 20)
        self.assertNotEqual(first.replies, third.replies)
        for result, model in ((transient, first), (same_process, second)):
            self.assertEqual((result["rc"], result["status"], result["published"], result["flags"]),
                             (0, "pass", True, []), result)
            rates = disclosed(model)
            self.assertTrue(rates)
            for cpu_s, rate in rates:
                # The worker's observed CPU is kept, over 5 s to 30.02 s.
                self.assertEqual(cpu_s, 0.6)
                self.assertAlmostEqual(rate, 0.6 / 25.02, places=9)
        for key in ("rc", "status", "published", "flags", "judged_windows", "accepted", "work_started",
                    "report_intervals", "recorded", "guard_count", "refused_at"):
            self.assertEqual(transient[key], same_process[key], key)
        self.assertEqual(disclosed(first), disclosed(second))

        self.assert_withheld(confirmed)
        self.assertIn((0.0, 30.02, fixture.PID), [flag[:3] for flag in confirmed["flags"]], confirmed)
        self.assertIn((0.0, 30.02), confirmed["report_intervals"])
        self.assertIn("mdworker_shared 0.0545455 CPU-s/s", confirmed["reason"])
        for cpu_s, rate in disclosed(third):
            self.assertEqual(cpu_s, 0.6)
            self.assertAlmostEqual(rate, 0.6 / 11, places=9)

    def test_arguments_sighting_before_the_first_accounting_row_names_the_process(self):
        # Born between the 45 s accounting read and its arguments read, the
        # process is named only in that arguments table. It then replaces its
        # arguments (exec keeps PID and start). Accounting first lists it at
        # 60 s with 1.80 CPU-s, after a census that shows the neutral name.
        from tests.align import test_r0_vs_l3_differential as fixture

        def rows(case, now):
            if now >= 45.015:
                named = case.name == "named_once" and now < 50
                yield (fixture.PID, 45, 180 if now >= 55 else 0, "python3",
                       "python3 mdworker_task.py" if named else "python3 other.py")

        result, model = self.run_tables(fixture.Case("named_once", end=65), self.tables(rows))
        self.assertEqual([row.split()[0] == str(fixture.PID) for _, _, row in model.log], [False, False, True])
        self.assert_withheld(result)
        self.assertIn((30.0, 60.0, fixture.PID), [flag[:3] for flag in result["flags"]], result)

        result, _ = self.run_tables(fixture.Case("never_named", end=65), self.tables(rows))
        self.assertEqual((result["rc"], result["published"], result["flags"]), (0, True, []), result)

    def test_earlier_holders_name_does_not_follow_the_pid_to_a_later_process(self):
        # A named worker holds the PID until 5 s without using CPU. An
        # ordinary process started at 10 s under the same PID uses 1.80
        # CPU-s: its start second begins after every sighting of the worker,
        # and accounting has the worker on record, so it is not a contaminant.
        from tests.align import test_r0_vs_l3_differential as fixture

        def rows(case, now):
            if now < 5:
                yield (fixture.PID, -100, 0, "python3", "python3 mdworker_task.py")
            elif now >= 10:
                name = fixture.WORKER if case.name == "worker_again" else "ordinary"
                yield (fixture.PID, 10, 180 if now >= 20 else 0, name, name)

        result, _ = self.run_tables(fixture.Case("ordinary_successor", end=40), self.tables(rows))
        self.assertEqual((result["rc"], result["published"], result["flags"]), (0, True, []), result)

        result, _ = self.run_tables(fixture.Case("worker_again", end=40), self.tables(rows))
        self.assert_withheld(result)
        self.assertIn((0.0, 30.0, fixture.PID), [flag[:3] for flag in result["flags"]], result)

    def test_later_process_is_cleared_only_by_a_start_second_after_the_sighting(self):
        # A resident worker without CPU exits at 30.5 s; its last arguments
        # sighting is the 30 s census. An ordinary process born later under
        # the PID uses 1.80 CPU-s by 40 s.
        from tests.align import test_r0_vs_l3_differential as fixture

        def rows(case, now):
            kind, born = case.name.split("_")
            if kind != "alone" and now < 30.5:
                yield (fixture.PID, -100, 0, fixture.WORKER, fixture.WORKER)
            if now >= float(born):
                # After the step the kernel dates a new process on the stepped clock.
                printed = float(born) - 5 if kind == "stepped" else float(born)
                yield (fixture.PID, printed, 180 if now >= 42 else 0, "ordinary", "ordinary")

        # 31.0 and 31.9 print start second 31, after the sighting at 30.0.
        # 30.6 prints second 30, which holds the sighting: lstart cannot
        # tell that process from the one sighted, and the name stays.
        for name, named in (("succ_31.9", False), ("succ_31.0", False), ("succ_30.6", True), ("alone_30.6", False)):
            with self.subTest(case=name):
                result, _ = self.run_tables(fixture.Case(name, end=65), self.tables(rows, slow_reads=(0, 0)))
                if named:
                    self.assert_withheld(result)
                    self.assertIn("ordinary", result["reason"])
                else:
                    self.assertEqual((result["rc"], result["published"], result["flags"]), (0, True, []), result)

        # A 5 s backward wall step at 35 s, after the sighting. The process
        # born at 40 s clears the sighting by more than the step, so no
        # process is flagged. The step flags its windows and withholds the run.
        result, model = self.run_tables(fixture.Case("stepped_40", end=65), self.tables(
            rows, slow_reads=(0, 0), wall_step=(35, -5)))
        self.assert_withheld(result)
        self.assertEqual(result["flags"], [], result)
        self.assertNotIn("ordinary", result["reason"])
        self.assertTrue(all(f.get("kind") == "wall_clock" for f in model.guard.contention_flags))
        self.assertTrue(model.guard.contention_flags)

    def test_later_workers_name_does_not_reach_back_to_an_earlier_process(self):
        # An ordinary process uses 0.60 CPU-s and exits at 32.599 s. A named
        # worker is born under the PID one millisecond later and is first
        # sighted by the 45 s census. Its start second ends at 33 s, which
        # bounds the ordinary process to 0.06 CPU-s/s; the sighting began
        # twelve seconds after that and is not the ordinary process's.
        from tests.align import test_r0_vs_l3_differential as fixture

        def rows(case, now):
            if 23.6 <= now < 32.599:
                name = fixture.WORKER if case.name == "earlier_worker" else "ordinary"
                yield (fixture.PID, 23.6, 60 if now >= 26 else 0, name, name)
            elif 32.6 <= now < 47:
                yield (fixture.PID, 32.6, 0, fixture.WORKER, fixture.WORKER)

        result, _ = self.run_tables(fixture.Case("earlier_ordinary", end=65), self.tables(rows, slow_reads=(0, 0)))
        self.assertEqual((result["rc"], result["published"], result["flags"]), (0, True, []), result)

        # The same earlier process as a named worker is flagged on that bound.
        result, _ = self.run_tables(fixture.Case("earlier_worker", end=65), self.tables(rows, slow_reads=(0, 0)))
        self.assert_withheld(result)
        self.assertIn((15.0, 45.0, fixture.PID), [flag[:3] for flag in result["flags"]], result)

    def test_sighting_without_another_holder_on_record_stays_with_the_pid(self):
        # An args-named process is listed only by the 0 s arguments read and
        # never by accounting. A second process takes the PID at 5 s, reaches
        # 1.80 CPU-s and is listed once by accounting at 15 s; its own
        # arguments are never read. Accounting has no other holder to give
        # the sighting to, so it stays with this row, as on 9ed986bec.
        from tests.align import test_r0_vs_l3_differential as fixture

        def rows(case, now):
            if 0.015 <= now < 2:
                yield (fixture.PID, 0.015, 0, "python3", fixture.ARG_WORKER)
            if 5 <= now < 15.035:
                yield (fixture.PID, 5, 180 if now >= 10 else 0, "python3", fixture.ARG_WORKER)

        class Baseline(self.tables(rows, slow_reads=(0, 1))):
            def run(self, argv, **kwargs):
                start = self.now
                reply = super().run(argv, **kwargs)
                if 15 <= start < 16 and tuple(argv) in (contention.PS_ARGV, prewindow.PS_ARGV):
                    self.now += 0.01
                return reply

        result, _ = self.run_tables(fixture.Case("unowned_sighting", end=40), Baseline)
        self.assert_withheld(result)
        self.assertIn("python3", result["reason"])
        self.assertTrue(any(flag[2] == fixture.PID and flag[1] < 31 for flag in result["flags"]), result)

    def test_printed_start_proves_a_later_birth_only_beyond_any_clock_shift(self):
        from joulewise.align.r0_host import _born_after

        def read(started_s, finished_s, wall_offset_s=1_000):
            stamp = lambda at: SimpleNamespace(monotonic_ns=int(at * 1e9), wall_ns=int((at + wall_offset_s) * 1e9))
            return SimpleNamespace(started=stamp(started_s), finished=stamp(finished_s))

        row = {"start_epoch_s": 1_010.0}  # monotonic 10 s on the default offset
        reference, listing = read(0, 0.01), read(15, 15.01)
        self.assertTrue(_born_after(row, listing, int(9.999e9), reference))
        # lstart is the floor of the start: a sighting inside that second
        # could have listed the process.
        self.assertFalse(_born_after(row, listing, int(10e9), reference))
        self.assertFalse(_born_after(row, listing, int(12e9), reference))
        # A 2 s wall step between the reference and the listing moves the
        # printed start by up to 2 s: the start must clear the instant by it.
        back, forward = read(15, 15.01, 998), read(15, 15.01, 1_002)
        for stepped, floor_s in ((back, 12), (forward, 8)):
            self.assertFalse(_born_after(row, stepped, int((floor_s - 2) * 1e9), reference))
            self.assertTrue(_born_after(row, stepped, int((floor_s - 2.001) * 1e9), reference))
        # No reference, or a start dated after its own listing: no proof.
        self.assertFalse(_born_after(row, listing, int(9e9), None))
        self.assertFalse(_born_after({"start_epoch_s": 1_016.0}, listing, int(9e9), reference))

    def test_history_is_kept_per_identity_across_pid_reuse(self):
        # Two holders of PID 42 alternate in the tables. Each keeps its own
        # peak counter and classification.
        guard = QuietGuard([], run=lambda *a, **k: None, inspect_custody=lambda **kw: Census(), host_reader=None)
        self.addCleanup(guard.close)
        stamp = SimpleNamespace(monotonic_ns=0, wall_ns=1_800_000_000_000_000_000)

        def remember(start, cpu, matches):
            row = {"pid": 42, "start_identity": start, "start_epoch_s": 0.0, "command": "fixture",
                   "cumulative_cpu_seconds": cpu, "contaminant_matches": list(matches)}
            snapshot = SimpleNamespace(rows={(42, start): row}, started=stamp, finished=stamp)
            guard._remember_cpu_snapshot(snapshot, census_summary=None, admission=True)
            return row

        remember(OLD_START, 1.8, ["ucomm"])
        other = remember(NEW_START, 0.2, [])
        self.assertEqual((other["contaminant"], other.get("peak_cpu_seconds")), (False, None))
        again = remember(OLD_START, 0.0, [])
        self.assertEqual((again["contaminant_matches"], again["peak_cpu_seconds"]), (["ucomm"], 1.8))
        self.assertEqual(guard._process_history[42][NEW_START], (0.2, set()))


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
                named = {line.split()[0] for line in args.splitlines() if line.strip()}
                # Keep each accounting PID visible to the arguments read.
                # Neutral arguments leave its classification to accounting.
                sample = latest[1] if isinstance(latest, tuple) else latest
                if isinstance(sample, str):
                    for line in sample.splitlines()[1:]:
                        pid = line.split()[0]
                        if pid != "1" and pid not in named:
                            args += f"{pid} 0.0 fixture-resident\n"
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
        # A wall clock that moves with the fake monotonic clock. Its origin
        # is hours after OLD_START and NEW_START. Tests that need another
        # wall clock replace guard.wall_clock_ns.
        from datetime import datetime
        wall0 = datetime(2026, 11, 7, 0, 0, 0).timestamp()
        guard = guard_type([], run=run, inspect_custody=lambda **kw: Census(),
                           clock=clock, sleep=clock.sleep, host_reader=None,
                           wall_clock_ns=lambda: int((wall0 + clock()) * 1e9))
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

    def test_short_respawn_bursts_use_the_observed_lifetime(self):
        # Each synthetic worker was born 0.6 s before the closing sample
        # and used 0.6 CPU-s. The %CPU field is separate from this rate.
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
                with patch.object(guard, "wall_clock_ns",
                           side_effect=lambda: int((wall_end - 60 + clock()) * 1e9)):
                    guard.check(force=True)
                    clock.now = 60
                    self.assert_flagged(guard, f"{pid} {name} 1 CPU-s/s")
                self.assertEqual(len(calls), 4)  # 3 admission + 1 daemon
                entry = guard.receipts[-1]["cpu_interval"]["contaminants"][0]
                self.assertEqual((entry["pid"], entry["lstart"], entry["name"]),
                                 (pid, " ".join(NEW_START.split()), name))
                self.assert_rate(entry["cpu_s_per_s"], 1.0, 0.6)
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
                with patch.object(guard, "wall_clock_ns",
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
        guard, clock, _ = self.guard([cpu_table(), cpu_table((42, NEW_START, "0:01.60", "photoanalysisd"))])
        from datetime import datetime
        wall = datetime(2026, 11, 6, 18, 5, 15).timestamp()
        with patch.object(guard, "wall_clock_ns",
                   side_effect=lambda: int((wall + clock()) * 1e9)):
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
                with patch.object(guard, "wall_clock_ns", side_effect=lambda: int(
                        (datetime(2026, 11, 6, 18, 5, 0).timestamp() + clock()) * 1e9)):
                    if refuses:  # R0-L3: flagged, not refused
                        self.assert_flagged(guard, "mdworker_shared.*CPU-s/s")
                    else:
                        guard.check(force=True)
                        self.assert_rate(guard.receipts[-1]["cpu_interval"]["contaminants"][0]["cpu_s_per_s"],
                                         0.04, 15)

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

    def test_exit_without_new_growth_keeps_only_the_previous_flag(self):
        guard, clock, _ = self.guard([
            cpu_table((42, OLD_START, "0:00.00", "mdworker_shared")),
            cpu_table((42, OLD_START, "0:01.80", "mdworker_shared")), cpu_table()])
        self.assert_flagged(guard, "mdworker_shared")
        clock.now = 60
        receipt = {}
        self.assertEqual(guard._cpu_interval(receipt), [])
        self.assertEqual(receipt["cpu_interval"]["exited_over_limit"], [])
        flag, = rule_flags(guard)
        self.assertEqual(flag["interval"]["end_monotonic_s"], 30)

    def test_exit_delta_uses_growth_since_opening_for_same_worker(self):
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
        interval = guard.receipts[-1]["cpu_interval"]
        self.assertEqual(interval["start_monotonic_s"], 45)
        self.assertEqual(interval["contaminants"], [])
        carried, = [flag for flag in guard.contention_flags if flag["interval"]["end_monotonic_s"] == 75]
        self.assertEqual(carried["interval"]["start_monotonic_s"], 30)
        self.assertIn("previous interval", carried["busy"][0]["basis"])

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

    def test_contaminant_regression_discloses_drop_and_carries_admitted_flag(self):
        # (0.05 + 0.01) * 30 = 1.80 CPU-s, then TIME drops to zero.
        guard, clock, _ = self.guard([
            cpu_table((42, OLD_START, "0:00.00", "mdworker_shared")),
            cpu_table((42, OLD_START, "0:01.80", "mdworker_shared")),
            cpu_table((42, OLD_START, "0:00.00", "mdworker_shared"))])
        self.assert_flagged(guard, "mdworker_shared 0.06 CPU-s/s")
        clock.now += prewindow.INTERVAL_S
        guard.check(force=True)
        interval = guard.receipts[-1]["cpu_interval"]
        self.assertEqual(interval["exited_over_limit"], [])
        self.assertTrue(interval["regressed_counters"][0]["contaminant"])
        original, carried = rule_flags(guard)
        self.assertEqual(original["interval"]["end_monotonic_s"], 30)
        self.assertEqual(carried["interval"]["start_monotonic_s"], 30)
        self.assertEqual(carried["interval"]["end_monotonic_s"], 60)
        self.assertIn("previous interval", carried["busy"][0]["basis"])

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
        guard.check(force=True)
        self.assertIsNone(guard.failure)
        rule = [f["flag"] for f in guard.contention_flags if f.get("kind") is None]
        self.assertIn("42 mdworker_shared 0.1 CPU-s/s", rule[-1], rule)
        self.assertRegex(guard.receipts[-1]["contention_flag"], "42 mdworker_shared 0.1 CPU-s/s")
        # Lead P1 also proves the burst at the 330 s read: 11.99 CPU-s after
        # rounding since the 120 s read, so one of seven 30 s windows held
        # at least 1.713 CPU-s.
        proven = [f["flag"] for f in guard.contention_flags if f.get("kind") == "proven_30s"]
        self.assertIn("11.99 CPU-s after rounding from 120.000 s to 330.000 s: at least 1.713 CPU-s in one of "
                      "7 windows", proven[-1])
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

    def test_repeated_short_startup_bursts_are_judged_without_latching(self):
        # A new pair born in every 15 s cadence slot for ten minutes uses
        # 0.6 CPU-s each before its first sample and exits by the next one.
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
        # The newest photoanalysisd uses 0.6 CPU-s over a 3 s overlap.
        self.assert_rate(max(rates), 0.2, 3)
        self.assertEqual(sorted({flag["interval"]["end_monotonic_s"] for flag in guard.contention_flags}), times[2:])
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
        # A throttled tick skips repeated probes, never a stale sample (lead
        # ruling after audit 3). The refusal then latches for every caller.
        with self.assertRaisesRegex(Refused, "background snapshots stalled \\(51.0 s since the last\\)"):
            guard.check()
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

    def test_args_ps_time_only_extends_the_admitted_midpoint(self):
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
                           sleep=clock.sleep, host_reader=None,
                           wall_clock_ns=lambda: 1_800_000_000_000_000_000 + round(clock() * 1e9))
        self.addCleanup(guard.close)
        guard.check(force=True)
        self.assertEqual(guard.receipts[-1]["cpu_interval"]["elapsed_s"], 30)
        background, admitted = guard.contention_flags
        self.assertEqual(background["interval"]["end_monotonic_s"], 30)
        self.assertAlmostEqual(background["busy"][0]["cpu_s_per_s"], 1.8 / 30)
        self.assertEqual(admitted["interval"]["end_monotonic_s"], 32.5)
        self.assertAlmostEqual(admitted["busy"][0]["cpu_s_per_s"], 1.8 / 32.5)

    def test_host_probe_time_precedes_the_admitted_cpu_sample(self):
        clock = GuardClock()

        def read_host():
            clock.now += 2
            return [[0, 0, 100, 0]]

        guard = QuietGuard([], run=self.runner, clock=clock, host_reader=read_host,
                           wall_clock_ns=lambda: round(clock() * 1e9))
        snapshot = guard._cpu_snapshot()
        self.assertEqual(snapshot.host, [[0, 0, 100, 0]])
        self.assertEqual(snapshot.admitted_midpoint_ns, 2_000_000_000)

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
        with patch.object(guard, "wall_clock_ns",
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
        with patch.object(guard, "wall_clock_ns", side_effect=[wall] * 4 + [backwards] * 2):
            guard.check(force=True)
        self.assertTrue(guard.receipts[-1]["wall_clock_backwards"])
        entry = guard.receipts[-1]["cpu_interval"]["contaminants"][0]
        self.assertEqual(entry["matched_on"], ["ucomm"])
        self.assert_rate(entry["cpu_s_per_s"], 0.04, prewindow.INTERVAL_S)

    def test_large_backwards_wall_step_charges_new_process_from_zero(self):
        guard, _, _ = self.guard([
            cpu_table(), cpu_table((42, OLD_START, "0:01.80", "mdworker_shared"))])
        wall = 2_000_000_000_000_000_000
        with patch.object(guard, "wall_clock_ns",
                   side_effect=[wall] * 4 + [wall - 2_000_000_000] * 2):
            self.assert_flagged(guard, "mdworker_shared 0.06 CPU-s/s")
        self.assertNotIn("missed by the first snapshot",
                         [row["reason"] for row in guard.receipts[-1]["cpu_interval"]["unaccounted"]])


if __name__ == "__main__":
    unittest.main()
