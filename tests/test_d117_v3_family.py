"""D-147 S3 regression coverage for the r6-bound D-117 v3 pack family."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

from joulewise.arm_readiness import committed_pack_tree_sha256
from joulewise.calibration_bracketing import acceptance_allowance_rule


ROOT = Path(__file__).resolve().parents[1]
R6_ACCEPTANCE = {
    "acceptance_id": "d079_calibration_acceptance_v2_n17_r6",
    "path": "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json",
    "artifact_sha256": "0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d",
    "derivation_sha256": "18d09aa9d4accb16a8dff770de85cd7e7525bdb0b6e68f1de716e20fb8a9b9f3",
}
R6_ALLOWANCE_RULE = "max(observed_drift_s,0.009724)"
N19_ALLOWANCE_RULE = "max(observed_drift_s,0.010818)"

FAMILIES = (
    {
        "v2": "d117_floor_qwen25_1p5b_v2",
        "v3": "d117_floor_qwen25_1p5b_v3",
        "v3_spec": "configs/floor_mint/d117_qwen25_1p5b_v3_extraction_spec.json",
    },
    {
        "v2": "d117_floor_qwen25_7b_v2",
        "v3": "d117_floor_qwen25_7b_v3",
        "v3_spec": "configs/floor_mint/d117_qwen25_7b_v3_extraction_spec.json",
    },
    {
        "v2": "d117_contrast_qwen25_1p5b_vs_7b_v2",
        "v3": "d117_contrast_qwen25_1p5b_vs_7b_v3",
        "v3_spec": None,
    },
)

V1_V2_SPECS = (
    (
        "configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json",
        "d079_calibration_acceptance_v2_n19",
    ),
    (
        "configs/floor_mint/d117_qwen25_1p5b_v2_extraction_spec.json",
        "d079_calibration_acceptance_v2_n19_r2",
    ),
    (
        "configs/floor_mint/d117_qwen25_7b_extraction_spec.json",
        "d079_calibration_acceptance_v2_n19",
    ),
    (
        "configs/floor_mint/d117_qwen25_7b_v2_extraction_spec.json",
        "d079_calibration_acceptance_v2_n19_r2",
    ),
)

# These are D-134 committed-tree digests, not working-tree inventories.  The
# helper simultaneously proves every v2 disk byte still matches HEAD.
V2_PACK_TREE_SHA256 = {
    "d117_floor_qwen25_1p5b_v2": (
        "95f7c51ca4f2833a69d2767e9a35fcbf028365332edeb36d1b43d73b6eea31b9"
    ),
    "d117_floor_qwen25_7b_v2": (
        "e5ec0f74df3a61daff3ffdb8c6521c2ae69dae25ac6b6490394ee64d89015968"
    ),
    "d117_contrast_qwen25_1p5b_vs_7b_v2": (
        "2fe51b037ad063f932c29445ef60cde24479f76d465d5f013810e0287274e540"
    ),
}

# These directories enter a pack only through the arm-readiness freeze/MINT
# transaction.  They are deliberately absent from generator output, but a
# post-MINT generator check audits the finalized pack inventory named by the
# now-pinned plan tree and therefore needs them as explicit test-fixture state.
MINT_CUSTODY_DIRECTORIES = (
    "arm_readiness.evidence",
    "arm_readiness.freeze.receipts",
    "arm_readiness.sources",
    "identity_pin_projection.receipts",
)


def load_json(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{relative} must contain a JSON object")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generator_command(family: dict[str, Any], output_root: Path) -> list[str]:
    return [
        sys.executable,
        str(
            ROOT
            / "configs/campaigns"
            / family["v2"]
            / "generate_configs.py"
        ),
        "--output-root",
        str(output_root),
        "--pack-id",
        family["v3"],
        "--family-suffix",
        "_v3",
    ]


def seed_mint_custody(family: dict[str, Any], output_root: Path) -> None:
    """Overlay committed non-generator artifacts for finalized-pack checking."""

    relative_pack = Path("configs/campaigns") / family["v3"]
    for directory in MINT_CUSTODY_DIRECTORIES:
        shutil.copytree(
            ROOT / relative_pack / directory,
            output_root / relative_pack / directory,
        )


class D117V3FamilyTests(unittest.TestCase):
    maxDiff = None

    def assert_r6_pin(self, actual: dict[str, Any]) -> None:
        self.assertEqual(
            {key: actual[key] for key in R6_ACCEPTANCE},
            R6_ACCEPTANCE,
        )

    def test_unedited_v2_generators_emit_v3_successors(self) -> None:
        """The production route begins with untouched v2 successor emission."""

        before = {
            family["v2"]: sha256(
                ROOT / "configs/campaigns" / family["v2"] / "generate_configs.py"
            )
            for family in FAMILIES
        }
        with tempfile.TemporaryDirectory(prefix="d117-v2-to-v3-") as temp:
            output_root = Path(temp)
            for family in FAMILIES:
                with self.subTest(family=family["v3"]):
                    command = generator_command(family, output_root)
                    generated = subprocess.run(
                        command,
                        cwd=ROOT,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(generated.returncode, 0, generated.stderr)
                    generated_pack = output_root / "configs/campaigns" / family["v3"]
                    self.assertTrue((generated_pack / "generate_configs.py").is_file())
                    self.assertTrue((generated_pack / "plan_tree.json").is_file())
                    self.assertTrue((generated_pack / "order_manifest.json").is_file())
                    if family["v3_spec"] is not None:
                        self.assertTrue((output_root / family["v3_spec"]).is_file())
                    for directory in MINT_CUSTODY_DIRECTORIES:
                        self.assertFalse((generated_pack / directory).exists())
                    seed_mint_custody(family, output_root)
                    checked = subprocess.run(
                        [*command, "--check"],
                        cwd=ROOT,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(
            {
                family["v2"]: sha256(
                    ROOT
                    / "configs/campaigns"
                    / family["v2"]
                    / "generate_configs.py"
                )
                for family in FAMILIES
            },
            before,
        )

    def test_check_still_refuses_missing_generator_owned_output(self) -> None:
        """The MINT-custody overlay must not make generator checks fail open."""

        family = FAMILIES[0]
        with tempfile.TemporaryDirectory(prefix="d117-v3-missing-owned-") as temp:
            output_root = Path(temp)
            command = generator_command(family, output_root)
            generated = subprocess.run(
                command,
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            seed_mint_custody(family, output_root)

            generated_pack = output_root / "configs/campaigns" / family["v3"]
            (generated_pack / "order_manifest.json").unlink()
            checked = subprocess.run(
                [*command, "--check"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(checked.returncode, 0)
            self.assertIn("missing=order_manifest.json", checked.stderr)

    def test_v3_specs_and_plan_trees_bind_r6_via_generation_resolver(self) -> None:
        self.assertEqual(
            acceptance_allowance_rule(R6_ACCEPTANCE["acceptance_id"]),
            R6_ALLOWANCE_RULE,
        )
        for family in FAMILIES[:2]:
            with self.subTest(spec=family["v3_spec"]):
                assert family["v3_spec"] is not None
                spec = load_json(family["v3_spec"])
                self.assertEqual(len(spec["cells"]), 6)
                for cell in spec["cells"]:
                    basis = cell["calibration_basis"]
                    self.assert_r6_pin(basis["issued_acceptance"])
                    self.assertEqual(basis["allowance_rule"], R6_ALLOWANCE_RULE)

                source = (
                    ROOT
                    / "configs/campaigns"
                    / family["v3"]
                    / "generate_configs.py"
                ).read_text(encoding="utf-8")
                self.assertIn("acceptance_allowance_rule(", source)
                self.assertIn('acceptance_pin()["acceptance_id"]', source)
                self.assertNotIn(
                    '"allowance_rule": "max(observed_drift_s,', source
                )

        for family in FAMILIES[:2]:
            with self.subTest(plan_tree=family["v3"]):
                policy = load_json(
                    f"configs/campaigns/{family['v3']}/plan_tree.json"
                )["acceptance_policy"]
                self.assert_r6_pin(policy["issued_acceptance"])
        contrast_policy = load_json(
            "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/plan_tree.json"
        )["acceptance_policy"]
        self.assertEqual(
            {
                "acceptance_id": contrast_policy["issued_artifact_id"],
                "artifact_sha256": contrast_policy["issued_artifact_sha256"],
                "derivation_sha256": contrast_policy["issued_derivation_sha256"],
            },
            {
                key: R6_ACCEPTANCE[key]
                for key in ("acceptance_id", "artifact_sha256", "derivation_sha256")
            },
        )

    def test_v1_v2_specs_replay_the_n19_resolver_rule(self) -> None:
        for relative, acceptance_id in V1_V2_SPECS:
            with self.subTest(spec=relative):
                spec = load_json(relative)
                self.assertEqual(
                    acceptance_allowance_rule(acceptance_id), N19_ALLOWANCE_RULE
                )
                for cell in spec["cells"]:
                    basis = cell["calibration_basis"]
                    self.assertEqual(
                        basis["issued_acceptance"]["acceptance_id"], acceptance_id
                    )
                    self.assertEqual(basis["allowance_rule"], N19_ALLOWANCE_RULE)

    def test_committed_v2_pack_tree_digests_are_unchanged_at_head(self) -> None:
        for pack_id, expected in V2_PACK_TREE_SHA256.items():
            with self.subTest(pack=pack_id):
                self.assertEqual(
                    committed_pack_tree_sha256(ROOT / "configs/campaigns" / pack_id),
                    expected,
                )


if __name__ == "__main__":
    unittest.main()
