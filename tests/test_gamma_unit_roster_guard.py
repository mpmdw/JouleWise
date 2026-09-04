from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import arm_readiness, identity_pins


ROOT = Path(__file__).resolve().parents[1]
GAMMA_PACK = (
    ROOT / "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3"
)


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected JSON object: {path}")
    return value


def render_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def pack_bytes(pack: Path) -> dict[str, bytes]:
    return {
        path.relative_to(pack).as_posix(): path.read_bytes()
        for path in sorted(pack.rglob("*"))
        if path.is_file()
    }


class GammaUnitRosterGuardTests(unittest.TestCase):
    def _mutated_pack(self, mutate) -> tuple[tempfile.TemporaryDirectory, Path]:
        temporary = tempfile.TemporaryDirectory(prefix="gamma-roster-")
        self.addCleanup(temporary.cleanup)
        pack = Path(temporary.name) / GAMMA_PACK.name
        shutil.copytree(GAMMA_PACK, pack)
        tree_path = pack / "plan_tree.json"
        tree = read_json(tree_path)
        units = tree["arm_attachments"]["identity_pin_projection"][
            "identity_units"
        ]
        mutate(units)
        raw = render_json(tree)
        tree_path.write_bytes(raw)
        (pack / "plan_tree.sha256").write_text(
            f"{hashlib.sha256(raw).hexdigest()}  plan_tree.json\n",
            encoding="ascii",
        )
        return temporary, pack

    def test_freeze_refuses_every_counterfactual_gamma_roster(self) -> None:
        def remove_one(units: list[dict]) -> None:
            units.pop()

        def reorder(units: list[dict]) -> None:
            units[0], units[1] = units[1], units[0]

        def add_one(units: list[dict]) -> None:
            extra = copy.deepcopy(units[-1])
            extra["identity_unit_id"] = "C/decode"
            units.append(extra)

        def redirect_producer(units: list[dict]) -> None:
            units[0]["producer_plan_reference"]["plan_id"] = (
                "plan-d117-floor-wrong-producer-v3"
            )

        for name, mutate in (
            ("three units", remove_one),
            ("reordered units", reorder),
            ("extra unit", add_one),
            ("wrong producer reference", redirect_producer),
        ):
            with self.subTest(counterfactual=name):
                _temporary, pack = self._mutated_pack(mutate)
                before = pack_bytes(pack)
                with self.assertRaisesRegex(
                    identity_pins.IdentityPinProjectionError,
                    "ordered D-131 gamma unit roster",
                ) as refusal:
                    identity_pins.freeze_projection(pack)
                self.assertEqual(
                    refusal.exception.reason_code,
                    "readiness_identity_artifact_unreadable",
                )
                self.assertIn("identity_unit_roster", refusal.exception.observed)
                self.assertEqual(pack_bytes(pack), before)

    def test_arm_authenticates_receipt_roster_against_d131_not_the_pack(self) -> None:
        tree = read_json(GAMMA_PACK / "plan_tree.json")
        projection = tree["arm_attachments"]["identity_pin_projection"]
        malformed_projection = copy.deepcopy(projection)
        malformed_projection["identity_units"].pop()
        receipt_reference = projection["projection_receipt"]
        malformed_receipt = read_json(GAMMA_PACK / receipt_reference["path"])
        malformed_receipt["receipt_kind"] = "arm_reverification"
        malformed_receipt["identity_units"].pop()
        malformed_receipt["pack"]["reviewed_git_commit"] = "a" * 40
        item = {
            "evidence_id": "u11-arm-reverification",
            "receipt_kind": "arm_reverification",
            "namespace": "WINDOW_CUSTODY",
            "path": "receipts/bracket-001/identity-pin-arm-verify.json",
            "sha256": "b" * 64,
            "schema_version": identity_pins.IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA,
            "status": "PASS",
        }

        with (
            mock.patch.object(
                arm_readiness,
                "_read_identity_projection_receipt",
                return_value=(malformed_receipt, b"receipt"),
            ),
            mock.patch.object(
                arm_readiness,
                "_plan_tree",
                return_value=(tree, b"tree"),
            ),
            mock.patch.object(
                arm_readiness,
                "validate_identity_pin_projection",
                return_value=malformed_projection,
            ),
        ):
            with self.assertRaisesRegex(
                arm_readiness.ArmReadinessError,
                "ordered D-131 gamma unit roster",
            ):
                arm_readiness._authenticate_identity_arm_evidence(
                    item,
                    Path("/synthetic/custody"),
                    GAMMA_PACK,
                    {"head_commit": "a" * 40},
                )
            # Counterfactual control: without the arm-side roster comparison,
            # the receipt and pack agree on the same malformed three-unit list
            # and the former self-consistency check returns PASS.
            with mock.patch.object(
                arm_readiness,
                "validate_d131_gamma_identity_unit_roster",
                return_value=None,
            ):
                pseudo_receipt, reasons = (
                    arm_readiness._authenticate_identity_arm_evidence(
                        item,
                        Path("/synthetic/custody"),
                        GAMMA_PACK,
                        {"head_commit": "a" * 40},
                    )
                )
            self.assertEqual(pseudo_receipt["status"], "PASS")
            self.assertEqual(reasons, [])

    def test_current_gamma_projection_and_frozen_receipt_still_validate(self) -> None:
        tree = read_json(GAMMA_PACK / "plan_tree.json")
        projection = tree["arm_attachments"]["identity_pin_projection"]
        identity_pins.validate_identity_pin_projection(
            projection, plan_id=tree["plan"]["plan_id"]
        )

        item, pseudo_receipt, reasons = (
            arm_readiness._load_frozen_identity_evidence(GAMMA_PACK, tree)
        )
        self.assertEqual(reasons, [])
        self.assertEqual(item["status"], "PASS")
        self.assertEqual(pseudo_receipt["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
