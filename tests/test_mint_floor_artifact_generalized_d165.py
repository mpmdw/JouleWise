from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from joulewise import detection_floor, dominance_closeout
from scripts import mint_floor_artifact_generalized as mint
from tests.test_d165_dominance_closeout import builder_recomputations, floor_artifact, replay_sidecar


class MintD165OutputTests(unittest.TestCase):
    def test_existing_cli_flag_and_real_sidecar_writer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = mint._parser().parse_args([
                "--pinset", str(root / "pins.json"), "--pinset-sha256", "1" * 64,
                "--v2-input-manifest", str(root / "inputs.json"),
                "--out", str(root / "floor.json"), "--single-count-out", str(root / "statement.txt"),
                "--d165-replay-out", str(root / "replay.json"),
                "--project-commit", "0" * 40, "--project-tree-state", "clean",
            ])
            floor = floor_artifact()
            floor["single_count_discipline"] = detection_floor.attribution_single_count_discipline()
            records = builder_recomputations(floor, replay_sidecar(floor))
            sidecar = dominance_closeout.build_d165_replay_sidecar(floor, records)
            mint._write_v2_artifact_outputs(output_core=mint._fresh_original_core(), artifact=floor,
                sidecar=sidecar, floor_path=args.out, statement_path=args.single_count_out,
                d165_replay_out=args.d165_replay_out)
            self.assertEqual(json.loads(args.out.read_text()), floor)
            self.assertEqual(json.loads(args.d165_replay_out.read_text()), sidecar)
            self.assertEqual(args.out.read_bytes(), mint._artifact_payload(floor))
            self.assertTrue(args.single_count_out.read_text())
            with self.assertRaises(mint.MintError):
                mint._write_v2_artifact_outputs(output_core=mint._fresh_original_core(), artifact=floor,
                    sidecar=sidecar, floor_path=args.out, statement_path=args.single_count_out,
                    d165_replay_out=root / "another-replay.json")
            self.assertFalse((root / "another-replay.json").exists())


if __name__ == "__main__":
    unittest.main()
