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
from joulewise.align.r0_host import QuietGuard, Refused, disk_census, w1_disk_gate, host_snapshot, host_identity, inventory, smc_enumeration, swap_bytes
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
            self.assertEqual(result["smc_step_budget"]["capture_seconds"], 2700)  # 1200 idle cap +900 load +600 recovery.
            # R0 states what the W1 arm gate will require, from the gate's own constant.
            need = result["w1_requirement"]
            self.assertEqual(need["gate"], "joulewise.align.r0_host.w1_disk_gate")
            self.assertIn("align_v4_session.py install", need["called_by"])
            self.assertEqual(need["required_free_bytes_after_r0"], 80_000_000_000)
            self.assertFalse(need["free_space_would_pass_now"])
            self.assertEqual(need["shortfall_bytes"], 14_000_000_000)
            self.assertEqual(need["offload_labels_rehashed_at_arm"], ["pilot10"])
            self.assertFalse(need["offloads_checked_by_r0"])
            with patch("shutil.disk_usage", return_value=SimpleNamespace(free=80_000_000_000)):
                self.assertTrue(disk_census(config, PINS)["w1_requirement"]["free_space_would_pass_now"])
            with patch("joulewise.align.r0_host.W1_REQUIRED_FREE_BYTES", 90_000_000_000), \
                    patch("shutil.disk_usage", return_value=SimpleNamespace(free=85_000_000_000)):
                need = disk_census(config, PINS)["w1_requirement"]
                self.assertEqual((need["required_free_bytes_after_r0"], need["free_space_would_pass_now"]),
                                 (90_000_000_000, False))
                self.assertEqual(w1_disk_gate(dict(config, offloads=[]))["required_free_bytes_after_r0"],
                                 90_000_000_000)

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


