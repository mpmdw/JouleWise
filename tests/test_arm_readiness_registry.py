from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise.arm_readiness import (
    ArmReadinessError,
    applicability_for_row,
    gnu_sidecar,
    load_registry,
    render_json,
    validate_freeze_receipt,
)
from tests.test_arm_readiness_schemas import sample_freeze


ROOT = Path(__file__).resolve().parents[1]
PACKS = {
    "ALPHA": "d117_floor_qwen25_1p5b_v1",
    "BETA": "d117_floor_qwen25_7b_v1",
    "GAMMA": "d117_contrast_qwen25_1p5b_vs_7b_v1",
}
PAGES = {
    "ALPHA": ROOT / "docs/phase_2/alpha_arm_readiness.md",
    "BETA": ROOT / "docs/phase_2/beta_arm_readiness.md",
    "GAMMA": ROOT / "docs/phase_2/gamma_arm_readiness.md",
}
ROW_ID_RE = re.compile(r"`((?:desk|privilege|clock|t0)\.[a-z0-9_]+)`")
EXPECTED_ROW_IDS = [
    "clock.correct_and_prior_state",
    "clock.network_time_off",
    "clock.restore_recipe",
    "desk.acceptance_owner",
    "desk.acceptance_successor",
    "desk.arming_procedure",
    "desk.current_pack",
    "desk.estimator_identity",
    "desk.identity_pin_projection",
    "desk.mint_trust",
    "desk.multicell_mint",
    "desk.pack_family",
    "desk.reason_code_plumbing",
    "desk.receipt_oracle",
    "desk.recovery_ledger_path",
    "desk.reviewed_checkout",
    "desk.terminal_review",
    "desk.three_window_regression",
    "desk.under_lease_rehearsal",
    "privilege.activation_fence",
    "privilege.fresh_authorization",
    "privilege.installed_bytes",
    "privilege.isolated_interpreter",
    "t0.background_quiet",
    "t0.campaign_lock_absent",
    "t0.display_thermal_idle",
    "t0.fresh_roots_waivers",
    "t0.ledger_reservation",
    "t0.machine_readiness",
    "t0.no_stray_keepawake",
    "t0.offline_inputs",
    "t0.passwordless_powermetrics",
    "t0.power_path",
    "t0.single_launch_capability",
    "t0.storage_backup_capacity",
]


class ArmReadinessRegistryTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.registry, cls.raw = load_registry(ROOT)
        cls.rows = {row["row_id"]: row for row in cls.registry["rows"]}

    def test_registry_has_complete_unique_35_row_profiles(self) -> None:
        self.assertEqual(len(self.rows), 35)
        self.assertEqual(list(self.rows), EXPECTED_ROW_IDS)
        profiles = self.registry["plan_profiles"]
        self.assertEqual([profile["profile_id"] for profile in profiles], ["ALPHA", "BETA", "GAMMA"])
        for profile in profiles:
            self.assertEqual(profile["required_row_ids"], list(self.rows))
            self.assertEqual(profile["window_kind"], profile["profile_id"])
        self.assertEqual(
            {row["applicability_rule"] for row in self.rows.values()},
            {"ALWAYS", "CLOCK_HELPER_ONLY", "SUCCESSOR_ACCEPTANCE_ONLY"},
        )

    def test_markdown_row_id_parity_exactly_once_for_each_profile(self) -> None:
        for profile in self.registry["plan_profiles"]:
            profile_id = profile["profile_id"]
            observed = ROW_ID_RE.findall(PAGES[profile_id].read_text(encoding="utf-8"))
            with self.subTest(profile=profile_id):
                self.assertEqual(len(observed), len(set(observed)))
                self.assertEqual(set(observed), set(profile["required_row_ids"]))

    def test_only_registered_conditional_rules_can_be_not_applicable(self) -> None:
        for row in self.rows.values():
            with self.subTest(row=row["row_id"], route="manual-issued"):
                observed = applicability_for_row(
                    row, clock_route="MANUAL", successor_acceptance=False
                )
                expected = (
                    "NOT_APPLICABLE"
                    if row["applicability_rule"]
                    in {"CLOCK_HELPER_ONLY", "SUCCESSOR_ACCEPTANCE_ONLY"}
                    else "REQUIRED"
                )
                self.assertEqual(observed, expected)
            with self.subTest(row=row["row_id"], route="helper-successor"):
                self.assertEqual(
                    applicability_for_row(
                        row, clock_route="HELPER", successor_acceptance=True
                    ),
                    "REQUIRED",
                )
        mutated = copy.deepcopy(next(iter(self.rows.values())))
        mutated["applicability_rule"] = "OPERATOR_CHOICE"
        with self.assertRaisesRegex(ArmReadinessError, "unknown applicability"):
            applicability_for_row(
                mutated, clock_route="MANUAL", successor_acceptance=False
            )

    def test_plan_tree_slots_bind_profiles_and_never_name_future_arm_receipt(self) -> None:
        registry_sha = hashlib.sha256(self.raw).hexdigest()
        for profile, pack_name in PACKS.items():
            tree = json.loads(
                (ROOT / "configs/campaigns" / pack_name / "plan_tree.json").read_text()
            )
            slot = tree["arm_attachments"]["arm_readiness"]
            with self.subTest(profile=profile):
                self.assertEqual(slot["contract_id"], "D-134")
                self.assertTrue(slot["required_before_arm"])
                self.assertEqual(slot["row_registry"]["plan_profile"], profile)
                self.assertEqual(slot["row_registry"]["sha256"], registry_sha)
                self.assertIsNone(slot["freeze_receipt"])
                serialized = json.dumps(slot, sort_keys=True)
                self.assertNotIn("arm_receipt_path", serialized)
                self.assertNotIn("arm_receipt_sha256", serialized)

    def test_generators_check_both_without_and_with_committed_freeze_receipts(self) -> None:
        for pack_name in PACKS.values():
            completed = subprocess.run(
                [sys.executable, str(ROOT / "configs/campaigns" / pack_name / "generate_configs.py"), "--check"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

        with tempfile.TemporaryDirectory() as temporary:
            clone = Path(temporary) / "repo"
            subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(ROOT), str(clone)], check=True)
            overlay = [
                "joulewise/arm_readiness.py",
                "configs/arm_readiness/d117_row_registry_v1.json",
            ]
            for pack_name in PACKS.values():
                overlay.extend(
                    [
                        f"configs/campaigns/{pack_name}/generate_configs.py",
                        f"configs/campaigns/{pack_name}/plan_tree.json",
                        f"configs/campaigns/{pack_name}/plan_tree.sha256",
                    ]
                )
            for relative in overlay:
                target = clone / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, target)
            for profile, pack_name in PACKS.items():
                pack_root = clone / "configs/campaigns" / pack_name
                receipt = sample_freeze(profile)
                receipt["pack_identity"]["pack_id"] = pack_name
                receipt["row_registry"]["sha256"] = hashlib.sha256(self.raw).hexdigest()
                validate_freeze_receipt(receipt)
                raw = render_json(receipt)
                receipt_dir = pack_root / "arm_readiness.freeze.receipts"
                receipt_dir.mkdir()
                (receipt_dir / "freeze-0001.json").write_bytes(raw)
                digest = hashlib.sha256(raw).hexdigest()
                (receipt_dir / "freeze-0001.json.sha256").write_bytes(
                    gnu_sidecar(digest, "freeze-0001.json")
                )
            for pack_name in PACKS.values():
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(clone / "configs/campaigns" / pack_name / "generate_configs.py"),
                        "--check",
                    ],
                    cwd=clone,
                    text=True,
                    capture_output=True,
                )
                self.assertNotEqual(
                    completed.returncode,
                    0,
                    "an uncommitted freeze receipt must remain an anomalous extra",
                )
            subprocess.run(["git", "config", "user.email", "tests@joulewise.invalid"], cwd=clone, check=True)
            subprocess.run(["git", "config", "user.name", "JouleWise tests"], cwd=clone, check=True)
            subprocess.run(["git", "add", "."], cwd=clone, check=True)
            subprocess.run(["git", "commit", "-qm", "committed freeze state"], cwd=clone, check=True)
            for profile, pack_name in PACKS.items():
                pack_root = clone / "configs/campaigns" / pack_name
                generated = subprocess.run(
                    [sys.executable, str(pack_root / "generate_configs.py")],
                    cwd=clone,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(generated.returncode, 0, generated.stdout + generated.stderr)
                slot = json.loads((pack_root / "plan_tree.json").read_text())["arm_attachments"]["arm_readiness"]
                receipt_raw = (pack_root / "arm_readiness.freeze.receipts/freeze-0001.json").read_bytes()
                self.assertEqual(
                    slot["freeze_receipt"],
                    {
                        "path": "arm_readiness.freeze.receipts/freeze-0001.json",
                        "sha256": hashlib.sha256(receipt_raw).hexdigest(),
                    },
                )
            for pack_name in PACKS.values():
                completed = subprocess.run(
                    [sys.executable, str(clone / "configs/campaigns" / pack_name / "generate_configs.py"), "--check"],
                    cwd=clone,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
