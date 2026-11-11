"""RL-49 feasibility witnesses. These are not R12 session/comparator tests."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
GENERATOR = REPO / "scripts/b6_r12_chain_fixture.py"


class PinnedArmWitnessTests(unittest.TestCase):
    def witness(self, denied=False):
        with tempfile.TemporaryDirectory(prefix="r12-arm-") as directory:
            root = Path(directory).resolve() / "witness"
            command = [sys.executable, "-B", str(GENERATOR), "--out", str(root)]
            if denied:
                command.append("--denied-off")
            result = subprocess.run(command, capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            receipt = json.loads((root / "receipt.json").read_bytes())
            manifest = json.loads((root / "manifest.json").read_bytes())
            arm = json.loads(Path(receipt["arm_path"]).read_bytes())
            return receipt, manifest, arm

    def test_declared_success_is_record_only_and_arm_go(self):
        """RL-49 rules 1-2: simulated OFF success; real arm predicts GO."""
        receipt, manifest, arm = self.witness()
        self.assertEqual(arm["decision"], "GO")
        self.assertEqual(arm["unmeasured"], [])
        for module, rows in arm["hazards"].items():
            for row in rows:
                self.assertEqual(row["verdict"]["status"], "PASS", module)
        self.assertEqual(arm["network_time_off"]["returncode"], 0)
        self.assertEqual(manifest["generator_sha256"], hashlib.sha256(GENERATOR.read_bytes()).hexdigest())
        self.assertTrue(receipt["safety"]["native_launch_denied"])
        self.assertTrue(receipt["safety"]["outside_write_denied"])
        self.assertGreaterEqual(receipt["logical_seconds"], 180)
        self.assertEqual(arm["hazards"]["instrument"][0]["verdict"]["status"], "PASS")
        child = [c for c in receipt["calls"] if c["kind"] == "pinned_instrument_child"]
        self.assertEqual(len(child), 1)
        self.assertTrue(child[0]["executed"])
        self.assertTrue(all(not c["executed"] for c in receipt["calls"] if c not in child))
        for name, digest in receipt["loaded_chain_sha256"].items():
            self.assertEqual(digest, manifest["source_sha256"][name], name)

    def test_denied_action_stays_record_only_and_arm_go(self):
        """RL-49 rule 2 extra shape: denied OFF is recorded; real arm predicts GO."""
        receipt, _, arm = self.witness(denied=True)
        self.assertEqual(arm["decision"], "GO")
        self.assertEqual(arm["network_time_off"]["returncode"], 126)
        denied = [c for c in receipt["calls"] if c["kind"] == "denied" and
                  c["argv"] == arm["network_time_off"]["argv"]]
        self.assertEqual(len(denied), 1)
        self.assertEqual(denied[0]["argv"], arm["network_time_off"]["argv"])
        self.assertFalse(denied[0]["executed"])


if __name__ == "__main__":
    unittest.main()
