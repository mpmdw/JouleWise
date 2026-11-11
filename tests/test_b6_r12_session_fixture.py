"""Source-only R12 bootstrap tests. All paths and readings are synthetic."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from b6_r12_session_fixture import command, prepare
from b6_r12_chain_fixture import PIN


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r12-session-")
        self.addCleanup(self.temp.cleanup)
        self.root = prepare(Path(self.temp.name).resolve() / "fixture")

    def test_pinned_children_share_clock_without_wall_wait(self):
        """Predict: pinned SystemClock advances 60+30 s across fresh children in <10 wall s."""
        started = time.monotonic()
        rows = []
        for seconds in (60, 30):
            p = subprocess.run(command(self.root, "probe", seconds), capture_output=True, text=True, timeout=20)
            self.assertEqual(p.returncode, 0, p.stderr)
            rows.append(json.loads(p.stdout))
        self.assertLess(time.monotonic() - started, 10)
        self.assertEqual(rows[0]["after"], rows[1]["before"])
        self.assertEqual(rows[1]["after"]["epoch_s"] - rows[0]["before"]["epoch_s"], 90)
        manifest = json.loads((self.root / "manifest.json").read_text())
        path = Path(rows[0]["source"])
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), manifest["source_sha256"]["joulewise/clock.py"])

    def test_guard_rejects_metadata_probes_exec_and_escaping_write(self):
        """Predict: six denials occur before native metadata access, exec or file creation."""
        result = subprocess.run(command(self.root, "guard-probe"), capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(json.loads(result.stdout)), 6)
        self.assertFalse((self.root.parent / "R12-outside-write").exists())

    @unittest.skipUnless(sys.platform == "darwin", "pinned USB protocol uses CommonCrypto")
    def test_real_meter_writer_uses_synthetic_libusb_object(self):
        """Predict: unchanged meter writes streaming header, 11 polls/110 samples and duration trailer; no native USB load."""
        relative = "scripts/km003c_monitor.py"
        source = subprocess.check_output(["git", "show", f"{PIN}:{relative}"], cwd=REPO)
        script = self.root / "pin" / relative
        script.parent.mkdir(exist_ok=True)
        script.write_bytes(source)
        result = subprocess.run(command(self.root, "meter-probe"), capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [json.loads(line) for line in (self.root / "source-only-meter.jsonl").read_text().splitlines()]
        self.assertEqual(rows[0]["status"], "streaming")
        self.assertEqual(rows[0]["init_errors"], [])
        self.assertEqual(rows[-1]["stop_reason"], "duration")
        polls = [row for row in rows if row["k"] == "b"]
        self.assertEqual(len(polls), 11)
        self.assertEqual(sum(row["n"] for row in polls), 110)
        self.assertTrue(all(len(bytes.fromhex(row["p"])) == 200 for row in polls))

    def test_pinned_j1_schema_mismatch_is_reported_without_patch(self):
        """Predict: f31's real producer/reader disagree on J1 schema; reader returns verdict_schema_mismatch."""
        relative = "scripts/b5_window_calibration_verdict.py"
        source = subprocess.check_output(["git", "show", f"{PIN}:{relative}"], cwd=REPO)
        script = self.root / "pin" / relative
        script.parent.mkdir(exist_ok=True)
        script.write_bytes(source)
        result = subprocess.run(command(self.root, "j1-schema-probe"), capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        self.assertNotEqual(record["producer"], record["consumer"])
        self.assertEqual(record["miss"], {"reason": "verdict_schema_mismatch"})

    @unittest.skipUnless(Path("/bin/zsh").is_file(), "rendered chain requires zsh")
    def test_shell_and_python_use_same_clock(self):
        """Predict: unedited zsh date/sleep commands and pinned child see the same 75 s advance."""
        script = self.root / "synthetic-shell-input.zsh"
        script.write_text('/bin/date +%s\n/bin/sleep 75\n/bin/date +%s\n')
        p = subprocess.run(["/bin/zsh", "-f", str(self.root / "shell.zsh"), str(script)],
                           capture_output=True, text=True, timeout=20)
        self.assertEqual(p.returncode, 0, p.stderr)
        first, last = map(int, p.stdout.splitlines())
        self.assertEqual(last - first, 75)
        child = subprocess.run(command(self.root, "probe", 0), capture_output=True, text=True, timeout=20)
        self.assertEqual(child.returncode, 0, child.stderr)
        self.assertEqual(json.loads(child.stdout)["before"]["epoch_s"], last)


@unittest.skipUnless(os.environ.get("R12_REAL_CHAIN_SET"), "explicit generated R12 set required")
class DeclaredShapeTests(unittest.TestCase):
    """Integration expectations declared before any official named shape run.

    §17-R12: docs/registrations/block6_s17_entries_DRAFT_2026-11-10.md:673.
    A skip here is not evidence of a generated or accepted fixture.
    """

    def evidence(self, name):
        root = Path(os.environ["R12_REAL_CHAIN_SET"])
        if root.is_relative_to("/Users/edr") or "restricted" in root.parts:
            self.fail("forbidden fixture root")
        value = json.loads((root / "observations.json").read_text())[name]
        self.assertEqual(value["production_exit"], 0)
        self.assertTrue(value["comparator_agrees"])
        return value

    def test_waited_attempt_n(self):
        """Predict r12-waited: option (c) exits 0/agrees, idle.waited and attempt >=2 telemetry (§17-R12:673)."""
        value = self.evidence("r12-waited")
        self.assertIn("idle.waited", value["flags"])
        self.assertGreaterEqual(value["max_idle_attempt"], 2)

    def test_wait_cap_and_budget_skips(self):
        """Predict r12-skips: option (c) exits 0/agrees; real idle.wait_cap_skip and idle.wait_budget_skip (§17-R12:673)."""
        value = self.evidence("r12-skips")
        self.assertTrue({"idle.wait_cap_skip", "idle.wait_budget_skip"}.issubset(value["flags"]))

    def test_unbounded_anchor(self):
        """Predict r12-anchor: option (c) exits 0/agrees; member.anchor_not_bounded excludes the source-skewed member (§17-R12:673)."""
        self.assertIn("member.anchor_not_bounded", self.evidence("r12-anchor")["flags"])

    def test_mixed_campaign_rows(self):
        """Predict r12-mixed: option (c) exits 0/agrees and classifies executed-member plus trailing evaluation rows (§17-R12:673)."""
        self.assertEqual(set(self.evidence("r12-mixed")["campaign_row_kinds"]), {"member", "evaluation"})

    def test_desk_compressed_logs_and_plists(self):
        """Predict r12-compressed: option (c) exits 0/agrees reading real desk-compressed campaign logs and plists (§17-R12:673)."""
        value = self.evidence("r12-compressed")
        self.assertGreater(value["compressed_campaign_logs"], 0)
        self.assertGreater(value["compressed_plists"], 0)

    def test_cross_session_gamma(self):
        """Predict r12-gamma-cross: nine-session option (c) exits 0/agrees and records a GAMMA unit paired across sessions (§17-R12:673)."""
        self.assertTrue(self.evidence("r12-gamma-cross")["cross_session_gamma"])


if __name__ == "__main__":
    unittest.main()
