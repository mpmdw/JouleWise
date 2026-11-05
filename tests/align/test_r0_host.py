from pathlib import Path
from types import SimpleNamespace
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.r0 import PINS
from joulewise.align.r0_host import QuietGuard, Refused, disk_census, host_snapshot, inventory, smc_enumeration, swap_bytes
from joulewise.measurement_liveness import Census
from tests.align.test_r0_checks import config_at


class R0HostTest(unittest.TestCase):
    def runner(self, argv, **kwargs):
        if "pgrep" in argv[0]:
            return subprocess.CompletedProcess(argv, 1, "", "")
        return subprocess.CompletedProcess(argv, 0, "1 0.0 /sbin/launchd\n", "")

    def test_guard_clear_reuses_shared_censuses_with_explicit_parents(self):
        calls = []
        def custody(**kwargs):
            calls.append(kwargs)
            return Census()
        guard = QuietGuard(["/tmp/explicit"], run=self.runner, inspect_custody=custody)
        guard.check(force=True)
        self.assertEqual(calls, [{"parents": [Path("/tmp/explicit")]}])
        self.assertEqual(len(guard.receipts), 1)

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

    def test_disk_requires_both_verified_offloads_and_80_decimal_gb(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = config_at(root)
            for tag in ("N", "D"):
                folder = root / tag
                folder.mkdir()
                (folder / "model").write_text("tiny fake weight")
            for label in ("pilot8", "pilot9"):
                folder = root / label
                folder.mkdir()
                (folder / "file").write_text("synthetic offload")
                manifest = root / (label + ".json")
                manifest.write_text(json.dumps(inventory(folder)))
                config["offloads"].append({"label": label, "inventory": str(manifest), "destination": str(folder)})
            with patch("shutil.disk_usage", return_value=SimpleNamespace(free=80_000_000_000)):
                self.assertEqual(disk_census(config, PINS)["status"], "pass")
                (root / "pilot9" / "file").write_text("changed")
                self.assertEqual(disk_census(config, PINS)["status"], "fail")
            with patch("shutil.disk_usage", return_value=SimpleNamespace(free=79_999_999_999)):
                self.assertEqual(disk_census(config, PINS)["status"], "fail")

    def test_swap_parse_and_missing_value(self):
        self.assertEqual(swap_bytes(lambda argv: "total = 0.00M used = 1.50M free = 1M"), 1572864)
        with self.assertRaises(ValueError):
            swap_bytes(lambda argv: "unavailable")

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
                self.assertEqual(smc_enumeration(root, root / "output")["status"], "pass")
                self.assertEqual(call.call_args.args[0][-2:], ["--output", str(root / "output")])


if __name__ == "__main__":
    unittest.main()
