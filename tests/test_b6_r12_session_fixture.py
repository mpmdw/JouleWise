"""Source-only R12 bootstrap tests. All paths and readings are synthetic."""
import hashlib
import importlib.util
import json
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


if __name__ == "__main__":
    unittest.main()
