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
    ROW_REGISTRY_RELATIVE_PATH,
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
FROZEN_PACK_DIRECTORIES = (
    "arm_readiness.evidence",
    "arm_readiness.freeze.receipts",
    "arm_readiness.sources",
    "identity_pin_projection.receipts",
)
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
        # Dual-coordinate semantics, per MAGISTRATE-RULING.md:124-131.  The
        # ruled repoint moved the LIVE registry -- the one the code loads for
        # new-family work -- to d117_row_registry_v2.json, and deliberately
        # kept the v1 file in-tree, sha-pinned and otherwise unreferenced, as
        # the archival companion of the _v3 generation.  The frozen packs
        # (_v1.._v3) were minted against v1, so their plan_tree bytes still
        # name the ARCHIVAL coordinate; that is the point of keeping v1
        # pinned, because a frozen recorded reference must keep resolving.
        # Both halves are asserted: the archival half inside the loop, the
        # live half after it.
        registry_sha = hashlib.sha256(self.raw).hexdigest()
        archival_relative = "configs/arm_readiness/d117_row_registry_v1.json"
        archival_sha = hashlib.sha256(
            (ROOT / archival_relative).read_bytes()
        ).hexdigest()
        for profile, pack_name in PACKS.items():
            pack_root = ROOT / "configs/campaigns" / pack_name
            tree = json.loads(
                (pack_root / "plan_tree.json").read_text()
            )
            slot = tree["arm_attachments"]["arm_readiness"]
            with self.subTest(profile=profile):
                self.assertEqual(
                    set(slot),
                    {
                        "arm_receipt_namespace",
                        "contract_id",
                        "freeze_receipt",
                        "pack_digest_algorithm",
                        "required_before_arm",
                        "row_registry",
                    },
                )
                self.assertEqual(slot["contract_id"], "D-134")
                self.assertTrue(slot["required_before_arm"])
                self.assertEqual(slot["row_registry"]["plan_profile"], profile)
                # Archival half: a frozen pack keeps the v1 coordinate it was
                # minted against, by design.
                self.assertEqual(slot["row_registry"]["path"], archival_relative)
                self.assertEqual(
                    slot["row_registry"]["registry_id"], "d117-row-registry-v1"
                )
                self.assertEqual(slot["row_registry"]["sha256"], archival_sha)
                self.assertEqual(
                    slot["arm_receipt_namespace"],
                    "arm_readiness.receipts/arm-<4+ digits>.json",
                )
                freeze_reference = slot["freeze_receipt"]
                if freeze_reference is not None:
                    self.assertEqual(set(freeze_reference), {"path", "sha256"})
                    self.assertRegex(
                        freeze_reference["path"],
                        r"\Aarm_readiness\.freeze\.receipts/freeze-[0-9]{4,}\.json\Z",
                    )
                    self.assertRegex(freeze_reference["sha256"], r"\A[0-9a-f]{64}\Z")
                    receipt_path = pack_root / freeze_reference["path"]
                    receipt_raw = receipt_path.read_bytes()
                    receipt_relative = receipt_path.relative_to(ROOT).as_posix()
                    committed_receipt = subprocess.run(
                        ["git", "show", f"HEAD:{receipt_relative}"],
                        cwd=ROOT,
                        check=True,
                        capture_output=True,
                    ).stdout
                    self.assertEqual(receipt_raw, committed_receipt)
                    validate_freeze_receipt(json.loads(receipt_raw))
                    receipt_sha = hashlib.sha256(receipt_raw).hexdigest()
                    self.assertEqual(freeze_reference["sha256"], receipt_sha)
                    sidecar_path = receipt_path.with_name(f"{receipt_path.name}.sha256")
                    sidecar_raw = sidecar_path.read_bytes()
                    sidecar_relative = sidecar_path.relative_to(ROOT).as_posix()
                    committed_sidecar = subprocess.run(
                        ["git", "show", f"HEAD:{sidecar_relative}"],
                        cwd=ROOT,
                        check=True,
                        capture_output=True,
                    ).stdout
                    self.assertEqual(sidecar_raw, committed_sidecar)
                    self.assertEqual(
                        sidecar_raw,
                        gnu_sidecar(receipt_sha, receipt_path.name),
                    )
                serialized = json.dumps(slot, sort_keys=True)
                self.assertNotIn("arm_receipt_path", serialized)
                self.assertNotIn("arm_receipt_sha256", serialized)
        # Live half: new-family work loads the v2 coordinate, and its bytes are
        # a genuinely different registry from the archival one the frozen packs
        # name -- so the two coordinates can never be silently collapsed.
        self.assertEqual(
            ROW_REGISTRY_RELATIVE_PATH.as_posix(),
            "configs/arm_readiness/d117_row_registry_v2.json",
        )
        self.assertEqual(self.registry["registry_id"], "d117-row-registry-v2")
        self.assertNotEqual(registry_sha, archival_sha)

    def test_generators_check_both_without_and_with_committed_freeze_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            frozen_clone = Path(temporary) / "frozen-repo"
            subprocess.run(
                ["git", "clone", "-q", "--no-hardlinks", str(ROOT), str(frozen_clone)],
                check=True,
            )
            overlay = [
                "joulewise/arm_readiness.py",
                "configs/arm_readiness/d117_row_registry_v2.json",
            ]
            for pack_name in PACKS.values():
                pack_relative = Path("configs/campaigns") / pack_name
                shutil.copytree(
                    ROOT / pack_relative,
                    frozen_clone / pack_relative,
                    dirs_exist_ok=True,
                    # A sibling suite that imports a pack's generate_configs.py
                    # by file location leaves __pycache__ inside the v1 pack.
                    # It is never a pack artifact -- the generator's own
                    # actual_pack_paths() already excludes it from the inventory
                    # it audits -- so carrying it into the fixture would fail
                    # this comparison on a build byproduct instead of on pack
                    # bytes.
                    ignore=shutil.ignore_patterns("__pycache__"),
                )
            for relative in overlay:
                target = frozen_clone / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, target)

            # Freeze-time directories are authenticated, committed pack additions
            # rather than draft-generator outputs.
            for pack_name in PACKS.values():
                pack_relative = Path("configs/campaigns") / pack_name
                for directory in FROZEN_PACK_DIRECTORIES:
                    frozen_directory = frozen_clone / pack_relative / directory
                    self.assertTrue(frozen_directory.is_dir())
                    self.assertTrue(any(frozen_directory.iterdir()))
                    completed = subprocess.run(
                        ["git", "status", "--porcelain", "--", str(pack_relative / directory)],
                        cwd=frozen_clone,
                        text=True,
                        capture_output=True,
                        check=True,
                    )
                    self.assertEqual(completed.stdout, "")

            generated_root = Path(temporary) / "generated"
            for pack_name in PACKS.values():
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(
                            frozen_clone
                            / "configs/campaigns"
                            / pack_name
                            / "generate_configs.py"
                        ),
                        "--output-root",
                        str(generated_root),
                    ],
                    cwd=frozen_clone,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

            # Compare every generator-owned file. U11 freeze is allowed to replace
            # only the identity projection, and D-134 is allowed to pin the freeze
            # receipt; the latter is deliberately not normalized away.
            for pack_name in PACKS.values():
                pack_relative = Path("configs/campaigns") / pack_name
                frozen_pack = frozen_clone / pack_relative
                generated_pack = generated_root / pack_relative
                expected_paths = {
                    path.relative_to(generated_pack)
                    for path in generated_pack.rglob("*")
                    if path.is_file()
                }
                expected_paths.add(Path("generate_configs.py"))
                observed_paths = {
                    path.relative_to(frozen_pack)
                    for path in frozen_pack.rglob("*")
                    if path.is_file()
                    and path.relative_to(frozen_pack).parts[0]
                    not in FROZEN_PACK_DIRECTORIES
                }
                self.assertEqual(observed_paths, expected_paths)
                for relative in expected_paths:
                    frozen_path = frozen_pack / relative
                    generated_path = generated_pack / relative
                    if relative == Path("generate_configs.py"):
                        continue
                    if relative == Path("plan_tree.json"):
                        frozen_value = json.loads(frozen_path.read_text())
                        generated_value = json.loads(generated_path.read_text())
                        freeze_reference = frozen_value["arm_attachments"][
                            "arm_readiness"
                        ]["freeze_receipt"]
                        self.assertIsNotNone(freeze_reference)
                        receipt_path = frozen_pack / freeze_reference["path"]
                        receipt_raw = receipt_path.read_bytes()
                        receipt_sha = hashlib.sha256(receipt_raw).hexdigest()
                        self.assertEqual(freeze_reference["sha256"], receipt_sha)
                        self.assertEqual(
                            receipt_path.with_name(
                                f"{receipt_path.name}.sha256"
                            ).read_bytes(),
                            gnu_sidecar(receipt_sha, receipt_path.name),
                        )
                        frozen_value["arm_attachments"]["identity_pin_projection"] = (
                            generated_value["arm_attachments"]["identity_pin_projection"]
                        )
                        generated_downstream = generated_value.get("downstream_contract", {})
                        if "producer_contract" in generated_downstream:
                            frozen_value["downstream_contract"]["producer_contract"][
                                "sha256"
                            ] = generated_downstream["producer_contract"]["sha256"]
                        self.assertEqual(frozen_value, generated_value)
                    elif relative == Path("producer_contract.json"):
                        frozen_value = json.loads(frozen_path.read_text())
                        generated_value = json.loads(generated_path.read_text())
                        frozen_value["identity_pin_projection"] = generated_value[
                            "identity_pin_projection"
                        ]
                        self.assertEqual(frozen_value, generated_value)
                    elif relative == Path("plan_tree.sha256"):
                        for pack in (frozen_pack, generated_pack):
                            plan_raw = (pack / "plan_tree.json").read_bytes()
                            self.assertEqual(
                                (pack / "plan_tree.sha256").read_bytes(),
                                gnu_sidecar(
                                    hashlib.sha256(plan_raw).hexdigest(),
                                    "plan_tree.json",
                                ),
                            )
                    else:
                        self.assertEqual(frozen_path.read_bytes(), generated_path.read_bytes())

            generated_pack_roots = {
                Path("configs/campaigns") / pack_name for pack_name in PACKS.values()
            }
            for generated_path in generated_root.rglob("*"):
                if not generated_path.is_file():
                    continue
                relative = generated_path.relative_to(generated_root)
                if any(root == relative or root in relative.parents for root in generated_pack_roots):
                    continue
                self.assertEqual(
                    (frozen_clone / relative).read_bytes(),
                    generated_path.read_bytes(),
                )

            clone = Path(temporary) / "draft-repo"
            subprocess.run(
                ["git", "clone", "-q", "--no-hardlinks", str(ROOT), str(clone)],
                check=True,
            )
            for relative in overlay:
                target = clone / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, target)
            for pack_name in PACKS.values():
                pack_root = clone / "configs/campaigns" / pack_name
                for directory in FROZEN_PACK_DIRECTORIES:
                    shutil.rmtree(pack_root / directory)
                generated = subprocess.run(
                    [sys.executable, str(pack_root / "generate_configs.py")],
                    cwd=clone,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(generated.returncode, 0, generated.stdout + generated.stderr)
                slot = json.loads((pack_root / "plan_tree.json").read_text())[
                    "arm_attachments"
                ]["arm_readiness"]
                self.assertIsNone(slot["freeze_receipt"])
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
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

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
            # The freeze TRANSACTION -- not the pack generator -- is what records
            # the attachment: `joulewise.arm_readiness` mints the receipt and
            # rewrites plan_tree.json plus its sidecar in the same operation
            # (the plan-tree carrier is the one pre-existing artifact a freeze is
            # allowed to move). A receipt on disk with no attachment is therefore
            # a half-applied fixture, not a state the contract can produce, and
            # relying on a later non-preserve regeneration to attach it is
            # exactly the rewrite the frozen-identity guard now refuses. Emulate
            # the carrier rewrite with the transaction's own byte format so the
            # committed state below is the state a real mint leaves behind.
            render_plan_tree = importlib.import_module(
                "joulewise.arm_readiness",
            )._render_plan_tree
            for pack_name in PACKS.values():
                pack_root = clone / "configs/campaigns" / pack_name
                receipt_relative = "arm_readiness.freeze.receipts/freeze-0001.json"
                receipt_raw = (pack_root / receipt_relative).read_bytes()
                tree = json.loads(
                    (pack_root / "plan_tree.json").read_text(encoding="utf-8")
                )
                tree["arm_attachments"]["arm_readiness"]["freeze_receipt"] = {
                    "path": receipt_relative,
                    "sha256": hashlib.sha256(receipt_raw).hexdigest(),
                }
                tree_raw = render_plan_tree(tree)
                (pack_root / "plan_tree.json").write_bytes(tree_raw)
                (pack_root / "plan_tree.sha256").write_bytes(
                    gnu_sidecar(
                        hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json"
                    )
                )
            subprocess.run(["git", "config", "user.email", "tests@joulewise.invalid"], cwd=clone, check=True)
            subprocess.run(["git", "config", "user.name", "JouleWise tests"], cwd=clone, check=True)
            subprocess.run(["git", "add", "."], cwd=clone, check=True)
            subprocess.run(["git", "commit", "-qm", "committed freeze state"], cwd=clone, check=True)
            for pack_name in PACKS.values():
                pack_root = clone / "configs/campaigns" / pack_name
                # Fail-closed frozen-identity guard: once the committed receipt
                # makes the current identity frozen, EVERY non-preserve
                # regeneration of that identity is refused before a single
                # write -- both the explicit opt-out and the default mode, whose
                # default is False here because the fixture receipt is not the
                # generator's embedded CURRENT_FROZEN_RECEIPT_SHA256.
                for refused_argv in ([], ["--no-preserve-current-frozen-bytes"]):
                    refused = subprocess.run(
                        [
                            sys.executable,
                            str(pack_root / "generate_configs.py"),
                            *refused_argv,
                        ],
                        cwd=clone,
                        text=True,
                        capture_output=True,
                    )
                    self.assertNotEqual(
                        refused.returncode,
                        0,
                        "a committed freeze receipt must refuse non-preserve regeneration",
                    )
                    self.assertIn(
                        "the current frozen identity requires preserve mode",
                        refused.stdout + refused.stderr,
                    )
                # Post-freeze regeneration is EXPLICIT preserve mode, and it is
                # byte-stable: the frozen pack's bytes never move.
                before = {
                    path.relative_to(pack_root): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in pack_root.rglob("*")
                    if path.is_file() and "__pycache__" not in path.parts
                }
                generated = subprocess.run(
                    [
                        sys.executable,
                        str(pack_root / "generate_configs.py"),
                        "--preserve-current-frozen-bytes",
                    ],
                    cwd=clone,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(generated.returncode, 0, generated.stdout + generated.stderr)
                after = {
                    path.relative_to(pack_root): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in pack_root.rglob("*")
                    if path.is_file() and "__pycache__" not in path.parts
                }
                self.assertEqual(after, before)
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
                    [
                        sys.executable,
                        str(clone / "configs/campaigns" / pack_name / "generate_configs.py"),
                        "--check",
                        "--preserve-current-frozen-bytes",
                    ],
                    cwd=clone,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            # Preserve mode replays committed bytes, so the byte comparison
            # inside --check compares the checkout to itself. Prove the leg
            # above still discriminates: the teeth are the attachment
            # authentication the generator performs at import (committed
            # receipt bytes vs HEAD, and vs the receipt the plan pins) and the
            # pack inventory it derives from the pinned reference. Break the
            # pin and the same command must refuse.
            for pack_name in PACKS.values():
                pack_root = clone / "configs/campaigns" / pack_name
                tree_path = pack_root / "plan_tree.json"
                original = tree_path.read_bytes()
                mutated = json.loads(original.decode("utf-8"))
                pin = mutated["arm_attachments"]["arm_readiness"]["freeze_receipt"]
                pin["sha256"] = "0" * 64
                tree_path.write_bytes(render_plan_tree(mutated))
                try:
                    refused = subprocess.run(
                        [
                            sys.executable,
                            str(pack_root / "generate_configs.py"),
                            "--check",
                            "--preserve-current-frozen-bytes",
                        ],
                        cwd=clone,
                        text=True,
                        capture_output=True,
                    )
                finally:
                    tree_path.write_bytes(original)
                self.assertNotEqual(
                    refused.returncode,
                    0,
                    "a plan pin that is not the committed receipt must refuse",
                )
                self.assertIn(
                    "committed freeze receipt is not the receipt the plan pins",
                    refused.stdout + refused.stderr,
                )


if __name__ == "__main__":
    unittest.main()
