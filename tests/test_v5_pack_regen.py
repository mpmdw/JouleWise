"""Idle-duration and historical-reference regressions for the issued v5 packs."""

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
                    members = []
                    for path in pack.rglob("*.json"):
                        row = json.loads(path.read_bytes())
                        if "sampling" in row and "run_id" in row:
                            members.append(row)
                    self.assertEqual(len(members), 80 if "contrast" in pack_id else 100)
                    self.assertTrue(all(row["sampling"]["idle_seconds"] == 75.0
                                        for row in members))

    def test_v5_reference_copies_change_only_idle_and_retain_run_ids(self):
        count = 0
        for directory in ("neg8_reference_corpus", "window_references"):
            historical = ROOT / "configs/campaigns" / directory
            prospective = historical.with_name(directory + "_v5")
            self.assertEqual({p.relative_to(historical) for p in historical.rglob("*") if p.is_file()},
                             {p.relative_to(prospective) for p in prospective.rglob("*") if p.is_file()})
            for path in historical.rglob("*"):
                if not path.is_file() or path.name == "README.md":
                    continue
                raw = path.read_bytes()
                copy_raw = (prospective / path.relative_to(historical)).read_bytes()
                if b'"idle_seconds": 30.0' in raw:
                    self.assertEqual(copy_raw, raw.replace(b'"idle_seconds": 30.0',
                                                          b'"idle_seconds": 75.0'))
                    count += 1
                else:
                    self.assertEqual(copy_raw, raw)
        self.assertEqual(count, 19)

    def test_v5_packs_pin_only_prospective_external_reference_roots(self):
        count = 0
        for pack_id in PACKS:
            tree = json.loads((ROOT / "configs/campaigns" / pack_id / "plan_tree.json").read_bytes())
            inputs = tree["external_inputs"]
            if isinstance(inputs, dict):
                inputs = [row for rows in inputs.values() for row in rows]
            for external in inputs:
                paths = [external.get("path", ""), external.get("manifest_path", ""),
                         external.get("manifest", {}).get("path", "")]
                for path in paths:
                    if any(name in path for name in ("neg8_reference_corpus", "window_references")):
                        self.assertTrue(any(name in path for name in
                                            ("neg8_reference_corpus_v5/", "window_references_v5/")))
                        count += 1
                for member in external.get("members", []):
                    path = ROOT / member["path"]
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), member["sha256"])
                    self.assertEqual(json.loads(path.read_bytes())["sampling"]["idle_seconds"], 75.0)
        self.assertEqual(count, 15)

    def test_gamma_interior_stages_retain_shared_midpoint_until_block5_design(self):
        """GAMMA-INTERIOR-REFERENCES-01 owns three-point evaluator semantics."""
        pack = ROOT / "configs/campaigns" / PACKS[-1]
        tree = json.loads((pack / "plan_tree.json").read_bytes())
        stage_ids = {"gamma-reference-decode-midpoint", "gamma-reference-arm-boundary",
                     "gamma-reference-prefill-midpoint"}
        external = {row["input_id"]: row for row in tree["external_inputs"]}
        stages = [stage for stage in tree["stage_graph"] if stage["stage_id"] in stage_ids]
        self.assertEqual(len(stages), 3)
        for stage in stages:
            self.assertEqual(stage["input_ref"], {"kind": "external_input", "input_id": "midpoint_reference"})
            source = external["midpoint_reference"]
            manifest_path = ROOT / source["manifest_path"]
            self.assertEqual(source["manifest_path"],
                             "configs/campaigns/window_references_v5/midpoint/order_manifest.json")
            self.assertEqual(hashlib.sha256(manifest_path.read_bytes()).hexdigest(), source["manifest_sha256"])
            row, = json.loads(manifest_path.read_bytes())["executed_order"]
            self.assertEqual(row["run_id"], "neg8-window-midpoint")
            argument = stage["launch"]["commands"][0]["argv_template"]["arguments"][0]
            self.assertEqual(ROOT / argument["value"], manifest_path.parent)
        self.assertFalse((pack / "references").exists())

        run_ids = []
        for stage in tree["stage_graph"]:
            if stage["kind"] != "campaign_collection":
                continue
            reference = stage["input_ref"]
            rows = (external[reference["input_id"]]["members"]
                    if reference["kind"] == "external_input" else
                    json.loads((pack / reference["path"]).read_bytes())["executed_order"])
            run_ids.extend(row["run_id"] for row in rows)
        self.assertEqual(len(run_ids), 101)
        self.assertEqual(len(set(run_ids)), 99)
        self.assertEqual(run_ids.count("neg8-window-midpoint"), 3)


if __name__ == "__main__":
    unittest.main()