class R0QuietIntervalTest(unittest.TestCase):
    # CPU fixtures derive from the 0.05 CPU-s/s bar and 30 s interval:
    # 0.06 / 0.04 straddle the bar by 0.01; 1.80 / 1.20 are their
    # 30 s counters. 0.60 = 60 TIME quanta, hence 0.02 over 30 s.
    # Scenario times 45 / 60 are 1.5 / 2 intervals; short-call offsets
    # 0.1 / 0.2 are 10 / 20 TIME quanta. One CPU-s is 100 quanta.
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
        # Opening is 0: bracket by 1 s (100 TIME quanta). The next eligible
        # opening is 30.1 = 30 + 10 TIME quanta, bracketed by 30 and 31.
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

    def test_contaminant_regression_between_short_forced_calls_is_recorded(self):
        # 100 TIME quanta / 30 s is below 0.05. A later drop of ten
        # quanta, seen ten quanta of wall time later, adds no refusal.
        def snapshot(cpu):
            return cpu_table((42, OLD_START, cpu, "mdworker_shared"))
        guard, clock, _ = self.guard([snapshot("0:01.00"), snapshot("0:02.00"), snapshot("0:01.90")])
        guard.check(force=True)
        clock.now = 30.1
        guard.check(force=True)
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
        busy = guard._cpu_interval(receipt)
        self.assertEqual(busy[0]["pid"], 42)
        self.assertIn("previous interval", busy[0]["basis"])
        self.assert_rate(busy[0]["cpu_s_per_s"], 0.06, 30)

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

    def test_contaminant_regression_with_previous_over_limit_still_refuses(self):
        # (0.05 + 0.01) * 30 = 1.80 CPU-s, then TIME -> zero.
        # check() latches on the first interval, so inspect the next interval
        # directly to verify the module's exited_over_limit rule too.
        guard, clock, _ = self.guard([
            cpu_table((42, OLD_START, "0:00.00", "mdworker_shared")),
            cpu_table((42, OLD_START, "0:01.80", "mdworker_shared")),
            cpu_table((42, OLD_START, "0:00.00", "mdworker_shared"))])
        with self.assertRaisesRegex(Refused, "mdworker_shared 0.06 CPU-s/s"):
            guard.check(force=True)
        clock.now += prewindow.INTERVAL_S
        receipt = {}
        self.assertEqual(guard._cpu_interval(receipt)[0]["pid"], 42)
        interval = receipt["cpu_interval"]
        self.assertEqual(interval["exited_over_limit"][0]["pid"], 42)
        self.assertTrue(interval["regressed_counters"][0]["contaminant"])
        with self.assertRaises(Refused):
            guard.check(force=True)

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

    def test_gap_contender_is_detected_on_first_wholly_post_gap_window(self):
        # Gap 600 = 20 * 30 s. A contender at 10 * 0.05 = 0.5 for
        # its last 30 s has 15 CPU-s, diluted to 0.025 over the gap.
        # With 15 s calls, the second call after the gap call (t=660)
        # first judges a wholly post-gap 30 s window, 630 -> 660.
        def snapshot(cpu):
            return cpu_table((42, OLD_START, cpu, "mdworker_shared"))
        guard, clock, calls = self.guard([
            snapshot("0:00.00"), snapshot("0:00.00"),
            snapshot("0:15.00"), snapshot("0:22.50"), snapshot("0:30.00")])
        guard.check(force=True)
        guard.sleep = lambda seconds: self.fail("slept after first admission")
        clock.now += 20 * prewindow.INTERVAL_S
        guard.check(force=True)
        interval = guard.receipts[-1]["cpu_interval"]
        self.assert_rate(interval["contaminants"][0]["cpu_s_per_s"], 0.025, 20 * prewindow.INTERVAL_S)
        self.assertTrue(interval["long_interval"])
        self.assertTrue(guard.receipts[-1]["long_interval"])
        clock.now += prewindow.INTERVAL_S / 2
        guard.check(force=True)  # 22.50 / 615 < 0.05; still uses the pre-gap opening.
        clock.now += prewindow.INTERVAL_S / 2
        with self.assertRaisesRegex(Refused, "mdworker_shared 0.5 CPU-s/s"):
            guard.check(force=True)
        self.assertEqual(clock.sleeps, [prewindow.INTERVAL_S])
        interval = guard.receipts[-1]["cpu_interval"]
        self.assertEqual(interval["elapsed_s"], prewindow.INTERVAL_S)
        self.assertEqual(len(guard._snapshots), 3)
        self.assertEqual(calls[-1] - calls[-2], prewindow.INTERVAL_S / 2)
        with self.assertRaises(Refused):
            guard.check(force=True)

    def test_gap_contention_refuses_on_the_long_judged_interval(self):
        # (0.05 + 0.01) * (20 * 30) = 36 CPU-s across the gap;
        # the long judged interval alone must refuse without another sleep.
        def snapshot(cpu):
            return cpu_table((42, OLD_START, cpu, "mdworker_shared"))
        guard, clock, _ = self.guard([
            snapshot("0:00.00"), snapshot("0:00.00"),
            snapshot("0:36.00")])
        guard.check(force=True)
        guard.sleep = lambda seconds: self.fail("slept after first admission")
        clock.now += 20 * prewindow.INTERVAL_S
        with self.assertRaisesRegex(Refused, "mdworker_shared 0.06 CPU-s/s"):
            guard.check(force=True)
        self.assertTrue(guard.receipts[-1]["cpu_interval"]["long_interval"])

    def test_no_sleep_after_first_admission_at_cadence_or_after_gaps(self):
        dwell = prewindow.INTERVAL_S
        # Guard cadence = 30 / 2; gaps = 20 * 30 and 30 + 100 TIME
        # quanta (600 and 31 s). Eight snapshots include the startup pair.
        steps = (dwell / 2, dwell / 2, 20 * dwell,
                 dwell + 100 * contention.PS_TIME_QUANTUM_S, dwell / 2, dwell / 2)
        guard, clock, calls = self.guard([cpu_table()] * (2 + len(steps)))
        guard.check(force=True)
        self.assertEqual(clock.sleeps, [dwell])
        guard.sleep = lambda seconds: self.fail("slept after first admission")
        for step in steps:
            clock.now += step
            guard.check()
            self.assertGreaterEqual(guard.receipts[-1]["cpu_interval"]["elapsed_s"], dwell)
        self.assertEqual(len(calls), 2 + len(steps))

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
        with patch("joulewise.align.r0_host.time.time_ns", side_effect=[wall, wall, backwards, backwards]):
            guard.check(force=True)
        self.assertTrue(guard.receipts[-1]["wall_clock_backwards"])
        entry = guard.receipts[-1]["cpu_interval"]["contaminants"][0]
        self.assertEqual(entry["matched_on"], ["ucomm"])
        self.assert_rate(entry["cpu_s_per_s"], 0.04, prewindow.INTERVAL_S)


if __name__ == "__main__":
    unittest.main()
