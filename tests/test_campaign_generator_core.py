"""Counterfactual and parity checks for the shared campaign-generator core."""

from __future__ import annotations

import ast
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise import campaign_generator_core as core


ROOT = Path(__file__).resolve().parents[1]
D117_GENERATORS = tuple(
    sorted((ROOT / "configs/campaigns").glob("d117_*/generate_configs.py"))
)
LIVE_V5_GENERATORS = tuple(
    ROOT / "configs/campaigns" / pack_id / "generate_configs.py"
    for pack_id in (
        "d117_contrast_v5",
        "d117_floor_qwen3-1p7b_v5",
        "d117_floor_qwen3-8b_v5",
    )
)
HISTORICAL_GENERATORS = tuple(
    ROOT / "configs/campaigns" / pack_id / "generate_configs.py"
    for pack_id in (
        "d117_contrast_qwen25_1p5b_vs_7b_v1",
        "d117_contrast_qwen25_1p5b_vs_7b_v2",
        "d117_contrast_qwen25_1p5b_vs_7b_v3",
        "d117_floor_qwen25_1p5b_v1",
        "d117_floor_qwen25_1p5b_v2",
        "d117_floor_qwen25_1p5b_v3",
        "d117_floor_qwen25_7b_v1",
        "d117_floor_qwen25_7b_v2",
        "d117_floor_qwen25_7b_v3",
    )
)
DIRECT_SHARED_FUNCTIONS = (
    "actual_pack_paths",
    "make_render_json",
    "sha256_bytes",
    "sidecar_bytes",
    "validate_generation_write_boundary",
)


def load_generator(path: Path):
    module_name = f"test_generator_core_{path.parent.name}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    old = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = old
    return module


class CampaignGeneratorCoreTests(unittest.TestCase):
    maxDiff = None

    def test_d117_generator_census_requires_explicit_live_or_historical_custody(
        self,
    ) -> None:
        self.assertEqual(
            set(D117_GENERATORS),
            set(LIVE_V5_GENERATORS) | set(HISTORICAL_GENERATORS),
        )

    def test_counterfactual_local_write_boundary_cannot_bypass_shared_core(
        self,
    ) -> None:
        """Restoring one generator-local validator makes this regression fail."""

        for path in LIVE_V5_GENERATORS:
            with self.subTest(generator=path.parent.name):
                generator = load_generator(path)
                for name in DIRECT_SHARED_FUNCTIONS:
                    self.assertIs(getattr(generator, name), getattr(core, name))
                self.assertIs(
                    generator.render_json.shared_implementation,
                    core.render_json,
                )

                tree = ast.parse(path.read_text(encoding="utf-8"))
                local_functions = {
                    node.name
                    for node in tree.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
                self.assertTrue(
                    local_functions.isdisjoint(
                        set(DIRECT_SHARED_FUNCTIONS) | {"render_json"}
                    ),
                    f"{path.parent.name} restored a generator-local core helper",
                )

    def test_frozen_generators_remain_self_contained_custody_snapshots(self) -> None:
        """The extraction must not rewrite hash-pinned historical evidence."""

        self.assertEqual(len(HISTORICAL_GENERATORS), 9)
        for path in HISTORICAL_GENERATORS:
            with self.subTest(generator=path.parent.name):
                source = path.read_text(encoding="utf-8")
                self.assertNotIn("joulewise.campaign_generator_core", source)
                self.assertIn("def validate_generation_write_boundary", source)

    def test_shared_boundary_refuses_a_symlinked_ancestor_before_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generator-core-boundary-") as temp:
            root = Path(temp)
            outside = root / "outside"
            outside.mkdir()
            (root / "pack").symlink_to(outside, target_is_directory=True)

            with self.assertRaisesRegex(ValueError, "write ancestor is a symlink"):
                core.validate_generation_write_boundary(
                    root, (Path("pack/calibration_plan.json"),)
                )
            self.assertEqual(list(outside.iterdir()), [])

    def test_shared_boundary_accepts_an_absent_closed_tree_without_writing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generator-core-boundary-") as temp:
            root = Path(temp)
            relative = Path("pack/calibration_plan.json")
            core.validate_generation_write_boundary(root, (relative,))
            self.assertFalse((root / relative).exists())


if __name__ == "__main__":
    unittest.main()
