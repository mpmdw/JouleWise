from __future__ import annotations

import copy
import hashlib
import inspect
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

from joulewise.arm_readiness import (
    ArmReadinessError,
    _pack_record,
    consume_launch_capability,
    generate_arm_receipt,
    generate_dry_run_receipt,
    generate_freeze_receipt,
    gnu_sidecar,
    render_json,
    reviewed_main,
    scan_receipt_namespace,
    validate_freeze_receipt,
    verify_arm_receipt,
    verify_receipt,
)
from tests.test_arm_readiness_schemas import (
    sample_arm,
    sample_dry_run,
    sample_freeze,
    sample_frozen_projection,
    sample_identity_receipt,
)


ROOT = Path(__file__).resolve().parents[1]
PACK_NAME = "d117_floor_qwen25_1p5b_v1"


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def make_go_fixture(
    pack_name: str = PACK_NAME, profile: str = "ALPHA"
) -> tuple[tempfile.TemporaryDirectory[str], Path, Path, Path, Path]:
    temporary = tempfile.TemporaryDirectory()
    repo = Path(temporary.name) / "repo"
    pack = repo / "configs/campaigns" / pack_name
    registry_source = ROOT / "configs/arm_readiness/d117_row_registry_v1.json"
    registry_target = repo / "configs/arm_readiness/d117_row_registry_v1.json"
    registry_target.parent.mkdir(parents=True)
    registry_target.write_bytes(registry_source.read_bytes())
    pack.mkdir(parents=True)
    plan_raw = render_json({"plan_id": "plan-test"})
    (pack / "calibration_plan.json").write_bytes(plan_raw)
    registry_sha = hashlib.sha256(registry_target.read_bytes()).hexdigest()
    identity_ids = (
        ("A/decode", "A/prefill_p256", "B/decode", "B/prefill_p256")
        if profile == "GAMMA"
        else (profile.lower(),)
    )
    identity_receipt = sample_identity_receipt(
        pack_id=pack_name, identity_unit_ids=identity_ids
    )
    identity_raw = render_json(identity_receipt)
    identity_sha = hashlib.sha256(identity_raw).hexdigest()
    identity_relative = "identity_pin_projection.receipts/projection-0001.json"
    identity_path = pack / identity_relative
    identity_path.parent.mkdir()
    identity_path.write_bytes(identity_raw)
    identity_path.with_suffix(".sha256").write_bytes(
        gnu_sidecar(identity_sha, identity_path.name)
    )
    tree = {
        "plan": {"path": "calibration_plan.json", "plan_id": "plan-test"},
        "window_identity": {"window_id": "window-test", "evidence_root_id": "evidence-test"},
        "roots": {
            "claim_root_leaf": "claim",
            "bound_root_leaf": "bound",
        },
        "acceptance_policy": {"selection": "issued_d116_artifact_only", "issued": "d079"},
        "arm_attachments": {
            "identity_pin_projection": sample_frozen_projection(
                identity_relative, identity_sha, identity_ids
            ),
            "arm_readiness": {
                "contract_id": "D-134",
                "required_before_arm": True,
                "row_registry": {
                    "registry_id": "d117-row-registry-v1",
                    "path": "configs/arm_readiness/d117_row_registry_v1.json",
                    "sha256": registry_sha,
                    "plan_profile": profile,
                },
                "freeze_receipt": None,
                "arm_receipt_namespace": "arm_readiness.receipts/arm-<4+ digits>.json",
                "pack_digest_algorithm": "joulewise.committed_pack_tree_sha256.v1",
            }
        },
    }
    tree_raw = render_json(tree)
    (pack / "plan_tree.json").write_bytes(tree_raw)
    (pack / "plan_tree.sha256").write_bytes(
        gnu_sidecar(hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json")
    )
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "tests@joulewise.invalid")
    git(repo, "config", "user.name", "JouleWise tests")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "pack")
    git(repo, "branch", "-M", "main")
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")

    custody = Path(temporary.name) / "window-custody"
    context_root = Path(temporary.name) / "context"
    context = sample_arm(context_root)["arm_context"]
    for name in (
        "claim_runs_root",
        "bound_runs_root",
        "custody_root",
        "quarantine_root",
        "claim_backup_destination",
        "bound_backup_destination",
    ):
        Path(context[name]).mkdir(parents=True)
    Path(context["waiver_path"]).write_bytes(render_json([]))
    arm = sample_arm(context_root)
    arm["pack"] = _pack_record(pack)
    arm["reviewed_main"] = reviewed_main(pack)
    arm["arm_context"] = context
    arm["row_registry"]["sha256"] = registry_sha
    namespace = custody / pack_name / "arm_readiness.receipts"
    namespace.mkdir(parents=True)
    arm_path = namespace / "arm-0001.json"
    raw = render_json(arm)
    arm_path.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    (namespace / "arm-0001.json.sha256").write_bytes(
        gnu_sidecar(digest, "arm-0001.json")
    )
    return temporary, repo, pack, custody, arm_path


