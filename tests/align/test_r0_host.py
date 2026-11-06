from pathlib import Path
from types import SimpleNamespace
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.r0 import PINS
from joulewise.align.r0_host import QuietGuard, Refused, disk_census, w1_disk_gate, host_snapshot, host_identity, inventory, smc_enumeration, swap_bytes
from joulewise.measurement_liveness import Census
from tests.align.test_r0_checks import config_at
from tests.align.test_r0_step import write_capture


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
        guard = QuietGuard([str(explicit)], run=self.runner, inspect_custody=custody)
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
            if "pgrep" in argv[0]:
                return self.runner(argv)
            return subprocess.CompletedProcess(argv, 0, "1 0.0 /sbin/launchd\n99 0.0 python scripts/run_campaign.py --runs-root /tmp/fake\n", "")
        guard = QuietGuard([], run=running, inspect_custody=lambda **kw: Census())
        with self.assertRaises(Refused):
            guard.check(force=True)
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
                payload = write_capture(output)
                result = smc_enumeration(root, output)
                self.assertEqual(result["selection"], {"s_fast": "TC0P", "s_slow": "TH0P"})
                self.assertEqual(result["status"], "pass")
                self.assertEqual(result["smc_source_commit"], "58525031a")
                self.assertEqual(result["selection_status"], "PROVISIONAL")
                self.assertEqual(result["response"]["selection_status"], "PROVISIONAL")
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
            write_capture(output, profile=profile)
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


if __name__ == "__main__":
    unittest.main()
