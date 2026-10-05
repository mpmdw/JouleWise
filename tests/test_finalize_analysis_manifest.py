from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise import detection_floor, dominance_closeout
from tests.test_analysis_finalizer import install_synthetic_finalization_fixture
from tests.test_d165_dominance_closeout import (
    builder_recomputations,
    floor_artifact,
    replay_sidecar,
)

ROOT = Path(__file__).resolve().parents[1]


class FinalizeSidecarCLITests(unittest.TestCase):
    def command(self, fixture: dict) -> list[str]:
        return [
            sys.executable, "-B", str(ROOT / "scripts/finalize_analysis_manifest.py"),
            "--prospective-manifest", str(fixture["prospective_path"]),
            "--plan-tree", str(fixture["plan_tree_path"]),
            "--custody-root", str(fixture["root"]),
            "--runs-root", str(fixture["runs_root"]),
            "--whole-window-verdict", str(fixture["verdict_path"]),
            "--bracket-binding", str(fixture["bracket_path"]),
            "--calibration-ledger", str(fixture["ledger_path"]),
            "--aggregate-floor-artifact", str(fixture["floor_path"]),
            "--output-dir", str(fixture["root"]),
        ]

    def test_documented_finalize_stages_real_common_mode_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = install_synthetic_finalization_fixture(
                root / "custody", dominance_criterion={"rule_id": "test-dominance"}
            )
            # Real sidecar producer and replay arithmetic on labelled fixture operands.
            floor = floor_artifact()
            records = builder_recomputations(floor, replay_sidecar(floor))
            self.assertTrue(all(r.estimator_path == "common_mode" for r in records.values()))
            self.assertEqual(
                detection_floor.two_shared_edge_common_mode_registration()["estimator_id"],
                detection_floor.COMMON_MODE_ESTIMATOR_ID,
            )
            sidecar = dominance_closeout.build_d165_replay_sidecar(floor, records)
            source = root / "mint-replay.json"
            raw = (json.dumps(sidecar, indent=2, sort_keys=True) + "\n").encode()
            source.write_bytes(raw)
            command = self.command(fixture) + ["--dominance-replay-sidecar", str(source)]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads(Path(json.loads(result.stdout)["output"]).read_text())
            attachment = manifest["evidence"]["dominance_replay_sidecar"]
            staged = fixture["root"] / attachment["path"]
            self.assertEqual(staged.read_bytes(), raw)
            self.assertEqual(source.read_bytes(), raw)
            self.assertEqual(attachment["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(attachment["sidecar_id"], sidecar["sidecar_id"])
            replay = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(replay.returncode, 0, replay.stdout + replay.stderr)
            self.assertEqual(json.loads(replay.stdout), json.loads(result.stdout))

    def test_without_sidecar_preserves_existing_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(
                Path(tmp), dominance_criterion={"rule_id": "test-dominance"}
            )
            result = subprocess.run(self.command(fixture), cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["reason"], "analysis_finalization_attachment_missing")
            self.assertEqual(list(Path(tmp).glob("*.finalized.json")), [])

    def test_sidecar_symlink_refuses_without_staging(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = install_synthetic_finalization_fixture(
                root / "custody", dominance_criterion={"rule_id": "test-dominance"}
            )
            target = root / "target.json"
            target.write_text(json.dumps({"schema_version": dominance_closeout.REPLAY_SCHEMA_VERSION,
                                          "sidecar_id": "valid-sidecar"}) + "\n")
            source = root / "link.json"
            source.symlink_to(target)
            result = subprocess.run(self.command(fixture) + ["--dominance-replay-sidecar", str(source)],
                                    cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["status"], "REFUSE")
            self.assertEqual(list(fixture["root"].glob("*.finalized.json")), [])


if __name__ == "__main__":
    unittest.main()