class ArmReadinessLifecycleTests(unittest.TestCase):
    def write_namespace_receipt(self, root: Path, name: str, receipt: dict) -> Path:
        root.mkdir(parents=True, exist_ok=True)
        path = root / name
        raw = render_json(receipt)
        path.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        (root / f"{name}.sha256").write_bytes(gnu_sidecar(digest, name))
        return path

    def test_freeze_receipts_can_never_carry_go(self) -> None:
        receipt = sample_freeze()
        receipt["arm_disposition"] = "GO"
        with self.assertRaises(ArmReadinessError):
            validate_freeze_receipt(receipt)

    def test_freeze_generation_is_byte_idempotent_and_sidecar_exact(self) -> None:
        temporary, _repo, pack, _custody, _arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        first = generate_freeze_receipt(pack)
        path = Path(first["receipt_path"])
        raw_before = path.read_bytes()
        sidecar_before = path.with_name(f"{path.name}.sha256").read_bytes()
        tree_raw = (pack / "plan_tree.json").read_bytes()
        self.assertEqual(
            tree_raw,
            __import__(
                "joulewise.arm_readiness", fromlist=["_render_plan_tree"]
            )._render_plan_tree(json.loads(tree_raw)),
        )
        second = generate_freeze_receipt(pack)
        self.assertFalse(second["mutated"])
        self.assertEqual(path.read_bytes(), raw_before)
        self.assertEqual(
            sidecar_before,
            gnu_sidecar(hashlib.sha256(raw_before).hexdigest(), path.name),
        )
        verified = verify_receipt(pack, path)
        self.assertEqual(verified["receipt_sha256"], first["receipt_sha256"])
        path.with_name(f"{path.name}.sha256").write_bytes(
            gnu_sidecar("0" * 64, path.name)
        )
        with self.assertRaisesRegex(ArmReadinessError, "sidecar"):
            verify_receipt(pack, path)

    def test_governed_namespace_five_digits_malformed_orphan_duplicate_and_successor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "receipts"
            first = sample_arm(temporary)
            first["receipt_id"] = "arm-10000"
            self.write_namespace_receipt(root, "arm-10000.json", first)
            scanned = scan_receipt_namespace(root, "arm")
            self.assertEqual(scanned[0]["number"], 10000)

            duplicate = copy.deepcopy(first)
            self.write_namespace_receipt(root, "arm-10001.json", duplicate)
            with self.assertRaisesRegex(ArmReadinessError, "receipt_id|semantic"):
                scan_receipt_namespace(root, "arm")

        anomaly_cases = ("malformed", "orphan", "sidecar-only", "id-mismatch")
        for case in anomaly_cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "receipts"
                root.mkdir()
                if case == "malformed":
                    (root / "notes.txt").write_text("not governed")
                elif case == "orphan":
                    (root / "arm-0001.json").write_bytes(render_json(sample_arm(temporary)))
                elif case == "id-mismatch":
                    receipt = sample_arm(temporary)
                    receipt["receipt_id"] = "arm-0002"
                    self.write_namespace_receipt(root, "arm-0001.json", receipt)
                else:
                    (root / "arm-0001.json.sha256").write_text("0" * 64 + "  arm-0001.json\n")
                with self.assertRaises(ArmReadinessError):
                    scan_receipt_namespace(root, "arm")

    def test_semantic_successor_stales_predecessor(self) -> None:
        temporary, _repo, pack, custody, arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        first, first_raw, first_sha = __import__("joulewise.arm_readiness", fromlist=["_read_arm_with_sidecar"])._read_arm_with_sidecar(arm_path)
        successor = copy.deepcopy(first)
        successor["receipt_id"] = "arm-0002"
        successor["supersedes"] = {
            "receipt_id": first["receipt_id"],
            "receipt_path": "arm_readiness.receipts/arm-0001.json",
            "receipt_sha256": first_sha,
            "pack_id": first["pack"]["pack_id"],
            "pack_sha256": first["pack"]["pack_sha256"],
        }
        self.write_namespace_receipt(arm_path.parent, "arm-0002.json", successor)
        with self.assertRaisesRegex(ArmReadinessError, "successor"):
            verify_arm_receipt(pack, arm_path)

    def test_arm_receipt_must_be_in_the_exact_governed_namespace(self) -> None:
        temporary, _repo, pack, custody, arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        wrong_namespace = custody / pack.name / "lookalike.receipts"
        wrong_namespace.mkdir()
        wrong_path = wrong_namespace / arm_path.name
        wrong_path.write_bytes(arm_path.read_bytes())
        wrong_path.with_name(f"{wrong_path.name}.sha256").write_bytes(
            arm_path.with_name(f"{arm_path.name}.sha256").read_bytes()
        )
        with self.assertRaisesRegex(ArmReadinessError, "arm_readiness.receipts"):
            verify_arm_receipt(pack, wrong_path)

    def test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses(self) -> None:
        from tests.test_arm_readiness_dry_run import install_passing_freeze
        from tests.test_arm_readiness_integration import (
            clear_initial_arm,
            install_passing_evidence,
            synthetic_identity_verifier,
        )
        from unittest import mock

        temporary, repo, pack, custody, _arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        clear_initial_arm(custody, pack.name)
        install_passing_freeze(repo, pack)
        from joulewise.arm_readiness import generate_arm_receipt, generate_dry_run_receipt

        dry = generate_dry_run_receipt(
            pack,
            custody,
            "race-rehearsal",
            Path(temporary.name) / "race-synthetic",
        )
        self.assertEqual(dry["status"], "PASS", dry)
        install_passing_evidence(pack, custody)
        context = sample_arm(Path(temporary.name) / "context")["arm_context"]
        with mock.patch(
            "joulewise.arm_readiness.verify_frozen_projection",
            side_effect=synthetic_identity_verifier,
        ):
            arm_result = generate_arm_receipt(pack, context, custody)
        self.assertEqual(arm_result["status"], "PASS", arm_result)
        arm_path = Path(arm_result["receipt_path"])
        barrier = threading.Barrier(8)
        outcomes: list[str] = []
        lock = threading.Lock()

        def consume() -> None:
            barrier.wait()
            try:
                result = consume_launch_capability(pack, arm_path, custody)
                outcome = result["status"]
            except ArmReadinessError as exc:
                outcome = exc.reason_code
            with lock:
                outcomes.append(outcome)

        threads = [threading.Thread(target=consume) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.assertEqual(outcomes.count("CONSUMED"), 1, outcomes)
        self.assertEqual(outcomes.count("readiness_record_consumed"), 7, outcomes)
        with self.assertRaisesRegex(ArmReadinessError, "already consumed"):
            consume_launch_capability(pack, arm_path, custody)

    def test_dry_run_is_rejected_by_launcher(self) -> None:
        temporary, _repo, pack, custody, arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        dry = sample_dry_run(temporary.name)
        dry_path = custody / PACK_NAME / "arm_readiness.dry_run.receipts/dry-run-0001.json"
        dry_path.parent.mkdir(parents=True)
        raw = render_json(dry)
        dry_path.write_bytes(raw)
        (dry_path.parent / "dry-run-0001.json.sha256").write_bytes(
            gnu_sidecar(hashlib.sha256(raw).hexdigest(), dry_path.name)
        )
        with self.assertRaisesRegex(ArmReadinessError, "dry-run"):
            consume_launch_capability(pack, dry_path, custody)

    def test_cli_derives_conclusions_and_rejects_override_options(self) -> None:
        script = ROOT / "scripts/generate_arm_readiness.py"
        forbidden = (
            "--row-verdict",
            "--applicability",
            "--pack-sha256",
            "--identity-pin",
            "--evidence-path",
            "--reason-code",
            "--output",
        )
        for option in forbidden:
            completed = subprocess.run(
                [sys.executable, str(script), "freeze", "--pack-root", "/tmp/pack", option, "operator-value"],
                text=True,
                capture_output=True,
            )
            with self.subTest(option=option):
                self.assertEqual(completed.returncode, 2)
                self.assertIn("unrecognized arguments", completed.stderr)

    def test_public_generation_signatures_expose_no_conclusion_overrides(self) -> None:
        forbidden = {
            "row_verdict",
            "applicability",
            "pack_sha256",
            "identity_pin",
            "evidence_path",
            "reason_code",
            "output",
        }
        for function in (
            generate_freeze_receipt,
            generate_dry_run_receipt,
            generate_arm_receipt,
            consume_launch_capability,
        ):
            with self.subTest(function=function.__name__):
                self.assertTrue(
                    forbidden.isdisjoint(inspect.signature(function).parameters)
                )


if __name__ == "__main__":
    unittest.main()
