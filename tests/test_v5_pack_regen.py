"""Idle-duration and historical-reference regressions for the issued v5 packs.

The block-5 timing ruling (2026-10-06) sizes idle capture by duration: idle_seconds 57.6
asks the adapter for ceil(57.6 / 0.1) = 576 records, about 75 s at the sampler's ~130.5 ms
cadence. Before it, the packs set idle_seconds 75.0 (750 records, about 98 s).
"""

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
V5_IDLE_SECONDS = 57.6


class V5PackRegenerationTests(unittest.TestCase):
    def test_generators_emit_duration_sized_idle_from_issued_pin(self):
        """Generate afresh until freeze; then respect the frozen-byte guard."""
        with tempfile.TemporaryDirectory(prefix="v5-idle-") as temporary:
            output = Path(temporary)
            for pack_id in PACKS:
                with self.subTest(pack=pack_id):
                    source = ROOT / "configs/campaigns" / pack_id
                    tree = json.loads((source / "plan_tree.json").read_bytes())
                    frozen = tree["arm_attachments"]["arm_readiness"]["freeze_receipt"] is not None
                    preserve = ("--preserve-current-frozen-bytes" if frozen else
                                "--no-preserve-current-frozen-bytes")
                    result = subprocess.run(
                        [sys.executable, "-B", str(source / "generate_configs.py"),
                         "--prefill-prompt-pin", str(PIN),
                         preserve, "--output-root", str(output)],
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
                    self.assertTrue(all(row["sampling"]["idle_seconds"] == V5_IDLE_SECONDS
                                        for row in members))

    def test_v5_reference_copies_change_only_idle_and_retain_run_ids(self):
        count = 0
        for directory in ("neg8_reference_corpus", "window_references"):
            historical = ROOT / "configs/campaigns" / directory
            prospective = historical.with_name(directory + "_v5")
            old_paths = {p.relative_to(historical) for p in historical.rglob("*") if p.is_file()}
            extra = ({Path(f"neg8-refcorpus-r{i:02d}.json") for i in range(13, 19)}
                     if directory == "neg8_reference_corpus" else set())
            self.assertEqual(old_paths | extra,
                             {p.relative_to(prospective) for p in prospective.rglob("*") if p.is_file()})
            for path in historical.rglob("*"):
                if not path.is_file() or path.name == "README.md":
                    continue
                raw = path.read_bytes()
                copy_raw = (prospective / path.relative_to(historical)).read_bytes()
                if b'"idle_seconds": 30.0' in raw:
                    self.assertEqual(copy_raw, raw.replace(b'"idle_seconds": 30.0',
                                                          b'"idle_seconds": 57.6'))
                    count += 1
                elif directory == "neg8_reference_corpus" and path.name in {"order_manifest.json", "settled_corpus.json"}:
                    # Membership and labels change prospectively; the next test pins each change.
                    continue
                else:
                    self.assertEqual(copy_raw, raw)
        self.assertEqual(count, 19)

    def test_corpus18_preserves_the_first_twelve_and_adds_six_identical_conditions(self):
        historical = ROOT / "configs/campaigns/neg8_reference_corpus"
        prospective = ROOT / "configs/campaigns/neg8_reference_corpus_v5"
        order = json.loads((prospective / "order_manifest.json").read_bytes())
        old_order = json.loads((historical / "order_manifest.json").read_bytes())
        corpus = json.loads((prospective / "derivation/settled_corpus.json").read_bytes())
        old_corpus = json.loads((historical / "derivation/settled_corpus.json").read_bytes())
        ids = [f"neg8-refcorpus-r{i:02d}" for i in range(1, 19)]
        corpus_id = "neg8-reference-corpus-m3max-qwen25-1p5b-v2-n18"
        self.assertEqual((18, "neg8-reference-corpus-order-v2", corpus_id),
                         (order["planned_n_bundles"], order["manifest_id"], order["plan_id"]))
        self.assertEqual(order["executed_order"][:12], old_order["executed_order"])
        self.assertEqual([row["run_id"] for row in order["executed_order"]], ids)
        self.assertEqual(corpus["corpus_id"], corpus_id)
        self.assertEqual(corpus["members"][:12], old_corpus["members"])
        self.assertEqual(corpus["members"], [{"bundle_id": run_id, "bundle_path": run_id} for run_id in ids])
        self.assertEqual({k: v for k, v in corpus.items() if k not in {"corpus_id", "members"}},
                         {k: v for k, v in old_corpus.items() if k not in {"corpus_id", "members"}})
        self.assertEqual({k: v for k, v in order.items() if k not in {"manifest_id", "plan_id", "planned_n_bundles", "executed_order"}},
                         {k: v for k, v in old_order.items() if k not in {"manifest_id", "plan_id", "planned_n_bundles", "executed_order"}})
        canonical = (prospective / "neg8-refcorpus-r01.json").read_bytes()
        for i in range(13, 19):
            row = order["executed_order"][i - 1]
            expected = {**old_order["executed_order"][-1], "index": i, "rep": i, "block_index": i,
                        "run_id": ids[i - 1], "config": f"{ids[i - 1]}.json"}
            self.assertEqual(row, expected)
            raw = (prospective / row["config"]).read_bytes()
            self.assertEqual(len(raw), 1319)
            self.assertEqual(raw, canonical.replace(b'"run_id": "neg8-refcorpus-r01"',
                                                    f'"run_id": "{ids[i - 1]}"'.encode()))

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
                    self.assertEqual(json.loads(path.read_bytes())["sampling"]["idle_seconds"], V5_IDLE_SECONDS)
        self.assertEqual(count, 15)

    def gamma_dispatches(self):
        """(stage id, runs-root binding, run id) for every member GAMMA's collection stages launch."""
        pack = ROOT / "configs/campaigns" / PACKS[-1]
        tree = json.loads((pack / "plan_tree.json").read_bytes())
        external = {row["input_id"]: row for row in tree["external_inputs"]}
        rows = []
        for stage in tree["stage_graph"]:
            if stage["kind"] != "campaign_collection":
                continue
            arguments = stage["launch"]["commands"][0]["argv_template"]["arguments"]
            root = next(value["value"] for flag, value in zip(arguments, arguments[1:])
                        if flag == {"kind": "literal", "value": "--runs-dir"})
            reference = stage["input_ref"]
            if reference["kind"] == "external_input":
                source = external[reference["input_id"]]
                manifest_path = ROOT / source["manifest_path"]
                self.assertEqual(hashlib.sha256(manifest_path.read_bytes()).hexdigest(), source["manifest_sha256"])
                # The stage launches the directory whose manifest the plan tree pins.
                self.assertEqual(ROOT / arguments[0]["value"], manifest_path.parent)
                order = json.loads(manifest_path.read_bytes())["executed_order"]
                self.assertEqual([row["run_id"] for row in order], [row["run_id"] for row in source["members"]])
            else:
                order = json.loads((pack / reference["path"]).read_bytes())["executed_order"]
            rows.extend((stage["stage_id"], root, row["run_id"], row.get("role"), row.get("sentinel_position"))
                        for row in order)
        return tree, rows

    def test_gamma_launches_no_run_id_twice_into_one_runs_root(self):
        """GAMMA-INTERIOR-REFERENCES-01 (lane L10): run_campaign skips a run id whose bundle exists."""
        _tree, rows = self.gamma_dispatches()
        self.assertEqual(len(rows), 107)
        pairs = [(root, run_id) for _stage, root, run_id, _role, _position in rows]
        self.assertEqual(len(set(pairs)), len(pairs),
                         [pair for pair in set(pairs) if pairs.count(pair) > 1])
        self.assertEqual(len({run_id for _root, run_id in pairs}), 107)

    def test_gamma_has_one_neg8_midpoint_and_two_diagnostic_interior_references(self):
        """The whole-window NEG-8 screen accepts exactly 3 start + 1 midpoint + 3 end references."""
        from scripts.run_campaign import _declared_neg8_reference_position

        tree, rows = self.gamma_dispatches()
        claim = [row for row in rows if row[1] == "claim_runs_root"]
        positions = [_declared_neg8_reference_position(role, position) for _s, _r, _i, role, position in claim]
        self.assertEqual((positions.count("start"), positions.count("midpoint"), positions.count("end")), (3, 1, 3))
        self.assertNotIn("invalid", positions)
        interior = {stage: (run_id, role) for stage, _root, run_id, role, _position in claim
                    if stage in {"gamma-reference-decode-midpoint", "gamma-reference-arm-boundary",
                                 "gamma-reference-prefill-midpoint"}}
        self.assertEqual(interior, {
            "gamma-reference-decode-midpoint": ("gamma-interior-reference-decode-midpoint",
                                                "window_interior_reference_diagnostic"),
            "gamma-reference-arm-boundary": ("neg8-window-midpoint", "neg8_daily_reference_midpoint"),
            "gamma-reference-prefill-midpoint": ("gamma-interior-reference-prefill-midpoint",
                                                 "window_interior_reference_diagnostic"),
        })
        # The arm boundary sits at the window's temporal midpoint: 40 science members on each side.
        order = [stage["stage_id"] for stage in tree["stage_graph"] if stage["kind"] == "campaign_collection"]
        boundary = order.index("gamma-reference-arm-boundary")
        science = [stage["stage_id"] for stage in tree["stage_graph"] if stage["stage_id"].startswith("gamma-science-")]
        counts = {stage["stage_id"]: stage["expected_count"] for stage in tree["stage_graph"]}
        self.assertEqual(sum(counts[s] for s in science if order.index(s) < boundary), 40)
        self.assertEqual(sum(counts[s] for s in science if order.index(s) > boundary), 40)
        # Each diagnostic config is the shared midpoint config byte for byte except run_id.
        shared = (ROOT / "configs/campaigns/window_references_v5/midpoint/neg8-window-midpoint.json").read_bytes()
        for name in ("decode_midpoint", "prefill_midpoint"):
            run_id = f"gamma-interior-reference-{name.replace('_', '-')}"
            raw = (ROOT / "configs/campaigns/gamma_interior_references_v5" / name / f"{run_id}.json").read_bytes()
            self.assertEqual(raw, shared.replace(b'"run_id": "neg8-window-midpoint"', f'"run_id": "{run_id}"'.encode()))
            self.assertEqual(json.loads(raw)["sampling"]["idle_seconds"], V5_IDLE_SECONDS)

    def test_generator_refuses_interior_reference_bytes_that_drift_from_the_shared_midpoint(self):
        import importlib.util
        import shutil

        spec = importlib.util.spec_from_file_location(
            "gamma_generator_under_test", ROOT / "configs/campaigns" / PACKS[-1] / "generate_configs.py")
        generator = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = generator
        self.addCleanup(sys.modules.pop, spec.name, None)
        spec.loader.exec_module(generator)
        self.assertEqual(set(generator.interior_reference_inputs()),
                         {"gamma-reference-decode-midpoint", "gamma-reference-prefill-midpoint"})
        with tempfile.TemporaryDirectory(prefix="v5-interior-") as temporary:
            root = Path(temporary)
            for relative in ("configs/campaigns/window_references_v5", "configs/campaigns/gamma_interior_references_v5"):
                shutil.copytree(ROOT / relative, root / relative)
            generator.REPO_ROOT = root
            generator.interior_reference_inputs()
            config = (root / "configs/campaigns/gamma_interior_references_v5/prefill_midpoint"
                      "/gamma-interior-reference-prefill-midpoint.json")
            config.write_bytes(config.read_bytes().replace(b'"output_tokens": 256', b'"output_tokens": 255'))
            with self.assertRaisesRegex(ValueError, "interior reference bytes differ"):
                generator.interior_reference_inputs()


if __name__ == "__main__":
    unittest.main()
