"""Idle duration and reference identity regressions for the issued v5 packs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKS = (
    "d117_floor_qwen3-1p7b_v5",
    "d117_floor_qwen3-8b_v5",
    "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5",
)
PIN = ROOT / "configs/campaigns/d117_contrast_v5/prefill_pin/prefill-prompt-pin.json"


class V5PackRegenerationTests(unittest.TestCase):
    def test_generators_emit_75_second_idle_from_issued_pin(self):
        """Generate afresh: committed member bytes cannot conceal an old constant."""
        with tempfile.TemporaryDirectory(prefix="v5-idle-") as temporary:
            output = Path(temporary)
            for pack_id in PACKS:
                with self.subTest(pack=pack_id):
                    result = subprocess.run(
                        [sys.executable, "-B", str(ROOT / "configs/campaigns" / pack_id
                                                  / "generate_configs.py"),
                         "--prefill-prompt-pin", str(PIN),
                         "--no-preserve-current-frozen-bytes", "--output-root", str(output)],
                        cwd=ROOT, capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    pack = output / "configs/campaigns" / pack_id
                    members = [json.loads(path.read_bytes()) for path in pack.rglob("*.json")
                               if "sampling" in json.loads(path.read_bytes())
                               and "run_id" in json.loads(path.read_bytes())]
                    self.assertEqual(len(members), 82 if "contrast" in pack_id else 100)
                    self.assertTrue(all(row["sampling"]["idle_seconds"] == 75.0
                                        for row in members))

    def test_all_dispatched_external_sources_use_75_second_idle(self):
        count = 0
        for directory in ("neg8_reference_corpus", "window_references"):
            for manifest in (ROOT / "configs/campaigns" / directory).rglob("order_manifest.json"):
                for row in json.loads(manifest.read_bytes())["executed_order"]:
                    config = json.loads((manifest.parent / row["config"]).read_bytes())
                    self.assertEqual(config["sampling"]["idle_seconds"], 75.0)
                    count += 1
        self.assertEqual(count, 19)

    def test_gamma_interior_stages_pin_distinct_run_ids_and_same_science(self):
        pack = ROOT / "configs/campaigns" / PACKS[-1]
        tree = json.loads((pack / "plan_tree.json").read_bytes())
        source = json.loads((ROOT / "configs/campaigns/window_references/midpoint"
                             / "neg8-window-midpoint.json").read_bytes())
        stage_ids = {"gamma-reference-decode-midpoint", "gamma-reference-arm-boundary",
                     "gamma-reference-prefill-midpoint"}
        run_ids = []
        for stage in tree["stage_graph"]:
            if stage["stage_id"] not in stage_ids:
                continue
            reference = stage["input_ref"]
            if reference["kind"] == "external_input":
                external = next(row for row in tree["external_inputs"]
                                if row["input_id"] == reference["input_id"])
                manifest_path = ROOT / external["manifest_path"]
                manifest_sha = external["manifest_sha256"]
            else:
                self.assertEqual(reference["kind"], "pack_manifest")
                manifest_path = pack / reference["path"]
                manifest_sha = reference["sha256"]
            self.assertEqual(hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                             manifest_sha)
            manifest = json.loads(manifest_path.read_bytes())
            row, = manifest["executed_order"]
            config_path = manifest_path.parent / row["config"]
            if reference["kind"] == "pack_manifest":
                self.assertEqual(hashlib.sha256(config_path.read_bytes()).hexdigest(),
                                 row["config_sha256"])
            config = json.loads(config_path.read_bytes())
            self.assertEqual(config["run_id"], row["run_id"])
            run_ids.append(row["run_id"])
            if reference["kind"] == "pack_manifest":
                self.assertEqual(manifest["calibration_plan_sha256"], tree["plan"]["actual_sha256"])
                self.assertIn("calibration-plan-sha256=" + tree["plan"]["actual_sha256"],
                              config["run_metadata"]["tags"])
            config["run_id"] = source["run_id"]
            config["run_metadata"]["tags"] = source["run_metadata"]["tags"]
            self.assertEqual(config, source)
            argument = stage["launch"]["commands"][0]["argv_template"]["arguments"][0]
            self.assertEqual(ROOT / argument["value"], manifest_path.parent)
        self.assertEqual(len(run_ids), 3)
        self.assertEqual(len(set(run_ids)), 3)
        self.assertIn(source["run_id"], run_ids)

        external = {row["input_id"]: row for row in tree["external_inputs"]}
        full_run_ids = []
        for stage in tree["stage_graph"]:
            if stage["kind"] != "campaign_collection":
                continue
            reference = stage["input_ref"]
            if reference["kind"] == "external_input":
                rows = external[reference["input_id"]]["members"]
            else:
                rows = json.loads((pack / reference["path"]).read_bytes())["executed_order"]
            full_run_ids.extend(row["run_id"] for row in rows)
        self.assertEqual(len(full_run_ids), 101)
        self.assertEqual(len(set(full_run_ids)), 101)


if __name__ == "__main__":
    unittest.main()
