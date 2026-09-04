"""Counterfactual and parity checks for the shared campaign-generator core."""

from __future__ import annotations

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
LEGACY_FAMILY_GENERATORS = tuple(
    path for path in D117_GENERATORS if path.parent.name != "d117_contrast_v5"
)
DIRECT_SHARED_FUNCTIONS = (
    "actual_pack_paths",
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

    def test_unfrozen_d117_generator_uses_the_one_shared_write_core(self) -> None:
        """Restoring any removed local copy makes this identity test fail."""

        self.assertEqual(len(D117_GENERATORS), 10)
        path = ROOT / "configs/campaigns/d117_contrast_v5/generate_configs.py"
        generator = load_generator(path)
        for name in DIRECT_SHARED_FUNCTIONS:
            self.assertIs(getattr(generator, name), getattr(core, name))
        self.assertIs(
            generator.render_json.shared_implementation,
            core.render_json,
        )

    def test_frozen_generators_remain_self_contained_custody_snapshots(self) -> None:
        """The extraction must not rewrite hash-pinned historical evidence."""

        self.assertEqual(len(LEGACY_FAMILY_GENERATORS), 9)
        for path in LEGACY_FAMILY_GENERATORS:
            with self.subTest(generator=path.parent.name):
                source = path.read_text(encoding="utf-8")
                self.assertNotIn("joulewise.campaign_generator_core", source)
                self.assertIn("def validate_generation_write_boundary", source)

    def test_identity_factory_refuses_a_family_downgrade(self) -> None:
        identity_class = core.make_generation_identity_class(
            module_name=__name__,
            pack_rel=Path("configs/campaigns/example_floor_v6"),
            current_family_suffix="_v6",
            preserve_current_frozen_bytes=False,
            draft_status="draft",
            frozen_status="frozen",
            freeze_aware_status=lambda _value: "draft",
            arm_readiness_attachment=lambda: {"freeze_receipt": None},
        )
        with self.assertRaisesRegex(ValueError, "refuses the downgrade target"):
            identity_class(
                pack_id="example_floor_v5",
                family_suffix="_v5",
                preserve_current_frozen_bytes=False,
            )

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
