from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import inspect
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

import joulewise.arm_readiness as readiness
import joulewise.arm_readiness_evidence as evidence_module
from joulewise.arm_readiness import (
    ArmReadinessError,
    _pack_record,
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
from scripts import generate_arm_readiness as arm_readiness_cli
from tests.test_arm_readiness_schemas import (
    sample_arm,
    sample_dry_run,
    sample_evidence,
    sample_freeze,
    sample_freeze_v2,
    sample_frozen_projection,
    sample_identity_receipt,
    TEST_BOOT_SESSION_ID,
)


ROOT = Path(__file__).resolve().parents[1]
PACK_NAME = "d117_floor_qwen25_1p5b_v2"
# The generation-1 ALPHA identity.  It is a historical record, NOT a superseded
# entry that leaves the code: ``_PROFILE_BY_PACK`` keeps it forever (see the
# ``_plan_profile`` docstring and PostSupersessionLayeringTests below).
HISTORICAL_PACK_NAME = "d117_floor_qwen25_1p5b_v1"
LAUNCH_WINDOW_SPEC = importlib.util.spec_from_file_location(
    "arm_readiness_lifecycle_launch_window",
    ROOT / "scripts/launch_window.py",
)
assert LAUNCH_WINDOW_SPEC is not None and LAUNCH_WINDOW_SPEC.loader is not None
launch_window = importlib.util.module_from_spec(LAUNCH_WINDOW_SPEC)
LAUNCH_WINDOW_SPEC.loader.exec_module(launch_window)


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def predecessor_pack_name(pack_name: str) -> str:
    """Return the previous-generation pack ID for a ``_v<N>`` successor."""

    match = re.search(r"_v([0-9]+)$", pack_name)
    if match is None or int(match.group(1)) < 2:
        raise ValueError(f"{pack_name!r} is not a successor pack ID")
    return f"{pack_name[: match.start()]}_v{int(match.group(1)) - 1}"


def identity_unit_ids_for(profile: str) -> tuple[str, ...]:
    return (
        ("A/decode", "A/prefill_p256", "B/decode", "B/prefill_p256")
        if profile == "GAMMA"
        else (profile.lower(),)
    )


def write_predecessor_pack(
    repo: Path,
    pack_name: str,
    profile: str,
    *,
    status: str = "PASS",
    plan_path_spelling: str | None = None,
    identity_status: str = "PASS",
) -> Path:
    """Author a committed historical pack whose freeze-0001 is hand-recorded.

    Deliberately map-free: no live ``_PROFILE_BY_PACK`` entry, no current R2
    resolver derivation, and ``plan_path_spelling`` may carry the superseded
    repository-relative plan reference the committed alpha/beta packs use.  The
    predecessor authenticator must work from these recorded bytes alone.
    """

    pack = repo / "configs/campaigns" / pack_name
    pack.mkdir(parents=True)
    plan_id = f"plan-{pack_name}"
    plan_raw = render_json({"plan_id": plan_id})
    (pack / "calibration_plan.json").write_bytes(plan_raw)
    plan_sha = hashlib.sha256(plan_raw).hexdigest()

    identity_ids = identity_unit_ids_for(profile)
    identity_receipt = sample_identity_receipt(
        pack_id=pack_name,
        identity_unit_ids=identity_ids,
        status=identity_status,
        reason_codes=(
            [] if identity_status == "PASS" else ["readiness_identity_environment_dirty"]
        ),
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

    registry_sha = hashlib.sha256(
        (repo / "configs/arm_readiness/d117_row_registry_v1.json").read_bytes()
    ).hexdigest()
    receipt = {
        "schema_version": readiness.FREEZE_RECEIPT_SCHEMA,
        "receipt_kind": "freeze",
        "receipt_id": "freeze-0001",
        "status": status,
        "arm_disposition": "NOT_APPLICABLE",
        "issued_at_utc": "2026-08-13T00:00:00Z",
        "pack_identity": {
            "pack_id": pack_name,
            "plan_id": plan_id,
            "window_id": f"window-{pack_name}",
            # A foreign absolute path: the historical mint machine's checkout.
            "pack_root": f"/Users/historical/checkout/configs/campaigns/{pack_name}",
            "plan_path": "calibration_plan.json",
            "plan_sha256": plan_sha,
        },
        "row_registry": {
            "registry_id": "d117-row-registry-v1",
            "path": "configs/arm_readiness/d117_row_registry_v1.json",
            "sha256": registry_sha,
            "plan_profile": profile,
        },
        "evidence": [
            {
                "evidence_id": "u11-freeze-projection",
                "receipt_kind": str(identity_receipt["receipt_kind"]),
                "namespace": "PACK",
                "path": identity_relative,
                "sha256": identity_sha,
                "schema_version": readiness.IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA,
                "status": identity_status,
            }
        ],
        "rows": [],
        "refusals": (
            []
            if status == "PASS"
            else [
                {
                    "type": "CUSTODY",
                    "code": "readiness_pack_digest_mismatch",
                    "row_id": None,
                    "evidence_id": None,
                }
            ]
        ),
        "supersedes": None,
        "assurance": copy.deepcopy(readiness.ASSURANCE),
    }
    validate_freeze_receipt(receipt)
    receipt_raw = render_json(receipt)
    receipt_sha = hashlib.sha256(receipt_raw).hexdigest()
    namespace = pack / "arm_readiness.freeze.receipts"
    namespace.mkdir()
    (namespace / "freeze-0001.json").write_bytes(receipt_raw)
    (namespace / "freeze-0001.json.sha256").write_bytes(
        gnu_sidecar(receipt_sha, "freeze-0001.json")
    )

    tree = {
        "plan": {
            "path": plan_path_spelling
            or "calibration_plan.json",
            "plan_id": plan_id,
        },
        "window_identity": {
            "window_id": f"window-{pack_name}",
            "evidence_root_id": "evidence-test",
        },
        "acceptance_policy": {
            "selection": "issued_d116_artifact_only",
            "issued": "d079",
        },
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
                "freeze_receipt": {
                    "path": "arm_readiness.freeze.receipts/freeze-0001.json",
                    "sha256": receipt_sha,
                },
                "arm_receipt_namespace": "arm_readiness.receipts/arm-<4+ digits>.json",
                "pack_digest_algorithm": "joulewise.committed_pack_tree_sha256.v1",
            },
        },
    }
    tree_raw = render_json(tree)
    (pack / "plan_tree.json").write_bytes(tree_raw)
    (pack / "plan_tree.sha256").write_bytes(
        gnu_sidecar(hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json")
    )
    return pack


def make_go_fixture(
    pack_name: str = PACK_NAME,
    profile: str = "ALPHA",
    *,
    predecessor_status: str = "PASS",
    predecessor_plan_path_spelling: str | None = None,
    identity_status: str = "PASS",
) -> tuple[tempfile.TemporaryDirectory[str], Path, Path, Path, Path]:
    """Build a committed one-pack repository.

    A successor pack ID (``_v2`` or later) additionally gets its committed
    previous-generation pack, so D-139 chain authentication has real bytes to
    authenticate.  ``predecessor_pack_root`` recovers that path.

    ``identity_status`` authors THIS pack's own identity-projection receipt as a
    schema-valid REFUSE, which is the only lawful way to mint a freeze receipt
    whose recorded REFUSE was caused by a refusing dependency.
    """

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
        pack_id=pack_name,
        identity_unit_ids=identity_ids,
        status=identity_status,
        reason_codes=(
            [] if identity_status == "PASS" else ["readiness_identity_environment_dirty"]
        ),
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
    if readiness._pack_generation(pack_name) > 1:
        write_predecessor_pack(
            repo,
            predecessor_pack_name(pack_name),
            profile,
            status=predecessor_status,
            plan_path_spelling=predecessor_plan_path_spelling,
        )
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "tests@joulewise.invalid")
    git(repo, "config", "user.name", "JouleWise tests")
    # EVIDENCE-AUTHOR-GIT-TEARDOWN-01: detached git maintenance spawned by
    # fixture commits can outlive the test and race TemporaryDirectory
    # cleanup under .git (ENOTEMPTY — the #121 mechanism class). Disable it
    # at creation so nothing races cleanup; prevention over errno tolerance
    # because no test in this fixture family asserts maintenance behavior.
    git(repo, "config", "gc.auto", "0")
    git(repo, "config", "maintenance.auto", "false")
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


def predecessor_pack_root(repo: Path, pack_name: str) -> Path:
    return repo / "configs/campaigns" / predecessor_pack_name(pack_name)


class ArmReadinessLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        patcher = mock.patch.object(
            readiness, "_current_boot_session_id", return_value=TEST_BOOT_SESSION_ID
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def write_namespace_receipt(self, root: Path, name: str, receipt: dict) -> Path:
        root.mkdir(parents=True, exist_ok=True)
        path = root / name
        raw = render_json(receipt)
        path.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        (root / f"{name}.sha256").write_bytes(gnu_sidecar(digest, name))
        return path

    def install_launch_manifest(
        self, root: Path, pack: Path, custody: Path, arm_path: Path
    ) -> tuple[argparse.Namespace, list[str]]:
        window_root = custody / "window-plan"
        window_root.mkdir()
        (window_root / "window.env").write_text("PACK_ROOT=/tmp/pack\n")
        chain_path = window_root / "window-chain.zsh"
        chain_path.write_text("#!/bin/zsh\nexit 0\n")
        exec_argv = [
            "/usr/bin/caffeinate",
            "-is",
            "/bin/zsh",
            str(chain_path),
            str(window_root),
        ]
        manifest_path = (
            custody
            / pack.name
            / "arm_readiness.t0.inputs"
            / "launch-manifest.json"
        )
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(
            render_json(
                {
                    "schema_version": readiness.LAUNCH_MANIFEST_SCHEMA,
                    "boot_session_id": TEST_BOOT_SESSION_ID,
                    "window_plan_root": str(window_root),
                    "prewindow_command": ["/bin/true"],
                    "launch_command": exec_argv,
                }
            )
        )
        args = argparse.Namespace(
            pack_root=pack,
            arm_receipt=arm_path,
            arm_readiness_custody_root=custody,
            launch_manifest=manifest_path,
            lifecycle_event=None,
        )
        return args, exec_argv

    def launch_artifact_references(
        self, manifest_path: Path
    ) -> dict[str, dict[str, str]]:
        manifest = readiness.parse_json_bytes(
            manifest_path.read_bytes(), require_canonical=True
        )
        window_root = Path(str(manifest["window_plan_root"]))

        def reference(path: Path) -> dict[str, str]:
            return {
                "path": str(path.resolve()),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }

        return {
            "launch_manifest": reference(manifest_path),
            "window_environment": reference(window_root / "window.env"),
            "window_chain": reference(window_root / "window-chain.zsh"),
        }

    def test_fixture_repos_disable_git_maintenance_at_creation(self) -> None:
        # EVIDENCE-AUTHOR-GIT-TEARDOWN-01 regression: fixture repos must never
        # spawn detached maintenance that can race TemporaryDirectory cleanup.
        temporary, repository, _pack, _custody, _arm = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        for key, want in (("gc.auto", "0"), ("maintenance.auto", "false")):
            got = subprocess.run(
                ["git", "config", "--get", key],
                cwd=repository,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(got, want, key)

    def test_freeze_receipts_can_never_carry_go(self) -> None:
        receipt = sample_freeze()
        receipt["arm_disposition"] = "GO"
        with self.assertRaises(ArmReadinessError):
            validate_freeze_receipt(receipt)

    def test_freeze_generation_is_byte_idempotent_and_sidecar_exact(self) -> None:
        temporary, repo, pack, _custody, _arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        predecessor = predecessor_pack_root(repo, PACK_NAME)
        first = generate_freeze_receipt(pack, predecessor_pack_root=predecessor)
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
        second = generate_freeze_receipt(pack, predecessor_pack_root=predecessor)
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

    def test_duplicate_parsed_arm_numbers_refuse_even_with_distinct_spellings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "receipts"
            first = sample_arm(temporary)
            first["receipt_id"] = "arm-00001"
            first_path = self.write_namespace_receipt(
                root, "arm-00001.json", first
            )
            first_raw = first_path.read_bytes()
            second = sample_arm(temporary)
            second["receipt_id"] = "arm-0001"
            second["supersedes"] = {
                "receipt_id": first["receipt_id"],
                "receipt_path": "arm_readiness.receipts/arm-00001.json",
                "receipt_sha256": hashlib.sha256(first_raw).hexdigest(),
                "pack_id": first["pack"]["pack_id"],
                "pack_sha256": first["pack"]["pack_sha256"],
            }
            self.write_namespace_receipt(root, "arm-0001.json", second)
            with self.assertRaisesRegex(
                ArmReadinessError, "duplicate/nonpositive receipt number"
            ):
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
        args, exec_argv = self.install_launch_manifest(
            Path(temporary.name), pack, custody, arm_path
        )
        barrier = threading.Barrier(8)
        outcomes: list[str] = []
        lock = threading.Lock()

        def consume() -> None:
            barrier.wait()
            try:
                launch_window.launch(args)
            except ArmReadinessError as exc:
                outcome = exc.reason_code
            except readiness.LaunchLineageError as exc:
                outcome = exc.reason_code
            with lock:
                outcomes.append(outcome)

        with mock.patch.object(
            launch_window, "_install_handoff"
        ), mock.patch.object(
            readiness,
            "_attested_launch_artifact_references",
            return_value=self.launch_artifact_references(args.launch_manifest),
        ), mock.patch.object(
            launch_window,
            "verify_consumed_launch",
            return_value={"exec_argv": exec_argv},
        ), mock.patch.object(launch_window.os, "execve") as execve:
            threads = [threading.Thread(target=consume) for _ in range(8)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=10)
        self.assertEqual(execve.call_count, 1)
        self.assertEqual(outcomes.count("launch_consumption_invalid"), 1, outcomes)
        self.assertEqual(outcomes.count("readiness_record_consumed"), 7, outcomes)
        self.assertNotIn("readiness_lock_unavailable", outcomes)
        consumption_path = (
            custody
            / pack.name
            / "arm_readiness.consumptions"
            / f"{arm_path.stem}.consumed.json"
        )
        consumption = readiness.validate_consumption_receipt(
            readiness.parse_json_bytes(
                consumption_path.read_bytes(), require_canonical=True
            )
        )
        self.assertEqual(
            consumption["schema_version"], readiness.CONSUMPTION_RECEIPT_SCHEMA
        )
        with mock.patch.object(
            launch_window, "_install_handoff"
        ), mock.patch.object(
            readiness,
            "_attested_launch_artifact_references",
            return_value=self.launch_artifact_references(args.launch_manifest),
        ):
            with self.assertRaisesRegex(
                ArmReadinessError, "already consumed"
            ) as replay:
                launch_window.launch(args)
        self.assertEqual(replay.exception.reason_code, "readiness_record_consumed")
        self.assertNotEqual(replay.exception.reason_code, "readiness_lock_unavailable")

    def test_boot_session_change_voids_verification_and_consumption(self) -> None:
        from tests.test_arm_readiness_dry_run import install_passing_freeze
        from tests.test_arm_readiness_integration import (
            clear_initial_arm,
            install_passing_evidence,
            synthetic_identity_verifier,
        )

        temporary, repo, pack, custody, _arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        clear_initial_arm(custody, pack.name)
        install_passing_freeze(repo, pack)
        dry = generate_dry_run_receipt(
            pack,
            custody,
            "boot-rehearsal",
            Path(temporary.name) / "boot-synthetic",
        )
        self.assertEqual(dry["status"], "PASS", dry)
        install_passing_evidence(pack, custody)
        context = sample_arm(Path(temporary.name) / "context")["arm_context"]
        with mock.patch.object(
            readiness,
            "verify_frozen_projection",
            side_effect=synthetic_identity_verifier,
        ):
            arm_result = generate_arm_receipt(pack, context, custody)
        self.assertEqual(arm_result["status"], "PASS", arm_result)
        arm_path = Path(arm_result["receipt_path"])
        args, _exec_argv = self.install_launch_manifest(
            Path(temporary.name), pack, custody, arm_path
        )

        same_boot = verify_arm_receipt(pack, arm_path)
        self.assertEqual(same_boot["status"], "PASS")
        changed_boot = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
        with mock.patch.object(
            readiness, "_current_boot_session_id", return_value=changed_boot
        ):
            for operation in (
                lambda: verify_arm_receipt(pack, arm_path),
                lambda: launch_window.launch(args),
            ):
                with self.subTest(operation=operation):
                    with self.assertRaises(ArmReadinessError) as caught:
                        operation()
                    self.assertEqual(
                        caught.exception.reason_code, "readiness_record_expired"
                    )
                    self.assertIn("prior boot session", str(caught.exception))

    def test_consume_collision_never_emits_defensive_lock_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pack = root / "pack"
            pack.mkdir()
            custody = root / "custody"
            arm_path = (
                custody
                / pack.name
                / "arm_readiness.receipts"
                / "arm-0001.json"
            )
            arm_path.parent.mkdir(parents=True)
            arm_path.write_bytes(b"placeholder\n")
            receipt = sample_arm(root / "context")
            args, exec_argv = self.install_launch_manifest(
                root, pack, custody, arm_path
            )
            manifest_raw = args.launch_manifest.read_bytes()
            manifest = readiness.parse_json_bytes(
                manifest_raw, require_canonical=True
            )
            window_root = Path(manifest["window_plan_root"])
            launch_inputs = {
                "pack_root": pack,
                "arm_receipt": arm_path,
                "authenticated_arm_receipt": receipt,
                "arm_receipt_sha256": "0" * 64,
                "window_custody_root": custody,
                "launch_manifest": args.launch_manifest,
                "authenticated_launch_manifest": manifest,
                "launch_manifest_sha256": hashlib.sha256(
                    manifest_raw
                ).hexdigest(),
                "window_plan_root": window_root,
                "window_environment_sha256": hashlib.sha256(
                    (window_root / "window.env").read_bytes()
                ).hexdigest(),
                "window_chain_sha256": hashlib.sha256(
                    (window_root / "window-chain.zsh").read_bytes()
                ).hexdigest(),
                "exec_argv": exec_argv,
            }
            with mock.patch.object(
                readiness,
                "_verify_arm_receipt",
                return_value={
                    "status": "PASS",
                    "arm_disposition": "GO",
                    "receipt_path": str(arm_path.resolve()),
                    "receipt_sha256": "0" * 64,
                    "pack_sha256": receipt["pack"]["pack_sha256"],
                },
            ), mock.patch.object(
                readiness,
                "_read_arm_with_sidecar",
                return_value=(receipt, b"placeholder\n", "0" * 64),
            ), mock.patch.object(
                readiness,
                "reviewed_main",
                return_value=receipt["reviewed_main"],
            ), mock.patch.object(
                readiness, "_root_policy_refusals", return_value=([], set())
            ), mock.patch.object(
                readiness,
                "_attested_launch_artifact_references",
                return_value=self.launch_artifact_references(
                    args.launch_manifest
                ),
            ), mock.patch.object(
                readiness,
                "_exclusive_write",
                side_effect=ArmReadinessError(
                    "readiness_output_collision", "synthetic O_EXCL loser"
                ),
            ), mock.patch.object(
                launch_window, "_install_handoff"
            ), mock.patch.object(
                launch_window,
                "_assemble_launch_inputs",
                return_value=launch_inputs,
            ):
                with self.assertRaises(ArmReadinessError) as caught:
                    launch_window.launch(args)
            self.assertEqual(
                caught.exception.reason_code, "readiness_record_consumed"
            )
            self.assertNotEqual(
                caught.exception.reason_code, "readiness_lock_unavailable"
            )

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
        args, _exec_argv = self.install_launch_manifest(
            Path(temporary.name), pack, custody, dry_path
        )
        with self.assertRaisesRegex(
            readiness.LaunchLineageError, "arm receipt is invalid"
        ) as caught:
            launch_window.launch(args)
        self.assertEqual(
            caught.exception.reason_code,
            "launch_consumption_invalid",
        )

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
            "--boot-session-id",
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
            "boot_session_id",
        }
        for function in (
            generate_freeze_receipt,
            generate_dry_run_receipt,
            generate_arm_receipt,
        ):
            with self.subTest(function=function.__name__):
                self.assertTrue(
                    forbidden.isdisjoint(inspect.signature(function).parameters)
                )
        self.assertNotIn("consume_launch_capability", readiness.__all__)
        with self.assertRaises(AttributeError):
            getattr(readiness, "consume_launch_capability")


SUCCESSOR_PACKS = {
    "ALPHA": "d117_floor_qwen25_1p5b_v2",
    "BETA": "d117_floor_qwen25_7b_v2",
    "GAMMA": "d117_contrast_qwen25_1p5b_vs_7b_v2",
}
SUCCESSOR_PROFILE_BY_PACK = {
    pack_name: profile for profile, pack_name in SUCCESSOR_PACKS.items()
}


class FreezeSuccessorChainTests(unittest.TestCase):
    """D-139: chain-monotonic freeze-0002 with an authenticated predecessor.

    The successor packs are pinned into the live profile map for the duration
    of each test so these regressions hold both before and after the D-138
    pack/profile map supersession lands.
    """

    def setUp(self) -> None:
        boot = mock.patch.object(
            readiness, "_current_boot_session_id", return_value=TEST_BOOT_SESSION_ID
        )
        boot.start()
        self.addCleanup(boot.stop)
        profiles = mock.patch.dict(
            readiness._PROFILE_BY_PACK, SUCCESSOR_PROFILE_BY_PACK
        )
        profiles.start()
        self.addCleanup(profiles.stop)

    def successor_fixture(
        self, profile: str = "ALPHA", **kwargs: object
    ) -> tuple[Path, Path, Path]:
        pack_name = SUCCESSOR_PACKS[profile]
        temporary, repo, pack, _custody, _arm_path = make_go_fixture(
            pack_name, profile, **kwargs
        )
        self.addCleanup(temporary.cleanup)
        return repo, pack, predecessor_pack_root(repo, pack_name)

    @staticmethod
    def freeze_namespace(pack: Path) -> Path:
        return pack / "arm_readiness.freeze.receipts"

    def assert_no_successor_bytes(self, pack: Path, tree_before: bytes) -> None:
        self.assertFalse(self.freeze_namespace(pack).exists())
        self.assertEqual((pack / "plan_tree.json").read_bytes(), tree_before)

    def mint(self, pack: Path, predecessor: Path | None) -> dict:
        return generate_freeze_receipt(pack, predecessor_pack_root=predecessor)

    def read_receipt(self, path: Path) -> dict:
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def run_freeze_cli(self, argv: list[str], expected_code: int | None) -> dict:
        buffer = io.BytesIO()
        stdout = mock.Mock(
            buffer=buffer,
            fileno=mock.Mock(side_effect=io.UnsupportedOperation("fileno")),
            isatty=mock.Mock(return_value=False),
        )
        with mock.patch.object(arm_readiness_cli.sys, "stdout", stdout):
            code = arm_readiness_cli.main(argv)
        if expected_code is not None:
            self.assertEqual(code, expected_code)
        return json.loads(buffer.getvalue().decode("utf-8"))

    # R-1 / R-7 -------------------------------------------------------------
    def test_pass_predecessor_mints_a_singleton_freeze_0002(self) -> None:
        repo, pack, predecessor = self.successor_fixture()
        result = self.mint(pack, predecessor)
        self.assertTrue(result["mutated"])
        namespace = self.freeze_namespace(pack)
        self.assertEqual(
            sorted(path.name for path in namespace.iterdir()),
            ["freeze-0002.json", "freeze-0002.json.sha256"],
        )
        receipt = self.read_receipt(result["receipt_path"])
        self.assertEqual(receipt["schema_version"], readiness.FREEZE_RECEIPT_V2_SCHEMA)
        self.assertEqual(receipt["receipt_id"], "freeze-0002")
        self.assertNotIn("supersedes", receipt)
        self.assertEqual(
            receipt["predecessor"]["freeze_receipt"]["receipt_id"], "freeze-0001"
        )
        # R-7: a singleton freeze-0002 under a new root needs no local 0001.
        scanned = scan_receipt_namespace(namespace, "freeze")
        self.assertEqual([item["number"] for item in scanned], [2])
        pinned = json.loads((pack / "plan_tree.json").read_text(encoding="utf-8"))[
            "arm_attachments"
        ]["arm_readiness"]["freeze_receipt"]
        self.assertEqual(
            pinned,
            {
                "path": "arm_readiness.freeze.receipts/freeze-0002.json",
                "sha256": result["receipt_sha256"],
            },
        )
        verified = verify_receipt(pack, Path(result["receipt_path"]))
        self.assertEqual(verified["receipt_sha256"], result["receipt_sha256"])

    # R-2 -------------------------------------------------------------------
    def test_serialized_predecessor_equals_independently_derived_bindings(
        self,
    ) -> None:
        repo, pack, predecessor = self.successor_fixture()
        result = self.mint(pack, predecessor)
        recorded = self.read_receipt(result["receipt_path"])["predecessor"]

        receipt_path = predecessor / "arm_readiness.freeze.receipts/freeze-0001.json"
        receipt_raw = receipt_path.read_bytes()
        receipt = json.loads(receipt_raw.decode("utf-8"))
        projection_relative = "identity_pin_projection.receipts/projection-0001.json"
        projection_raw = (predecessor / projection_relative).read_bytes()
        plan_raw = (predecessor / "calibration_plan.json").read_bytes()
        expected = {
            "pack_id": predecessor.name,
            "pack_path": f"configs/campaigns/{predecessor.name}",
            "pack_digest_algorithm": readiness.PACK_DIGEST_ALGORITHM,
            "pack_sha256": readiness.committed_pack_tree_sha256(predecessor),
            "plan_id": receipt["pack_identity"]["plan_id"],
            "plan_sha256": hashlib.sha256(plan_raw).hexdigest(),
            "freeze_receipt": {
                "receipt_id": "freeze-0001",
                "path": "arm_readiness.freeze.receipts/freeze-0001.json",
                "sha256": hashlib.sha256(receipt_raw).hexdigest(),
            },
            "identity_receipt": {
                "receipt_id": json.loads(projection_raw.decode("utf-8"))["receipt_id"],
                "path": projection_relative,
                "sha256": hashlib.sha256(projection_raw).hexdigest(),
            },
            "evidence_set_sha256": hashlib.sha256(
                readiness.FREEZE_PREDECESSOR_EVIDENCE_SET_DOMAIN
                + render_json(receipt["evidence"])
            ).hexdigest(),
        }
        self.assertEqual(recorded, expected)

    # R-3 / I-4 -------------------------------------------------------------
    def test_absent_predecessor_input_or_bytes_refuse_before_any_write(self) -> None:
        repo, pack, predecessor = self.successor_fixture()
        tree_before = (pack / "plan_tree.json").read_bytes()
        with self.assertRaises(ArmReadinessError) as caught:
            self.mint(pack, None)
        self.assertEqual(
            caught.exception.reason_code, "readiness_successor_chain_invalid"
        )
        self.assert_no_successor_bytes(pack, tree_before)

        cases = {
            "missing directory": lambda: shutil.rmtree(predecessor),
            "missing receipt": lambda: (
                predecessor / "arm_readiness.freeze.receipts/freeze-0001.json"
            ).unlink(),
            "missing sidecar": lambda: (
                predecessor / "arm_readiness.freeze.receipts/freeze-0001.json.sha256"
            ).unlink(),
            "missing identity receipt": lambda: (
                predecessor / "identity_pin_projection.receipts/projection-0001.json"
            ).unlink(),
        }
        for name, damage in cases.items():
            with self.subTest(case=name):
                repo, pack, predecessor = self.successor_fixture()
                tree_before = (pack / "plan_tree.json").read_bytes()
                damage()
                with self.assertRaises(ArmReadinessError) as caught:
                    self.mint(pack, predecessor)
                self.assertEqual(
                    caught.exception.reason_code, "readiness_successor_chain_invalid"
                )
                self.assert_no_successor_bytes(pack, tree_before)

    def test_uncommitted_predecessor_receipt_refuses(self) -> None:
        repo, pack, predecessor = self.successor_fixture()
        tree_before = (pack / "plan_tree.json").read_bytes()
        extra = predecessor / "arm_readiness.freeze.receipts/freeze-0003.json"
        extra.write_bytes(b"{}\n")
        with self.assertRaises(ArmReadinessError) as caught:
            self.mint(pack, predecessor)
        self.assertEqual(
            caught.exception.reason_code, "readiness_successor_chain_invalid"
        )
        self.assert_no_successor_bytes(pack, tree_before)

    # R-4 -------------------------------------------------------------------
    def test_refuse_status_predecessor_refuses_before_any_write(self) -> None:
        """Named regression killed by the R-13 mutant."""

        repo, pack, predecessor = self.successor_fixture(
            predecessor_status="REFUSE"
        )
        tree_before = (pack / "plan_tree.json").read_bytes()
        with self.assertRaises(ArmReadinessError) as caught:
            self.mint(pack, predecessor)
        self.assertEqual(
            caught.exception.reason_code, "readiness_successor_chain_invalid"
        )
        self.assertIn("did not record PASS", str(caught.exception))
        # An invalid ancestry never mints a REFUSE receipt of its own.
        self.assert_no_successor_bytes(pack, tree_before)

    def test_refuse_status_identity_receipt_refuses_before_any_write(self) -> None:
        repo, pack, predecessor = self.successor_fixture()
        tree_before = (pack / "plan_tree.json").read_bytes()
        # Re-author the predecessor with a REFUSE identity projection receipt.
        shutil.rmtree(predecessor)
        write_predecessor_pack(
            repo,
            predecessor.name,
            "ALPHA",
            identity_status="REFUSE",
        )
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "refusing identity projection")
        with self.assertRaises(ArmReadinessError) as caught:
            self.mint(pack, predecessor)
        self.assertEqual(
            caught.exception.reason_code, "readiness_successor_chain_invalid"
        )
        self.assert_no_successor_bytes(pack, tree_before)

    # R-5 -------------------------------------------------------------------
    def test_tampered_predecessor_bytes_refuse_at_mint(self) -> None:
        targets = (
            "calibration_plan.json",
            "arm_readiness.freeze.receipts/freeze-0001.json",
            "arm_readiness.freeze.receipts/freeze-0001.json.sha256",
            "identity_pin_projection.receipts/projection-0001.json",
            "identity_pin_projection.receipts/projection-0001.sha256",
            "plan_tree.json",
        )
        for relative in targets:
            with self.subTest(target=relative):
                repo, pack, predecessor = self.successor_fixture()
                tree_before = (pack / "plan_tree.json").read_bytes()
                target = predecessor / relative
                target.write_bytes(target.read_bytes() + b" ")
                with self.assertRaises(ArmReadinessError) as caught:
                    self.mint(pack, predecessor)
                self.assertEqual(
                    caught.exception.reason_code, "readiness_successor_chain_invalid"
                )
                self.assert_no_successor_bytes(pack, tree_before)

    def test_tampered_predecessor_bytes_refuse_at_every_later_load(self) -> None:
        repo, pack, predecessor = self.successor_fixture()
        result = self.mint(pack, predecessor)
        receipt_path = Path(result["receipt_path"])
        verify_receipt(pack, receipt_path)
        plan = predecessor / "calibration_plan.json"
        plan.write_bytes(plan.read_bytes() + b" ")
        with self.assertRaises(ArmReadinessError) as caught:
            verify_receipt(pack, receipt_path)
        self.assertEqual(
            caught.exception.reason_code, "readiness_successor_chain_invalid"
        )
        tree, _raw = readiness._plan_tree(pack)
        registry, _registry_raw, reference = readiness._registry_reference(pack)
        with self.assertRaises(ArmReadinessError) as caught:
            readiness._load_freeze_reference(
                pack, tree, reference, registry, require_pass=False
            )
        self.assertEqual(
            caught.exception.reason_code, "readiness_successor_chain_invalid"
        )

    def test_every_recorded_predecessor_binding_is_load_bearing(self) -> None:
        repo, pack, predecessor = self.successor_fixture()
        result = self.mint(pack, predecessor)
        recorded = self.read_receipt(result["receipt_path"])["predecessor"]
        readiness._authenticate_freeze_predecessor(
            pack,
            recorded,
            successor_receipt_id="freeze-0002",
            successor_profile="ALPHA",
        )
        mutations = {
            "pack_sha256": {"pack_sha256": "0" * 64},
            "plan_sha256": {"plan_sha256": "0" * 64},
            "plan_id": {"plan_id": "plan-forged"},
            "evidence_set_sha256": {"evidence_set_sha256": "0" * 64},
            "freeze_receipt.sha256": {
                "freeze_receipt": {
                    **recorded["freeze_receipt"],
                    "sha256": "0" * 64,
                }
            },
            "freeze_receipt.receipt_id": {
                "freeze_receipt": {
                    "receipt_id": "freeze-0002",
                    "path": "arm_readiness.freeze.receipts/freeze-0002.json",
                    "sha256": recorded["freeze_receipt"]["sha256"],
                }
            },
            "identity_receipt.sha256": {
                "identity_receipt": {
                    **recorded["identity_receipt"],
                    "sha256": "0" * 64,
                }
            },
            "identity_receipt.receipt_id": {
                "identity_receipt": {
                    **recorded["identity_receipt"],
                    "receipt_id": "synthetic/forged",
                }
            },
        }
        for name, mutation in mutations.items():
            with self.subTest(binding=name):
                mutated = copy.deepcopy(recorded)
                mutated.update(copy.deepcopy(mutation))
                with self.assertRaises(ArmReadinessError) as caught:
                    readiness._authenticate_freeze_predecessor(
                        pack,
                        mutated,
                        successor_receipt_id="freeze-0002",
                        successor_profile="ALPHA",
                    )
                self.assertEqual(
                    caught.exception.reason_code, "readiness_successor_chain_invalid"
                )

    # R-6 -------------------------------------------------------------------
    def test_self_wrong_role_and_ordinal_violations_refuse(self) -> None:
        repo, pack, predecessor = self.successor_fixture()
        tree_before = (pack / "plan_tree.json").read_bytes()
        with self.assertRaises(ArmReadinessError) as caught:
            self.mint(pack, pack)
        self.assertEqual(
            caught.exception.reason_code, "readiness_successor_chain_invalid"
        )
        self.assert_no_successor_bytes(pack, tree_before)

        foreign = write_predecessor_pack(
            repo, "d117_floor_qwen25_7b_v1", "BETA"
        )
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "beta predecessor")
        with self.assertRaises(ArmReadinessError) as caught:
            self.mint(pack, foreign)
        self.assertEqual(
            caught.exception.reason_code, "readiness_successor_chain_invalid"
        )
        self.assertIn("different plan profile", str(caught.exception))
        self.assert_no_successor_bytes(pack, tree_before)

        result = self.mint(pack, predecessor)
        recorded = self.read_receipt(result["receipt_path"])["predecessor"]
        for successor_receipt_id in ("freeze-0001", "freeze-0003"):
            with self.subTest(successor=successor_receipt_id):
                with self.assertRaises(ArmReadinessError) as caught:
                    readiness._authenticate_freeze_predecessor(
                        pack,
                        recorded,
                        successor_receipt_id=successor_receipt_id,
                        successor_profile="ALPHA",
                    )
                self.assertEqual(
                    caught.exception.reason_code, "readiness_successor_chain_invalid"
                )

    def test_successor_namespace_refuses_an_ordinal_that_skips_its_predecessor(
        self,
    ) -> None:
        repo, pack, predecessor = self.successor_fixture()
        result = self.mint(pack, predecessor)
        namespace = self.freeze_namespace(pack)
        receipt = self.read_receipt(result["receipt_path"])
        receipt["receipt_id"] = "freeze-0003"
        raw = render_json(receipt)
        (namespace / "freeze-0002.json").unlink()
        (namespace / "freeze-0002.json.sha256").unlink()
        (namespace / "freeze-0003.json").write_bytes(raw)
        (namespace / "freeze-0003.json.sha256").write_bytes(
            gnu_sidecar(hashlib.sha256(raw).hexdigest(), "freeze-0003.json")
        )
        with self.assertRaises(ArmReadinessError):
            scan_receipt_namespace(namespace, "freeze")

    # R-8 -------------------------------------------------------------------
    def test_repeat_mint_is_byte_idempotent_and_reauthenticates(self) -> None:
        repo, pack, predecessor = self.successor_fixture()
        first = self.mint(pack, predecessor)
        path = Path(first["receipt_path"])
        raw_before = path.read_bytes()
        tree_before = (pack / "plan_tree.json").read_bytes()
        second = self.mint(pack, predecessor)
        self.assertFalse(second["mutated"])
        self.assertEqual(second["receipt_sha256"], first["receipt_sha256"])
        self.assertEqual(path.read_bytes(), raw_before)
        self.assertEqual((pack / "plan_tree.json").read_bytes(), tree_before)
        # Even the idempotent replay must name the ancestry it re-authenticates.
        with self.assertRaises(ArmReadinessError) as caught:
            generate_freeze_receipt(pack)
        self.assertEqual(
            caught.exception.reason_code, "readiness_successor_chain_invalid"
        )

        plan = predecessor / "calibration_plan.json"
        plan.write_bytes(plan.read_bytes() + b" ")
        with self.assertRaises(ArmReadinessError) as caught:
            self.mint(pack, predecessor)
        self.assertEqual(
            caught.exception.reason_code, "readiness_successor_chain_invalid"
        )
        self.assertEqual(path.read_bytes(), raw_before)

    # R-8 / delta-8 F1 ------------------------------------------------------
    def test_replay_refuses_tampered_current_successor_bytes(self) -> None:
        """Replay authenticates the CURRENT receipt, not just its ancestry.

        Before this was fixed, a byte appended to the successor's own identity
        projection still replayed as ``mutated: false`` with the recorded
        status, because only the predecessor chain was re-authenticated.
        """

        repo, pack, predecessor = self.successor_fixture()
        first = self.mint(pack, predecessor)
        path = Path(first["receipt_path"])
        for label, target in (
            (
                "identity projection evidence",
                pack / "identity_pin_projection.receipts/projection-0001.json",
            ),
            ("freeze receipt", path),
            ("freeze receipt sidecar", path.with_name(f"{path.name}.sha256")),
        ):
            with self.subTest(tampered=label):
                original = target.read_bytes()
                target.write_bytes(original + b"\n")
                try:
                    with self.assertRaises(ArmReadinessError):
                        self.mint(pack, predecessor)
                finally:
                    target.write_bytes(original)
                restored = self.mint(pack, predecessor)
                self.assertFalse(restored["mutated"])
                self.assertEqual(
                    restored["receipt_sha256"], first["receipt_sha256"]
                )
                self.assertEqual(restored["status"], first["status"])

    # delta-10 F1 -----------------------------------------------------------
    @staticmethod
    def identity_row(receipt: dict) -> dict:
        return next(
            row
            for row in receipt["rows"]
            if row["row_id"] == "desk.identity_pin_projection"
        )

    def test_refuse_identity_projection_replays_as_its_recorded_refuse(self) -> None:
        """Replay returns the recorded conclusion; it does not re-adjudicate it.

        A schema-valid REFUSE identity projection lawfully mints a REFUSE
        freeze-0002.  Replaying that receipt authenticates every byte it binds
        and must then return the REFUSE it recorded.  Before this was fixed the
        loader compared the recorded refusals against a freshly derived list in
        ROW-DEFINITION order while every mint writes them in canonical
        (code, row_id, evidence_id) order, so the identity refusal -- whose code
        sorts away from its row-definition slot -- made a perfectly authentic
        receipt raise ``readiness_dependency_refused`` on replay.
        """

        repo, pack, predecessor = self.successor_fixture(identity_status="REFUSE")
        first = self.mint(pack, predecessor)
        self.assertTrue(first["mutated"])
        self.assertEqual(first["status"], "REFUSE")
        recorded = self.read_receipt(first["receipt_path"])
        self.assertEqual(self.identity_row(recorded)["verdict"], "REFUSE")
        self.assertIn("readiness_identity_environment_dirty", first["reason_codes"])

        replayed = self.mint(pack, predecessor)
        self.assertFalse(replayed["mutated"])
        self.assertEqual(replayed["status"], "REFUSE")
        self.assertEqual(replayed["receipt_sha256"], first["receipt_sha256"])
        self.assertEqual(replayed["reason_codes"], first["reason_codes"])
        # The bytes are untouched by a replay that returns a recorded REFUSE.
        self.assertEqual(self.read_receipt(first["receipt_path"]), recorded)
        # The loader itself replays it, which is what every consumer path uses.
        tree, _raw = readiness._plan_tree(pack)
        registry, _registry_raw, reference = readiness._registry_reference(pack)
        loaded, _loaded_reference = readiness._load_freeze_reference(
            pack, tree, reference, registry, require_pass=False
        )
        self.assertEqual(loaded["status"], "REFUSE")
        # ``require_pass`` remains the ONE gate that decides whether a caller
        # may USE a REFUSE -- replay tolerance never leaks into enforcement.
        with self.assertRaises(ArmReadinessError) as caught:
            readiness._load_freeze_reference(pack, tree, reference, registry)
        self.assertEqual(caught.exception.reason_code, "readiness_dependency_refused")

    def test_replay_refuses_a_tampered_refuse_identity_projection(self) -> None:
        """A recorded REFUSE replays; a tampered dependency still refuses.

        Replay tolerance is about the recorded CONCLUSION, never about the
        bytes: one appended byte on the identity-projection receipt the REFUSE
        was derived from must refuse, and the untouched fixture must replay
        again afterwards.
        """

        repo, pack, predecessor = self.successor_fixture(identity_status="REFUSE")
        first = self.mint(pack, predecessor)
        target = pack / "identity_pin_projection.receipts/projection-0001.json"
        original = target.read_bytes()
        target.write_bytes(original + b"\n")
        try:
            with self.assertRaises(ArmReadinessError) as caught:
                self.mint(pack, predecessor)
            self.assertEqual(
                caught.exception.reason_code, "readiness_dependency_refused"
            )
        finally:
            target.write_bytes(original)
        restored = self.mint(pack, predecessor)
        self.assertFalse(restored["mutated"])
        self.assertEqual(restored["receipt_sha256"], first["receipt_sha256"])
        self.assertEqual(restored["status"], first["status"])

    def test_identity_verdict_replays_as_recorded_pass_or_refuse(self) -> None:
        """PASS replays PASS and REFUSE replays REFUSE, row for row.

        No fixture in this suite can mint a whole-receipt PASS -- the freeze
        phase also requires desk evidence these packs do not carry -- so the
        PASS side of "the recorded conclusion is what replays" is pinned at the
        row the defect turned on.
        """

        conclusions = {}
        for identity_status in ("PASS", "REFUSE"):
            with self.subTest(identity_status=identity_status):
                _repo, pack, predecessor = self.successor_fixture(
                    identity_status=identity_status
                )
                minted = self.mint(pack, predecessor)
                recorded = self.read_receipt(minted["receipt_path"])
                self.assertEqual(
                    self.identity_row(recorded)["verdict"], identity_status
                )
                replayed = self.mint(pack, predecessor)
                self.assertFalse(replayed["mutated"])
                self.assertEqual(replayed["status"], minted["status"])
                self.assertEqual(replayed["reason_codes"], minted["reason_codes"])
                self.assertEqual(
                    self.read_receipt(replayed["receipt_path"]), recorded
                )
                conclusions[identity_status] = minted["reason_codes"]
        # The two fixtures differ by exactly the identity refusal, so the
        # replayed conclusions are genuinely distinct records.
        self.assertEqual(
            set(conclusions["REFUSE"]) - set(conclusions["PASS"]),
            {"readiness_identity_environment_dirty"},
        )
        self.assertEqual(set(conclusions["PASS"]) - set(conclusions["REFUSE"]), set())

    # R-9 -------------------------------------------------------------------
    def test_committed_v1_freeze_receipts_remain_authentic_historical_records(
        self,
    ) -> None:
        packs = (
            "d117_floor_qwen25_1p5b_v1",
            "d117_floor_qwen25_7b_v1",
            "d117_contrast_qwen25_1p5b_vs_7b_v1",
        )
        for pack_name in packs:
            with self.subTest(pack=pack_name):
                pack = ROOT / "configs/campaigns" / pack_name
                relative = (
                    f"configs/campaigns/{pack_name}"
                    "/arm_readiness.freeze.receipts/freeze-0001.json"
                )
                path = ROOT / relative
                raw = path.read_bytes()
                self.assertEqual(readiness._git_blob_at_head(ROOT, relative), raw)
                receipt = validate_freeze_receipt(json.loads(raw.decode("utf-8")))
                self.assertEqual(
                    receipt["schema_version"], readiness.FREEZE_RECEIPT_SCHEMA
                )
                self.assertEqual(receipt["status"], "PASS")
                self.assertIsNone(receipt["supersedes"])
                digest = hashlib.sha256(raw).hexdigest()
                pinned = json.loads(
                    (pack / "plan_tree.json").read_text(encoding="utf-8")
                )["arm_attachments"]["arm_readiness"]["freeze_receipt"]
                self.assertEqual(pinned["sha256"], digest)
                verified = verify_receipt(pack, path)
                self.assertEqual(verified["status"], "PASS")
                self.assertEqual(verified["receipt_sha256"], digest)

    # R-10 ------------------------------------------------------------------
    def test_v2_presence_never_supersedes_a_v1_receipt(self) -> None:
        repo, pack, predecessor = self.successor_fixture()
        self.mint(pack, predecessor)
        historical = (
            predecessor / "arm_readiness.freeze.receipts/freeze-0001.json"
        )
        verified = verify_receipt(predecessor, historical)
        self.assertEqual(verified["status"], "PASS")
        scanned = scan_receipt_namespace(
            predecessor / "arm_readiness.freeze.receipts", "freeze"
        )
        self.assertEqual([item["number"] for item in scanned], [1])
        self.assertIsNone(scanned[0]["receipt"]["supersedes"])

        # v1 and v2 may share one namespace without supersession semantics.
        with tempfile.TemporaryDirectory() as temporary:
            namespace = Path(temporary) / "arm_readiness.freeze.receipts"
            namespace.mkdir(parents=True)
            for name, receipt in (
                ("freeze-0001.json", sample_freeze()),
                ("freeze-0002.json", sample_freeze_v2()),
            ):
                receipt["receipt_id"] = name.removesuffix(".json")
                raw = render_json(receipt)
                (namespace / name).write_bytes(raw)
                (namespace / f"{name}.sha256").write_bytes(
                    gnu_sidecar(hashlib.sha256(raw).hexdigest(), name)
                )
            mixed = scan_receipt_namespace(namespace, "freeze")
            self.assertEqual([item["number"] for item in mixed], [1, 2])

    # R-12 ------------------------------------------------------------------
    def test_attachment_refuses_multiple_committed_freeze_candidates(self) -> None:
        repo, pack, predecessor = self.successor_fixture()
        namespace = predecessor / "arm_readiness.freeze.receipts"
        attachment = readiness.plan_arm_readiness_attachment(
            predecessor, "ALPHA", repo
        )
        self.assertEqual(
            attachment["freeze_receipt"]["path"],
            "arm_readiness.freeze.receipts/freeze-0001.json",
        )
        receipt = self.read_receipt(namespace / "freeze-0001.json")
        receipt["receipt_id"] = "freeze-0002"
        raw = render_json(receipt)
        (namespace / "freeze-0002.json").write_bytes(raw)
        (namespace / "freeze-0002.json.sha256").write_bytes(
            gnu_sidecar(hashlib.sha256(raw).hexdigest(), "freeze-0002.json")
        )
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "second committed freeze receipt")
        with self.assertRaises(ArmReadinessError) as caught:
            readiness.plan_arm_readiness_attachment(predecessor, "ALPHA", repo)
        self.assertEqual(
            caught.exception.reason_code, "readiness_freeze_receipt_mismatch"
        )
        self.assertIn("no unique selection", str(caught.exception))

    def test_attachment_refuses_a_committed_receipt_the_plan_does_not_pin(
        self,
    ) -> None:
        repo, pack, predecessor = self.successor_fixture()
        tree_path = predecessor / "plan_tree.json"
        tree = json.loads(tree_path.read_text(encoding="utf-8"))
        tree["arm_attachments"]["arm_readiness"]["freeze_receipt"]["sha256"] = (
            "0" * 64
        )
        raw = render_json(tree)
        tree_path.write_bytes(raw)
        (predecessor / "plan_tree.sha256").write_bytes(
            gnu_sidecar(hashlib.sha256(raw).hexdigest(), "plan_tree.json")
        )
        with self.assertRaises(ArmReadinessError) as caught:
            readiness.plan_arm_readiness_attachment(predecessor, "ALPHA", repo)
        self.assertEqual(
            caught.exception.reason_code, "readiness_freeze_receipt_mismatch"
        )

    # R-13 ------------------------------------------------------------------
    def test_bypassed_predecessor_authentication_survives_only_as_a_mutant(
        self,
    ) -> None:
        """Kill evidence for test_refuse_status_predecessor_refuses_before_any_write.

        With the shared authenticator neutered, the REFUSE-status ancestry mints
        a successor receipt.  That is exactly the failure the named regression
        catches, so the regression is load-bearing rather than incidental.
        """

        repo, pack, predecessor = self.successor_fixture(
            predecessor_status="REFUSE"
        )
        with mock.patch.object(
            readiness, "_authenticate_freeze_predecessor", return_value=None
        ) as bypassed:
            result = self.mint(pack, predecessor)
        self.assertTrue(bypassed.called)
        self.assertTrue(result["mutated"])
        self.assertTrue(
            (pack / "arm_readiness.freeze.receipts/freeze-0002.json").exists()
        )

    # R-14 ------------------------------------------------------------------
    def test_three_profile_family_advances_in_lockstep(self) -> None:
        for profile in ("ALPHA", "BETA", "GAMMA"):
            with self.subTest(profile=profile):
                repo, pack, predecessor = self.successor_fixture(profile)
                result = self.mint(pack, predecessor)
                receipt = self.read_receipt(result["receipt_path"])
                self.assertEqual(receipt["receipt_id"], "freeze-0002")
                self.assertEqual(
                    receipt["schema_version"], readiness.FREEZE_RECEIPT_V2_SCHEMA
                )
                self.assertEqual(receipt["row_registry"]["plan_profile"], profile)
                self.assertEqual(
                    receipt["predecessor"]["pack_id"],
                    predecessor_pack_name(SUCCESSOR_PACKS[profile]),
                )
                self.assertEqual(
                    receipt["predecessor"]["freeze_receipt"]["receipt_id"],
                    "freeze-0001",
                )

    # Lead hazard note ------------------------------------------------------
    def test_predecessor_authenticates_outside_the_live_map_and_resolver(
        self,
    ) -> None:
        """The v1 packs are historical records, not live vocabulary.

        Their committed ``plan.path`` uses the superseded repository-relative
        spelling that the shared R2 resolver refuses, and after D-138 they are
        absent from the live pack/profile map.  Chain authentication must key on
        the predecessor receipt's own recorded identity and profile.
        """

        pack_name = SUCCESSOR_PACKS["ALPHA"]
        predecessor_name = predecessor_pack_name(pack_name)
        with mock.patch.object(
            readiness, "_PROFILE_BY_PACK", {pack_name: "ALPHA"}
        ):
            temporary, repo, pack, _custody, _arm = make_go_fixture(
                pack_name,
                "ALPHA",
                predecessor_plan_path_spelling=(
                    f"configs/campaigns/{predecessor_name}/calibration_plan.json"
                ),
            )
            self.addCleanup(temporary.cleanup)
            predecessor = predecessor_pack_root(repo, pack_name)
            tree, _raw = readiness._plan_tree(predecessor)
            with self.assertRaises(ArmReadinessError):
                readiness.resolve_frozen_plan(predecessor, tree)
            with self.assertRaises(ArmReadinessError):
                readiness._plan_profile(predecessor)
            result = self.mint(pack, predecessor)
            receipt = self.read_receipt(result["receipt_path"])
            self.assertEqual(receipt["receipt_id"], "freeze-0002")
            self.assertEqual(receipt["predecessor"]["pack_id"], predecessor_name)
            verify_receipt(pack, Path(result["receipt_path"]))

    # CLI -------------------------------------------------------------------
    def test_cli_freeze_accepts_and_requires_a_predecessor_pack_root(self) -> None:
        repo, pack, predecessor = self.successor_fixture()
        # In-process: the successor pack lives in this test's patched profile
        # map, which a subprocess would not inherit until D-138 flips it.
        refusal = self.run_freeze_cli(["freeze", "--pack-root", str(pack)], 2)
        self.assertEqual(
            refusal["reason_codes"], ["readiness_successor_chain_invalid"]
        )
        self.assertFalse(self.freeze_namespace(pack).exists())

        result = self.run_freeze_cli(
            [
                "freeze",
                "--pack-root",
                str(pack),
                "--predecessor-pack-root",
                str(predecessor),
            ],
            None,
        )
        self.assertTrue(result["mutated"])
        self.assertTrue(
            (pack / "arm_readiness.freeze.receipts/freeze-0002.json").exists()
        )

    def test_first_generation_packs_reject_a_predecessor_input(self) -> None:
        # A generation-1 pack opens a chain.  The historical v1 identity keeps
        # its immutable map entry, so no patching is needed to resolve it.
        temporary, repo, pack, _custody, _arm = make_go_fixture(
            HISTORICAL_PACK_NAME, "ALPHA"
        )
        self.addCleanup(temporary.cleanup)
        with self.assertRaises(ArmReadinessError) as caught:
            generate_freeze_receipt(pack, predecessor_pack_root=pack)
        self.assertEqual(caught.exception.reason_code, "readiness_usage_invalid")
        self.assertFalse((pack / "arm_readiness.freeze.receipts").exists())


class FreezeReplayExpiryTests(unittest.TestCase):
    """B-12: every freeze replay authenticates evidence at live time."""

    def setUp(self) -> None:
        boot = mock.patch.object(
            readiness, "_current_boot_session_id", return_value=TEST_BOOT_SESSION_ID
        )
        boot.start()
        self.addCleanup(boot.stop)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.pack = Path(temporary.name) / "pack"
        evidence_directory = self.pack / "arm_readiness.evidence"
        evidence_directory.mkdir(parents=True)
        self.deadline = 1_000

        source_raw = render_json({"probe": "freeze-replay-expiry"})
        (self.pack / "source.json").write_bytes(source_raw)
        evidence = sample_evidence()
        evidence["valid_until_monotonic_ns"] = self.deadline
        evidence["facts"][0]["source_sha256"] = hashlib.sha256(
            source_raw
        ).hexdigest()
        evidence_raw = render_json(evidence)
        evidence_name = "evidence-1.json"
        evidence_path = evidence_directory / evidence_name
        evidence_path.write_bytes(evidence_raw)
        evidence_digest = hashlib.sha256(evidence_raw).hexdigest()
        evidence_path.with_name(f"{evidence_name}.sha256").write_bytes(
            gnu_sidecar(evidence_digest, evidence_name)
        )
        self.item = {
            "evidence_id": evidence["evidence_id"],
            "receipt_kind": evidence["kind"],
            "namespace": "PACK",
            "path": f"arm_readiness.evidence/{evidence_name}",
            "sha256": evidence_digest,
            "schema_version": evidence["schema_version"],
            "status": evidence["status"],
        }
        self.registry_reference = {"plan_profile": "ALPHA"}
        self.registry = {"schema_version": readiness.ROW_REGISTRY_SCHEMA}
        self.freeze_reference = {
            "path": "arm_readiness.freeze.receipts/freeze-0001.json",
            "sha256": "f" * 64,
        }
        self.tree = {
            "arm_attachments": {
                "arm_readiness": {"freeze_receipt": self.freeze_reference}
            }
        }
        self.freeze_receipt = {
            "schema_version": readiness.FREEZE_RECEIPT_SCHEMA,
            "receipt_id": "freeze-0001",
            "status": "PASS",
            "row_registry": self.registry_reference,
            "pack_identity": {"pack_id": "test"},
            "evidence": [self.item],
            "rows": [],
            "refusals": [],
        }

    def _load_freeze_reference(self) -> tuple[object, object]:
        scanned = {
            "path": Path("freeze-0001.json"),
            "sha256": self.freeze_reference["sha256"],
            "receipt": self.freeze_receipt,
        }
        with mock.patch.object(
            readiness, "scan_receipt_namespace", return_value=[scanned]
        ), mock.patch.object(
            readiness, "_valid_plan_attachment", return_value=None
        ), mock.patch.object(
            readiness,
            "_pack_identity",
            return_value=self.freeze_receipt["pack_identity"],
        ), mock.patch.object(
            readiness, "_profile_rows", return_value=[]
        ), mock.patch.object(
            readiness, "_validate_profile_rows", return_value=None
        ), mock.patch.object(
            readiness, "_load_frozen_identity_evidence", return_value=(None, None, [])
        ), mock.patch.object(
            readiness, "_evaluate_rows", return_value=([], [])
        ):
            return readiness._load_freeze_reference(
                self.pack,
                self.tree,
                self.registry_reference,
                self.registry,
            )

    def _freeze_evidence_for_arm(self) -> tuple[object, object]:
        with mock.patch.object(
            readiness, "_load_frozen_identity_evidence", return_value=(None, None, [])
        ):
            return readiness._freeze_evidence_for_arm(
                self.pack,
                self.tree,
                self.freeze_receipt,
                self.registry,
            )

    def test_both_freeze_replay_sites_refuse_expired_evidence(self) -> None:
        for label, replay in (
            ("load-freeze-reference", self._load_freeze_reference),
            ("freeze-evidence-for-arm", self._freeze_evidence_for_arm),
        ):
            with self.subTest(call_site=label), mock.patch.object(
                readiness.time,
                "monotonic_ns",
                return_value=self.deadline + 1,
            ):
                with self.assertRaises(ArmReadinessError) as caught:
                    replay()
                self.assertEqual(
                    caught.exception.reason_code, "readiness_record_expired"
                )

    def test_both_freeze_replay_sites_accept_unexpired_evidence(self) -> None:
        for label, replay in (
            ("load-freeze-reference", self._load_freeze_reference),
            ("freeze-evidence-for-arm", self._freeze_evidence_for_arm),
        ):
            with self.subTest(call_site=label), mock.patch.object(
                readiness.time,
                "monotonic_ns",
                return_value=self.deadline - 1,
            ):
                _items, receipts = replay()
                if label == "freeze-evidence-for-arm":
                    self.assertEqual(set(receipts), {self.item["evidence_id"]})

    def test_wrong_expected_head_still_refuses_before_expiry(self) -> None:
        with self.assertRaises(ArmReadinessError) as caught:
            readiness._authenticate_generic_evidence_item(
                self.item,
                self.pack,
                self.pack,
                expected_boot_session_id=TEST_BOOT_SESSION_ID,
                expected_head_commit="b" * 40,
                now_monotonic_ns=self.deadline - 1,
            )
        self.assertEqual(
            caught.exception.reason_code, "readiness_evidence_digest_mismatch"
        )
        self.assertIn("stale for pack or HEAD", str(caught.exception))

    def test_expiry_bypass_requires_the_explicit_named_opt_out(self) -> None:
        with mock.patch.object(
            readiness.time, "monotonic_ns", return_value=self.deadline + 1
        ):
            with self.assertRaises(ArmReadinessError) as caught:
                readiness._authenticate_generic_evidence_item(
                    self.item,
                    self.pack,
                    self.pack,
                    expected_boot_session_id=TEST_BOOT_SESSION_ID,
                )
            authenticated = readiness._authenticate_generic_evidence_item(
                self.item,
                self.pack,
                self.pack,
                expected_boot_session_id=TEST_BOOT_SESSION_ID,
                enforce_expiry=False,
            )
        self.assertEqual(caught.exception.reason_code, "readiness_record_expired")
        self.assertEqual(authenticated["evidence_id"], self.item["evidence_id"])


class PostSupersessionLayeringTests(unittest.TestCase):
    """The pack/profile map is IMMUTABLE HISTORY, not live vocabulary.

    A supersession never deletes a v1 identity from ``_PROFILE_BY_PACK``: the
    committed v1 receipts, evidence, and freeze chains were minted against that
    mapping and must stay authenticatable forever (see the ``_plan_profile``
    docstring, the R1 lane's ONE home for this design).  Successor identities
    install BY ROLE through the R1 registry's
    ``successor_policy.successor_pack_ids``, validated against the three
    D-139-approved uniform name shapes.

    Post-supersession refusal of a v1 pack is therefore LAYERED across the
    governed gates, not concentrated in a map lookup.  Measured against the
    committed campaign packs at this head: ALPHA/BETA v1 refuse freeze,
    dry-run, and arm at R2 frozen-plan resolution
    (``readiness_pack_unreadable``); GAMMA v1 refuses all three at freeze-
    receipt authentication (``readiness_freeze_receipt_mismatch``); all three
    refuse evidence authoring (``evidence_author_existing_stale``).  Those
    end-to-end paths are exercised by the R2 and freeze-authentication
    regressions in their own ONE homes; the units here pin the map design
    itself.
    """

    def setUp(self) -> None:
        patcher = mock.patch.object(
            readiness, "_current_boot_session_id", return_value=TEST_BOOT_SESSION_ID
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def historical_fixture(self, profile: str = "ALPHA") -> tuple[Path, Path, Path]:
        pack_name = predecessor_pack_name(SUCCESSOR_PACKS[profile])
        temporary, repo, pack, custody, _arm_path = make_go_fixture(
            pack_name, profile
        )
        self.addCleanup(temporary.cleanup)
        return repo, pack, custody

    def test_historical_map_is_immutable_and_successors_are_absent(self) -> None:
        self.assertEqual(
            readiness._PROFILE_BY_PACK,
            {
                "d117_floor_qwen25_1p5b_v1": "ALPHA",
                "d117_floor_qwen25_7b_v1": "BETA",
                "d117_contrast_qwen25_1p5b_vs_7b_v1": "GAMMA",
            },
        )
        self.assertEqual(
            evidence_module._PACKS_BY_PROFILE,
            {
                profile: pack_name
                for pack_name, profile in readiness._PROFILE_BY_PACK.items()
            },
        )
        # No successor ID is ever hardcoded here; only the approved shapes are
        # code constants, and installation is the registry's job.
        for pack_name in SUCCESSOR_PACKS.values():
            self.assertNotIn(pack_name, readiness._PROFILE_BY_PACK)
        for profile, pack_name in SUCCESSOR_PACKS.items():
            self.assertTrue(
                readiness._SUCCESSOR_PROFILE_PATTERNS[profile].fullmatch(pack_name)
            )
        for pack_name in readiness._PROFILE_BY_PACK:
            self.assertFalse(
                any(
                    pattern.fullmatch(pack_name)
                    for pattern in readiness._SUCCESSOR_PROFILE_PATTERNS.values()
                )
            )

    def test_row_registry_is_profile_keyed_and_needs_no_change(self) -> None:
        raw = (
            ROOT / "configs/arm_readiness/d117_row_registry_v1.json"
        ).read_text(encoding="utf-8")
        for pack_name in (
            *readiness._PROFILE_BY_PACK,
            *SUCCESSOR_PACKS.values(),
        ):
            self.assertNotIn(pack_name, raw)
        registry, _raw = readiness.load_registry(ROOT)
        self.assertEqual(
            [profile["profile_id"] for profile in registry["plan_profiles"]],
            ["ALPHA", "BETA", "GAMMA"],
        )

    def test_every_map_fed_entry_point_still_resolves_a_historical_pack(
        self,
    ) -> None:
        """The inverse regression: history must never stop resolving.

        Deleting a v1 identity from the map would orphan its own committed
        receipts, so every site the map feeds keeps resolving it.  Whatever
        prevents a v1 pack from arming is a LATER gate, never this lookup.
        """

        for profile in ("ALPHA", "BETA", "GAMMA"):
            with self.subTest(profile=profile):
                _repo, pack, _custody = self.historical_fixture(profile)
                self.assertEqual(readiness._plan_profile(pack), profile)
                _registry, _raw, reference = readiness._registry_reference(pack)
                self.assertEqual(reference["plan_profile"], profile)
                rows, kinds = evidence_module._required_generic_rows(
                    pack, readiness._plan_tree(pack)[0]
                )
                self.assertTrue(rows)
                self.assertTrue(kinds)

    def test_historical_predecessor_resolves_and_still_anchors_the_chain(
        self,
    ) -> None:
        """Retaining history must not disturb D-139 chain authentication."""

        temporary, repo, pack, _custody, _arm = make_go_fixture(PACK_NAME, "ALPHA")
        self.addCleanup(temporary.cleanup)
        predecessor = predecessor_pack_root(repo, PACK_NAME)
        self.assertIn(predecessor.name, readiness._PROFILE_BY_PACK)
        self.assertEqual(readiness._plan_profile(predecessor), "ALPHA")
        result = generate_freeze_receipt(pack, predecessor_pack_root=predecessor)
        receipt = json.loads(
            Path(result["receipt_path"]).read_text(encoding="utf-8")
        )
        self.assertEqual(receipt["receipt_id"], "freeze-0002")
        self.assertEqual(receipt["predecessor"]["pack_id"], predecessor.name)


if __name__ == "__main__":
    unittest.main()


class FreezeReplayExpiryOptOutCensusTests(unittest.TestCase):
    def test_no_production_caller_opts_out_of_expiry_enforcement(self) -> None:
        """The fail-closed default is the ONE expiry mechanism (FRE-01).

        Explicit per-site time arguments were removed as redundant; this
        census is the regression that keeps the opt-out out of production:
        enforce_expiry may appear in joulewise/ only at its definition and
        enforcement sites inside _authenticate_generic_evidence_item.
        """
        import pathlib

        root = pathlib.Path(__file__).resolve().parents[1]
        offenders: list[str] = []
        for path in sorted((root / "joulewise").rglob("*.py")):
            for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                if "enforce_expiry" not in line:
                    continue
                stripped = line.strip()
                if path.name == "arm_readiness.py" and (
                    stripped.startswith("enforce_expiry: bool")
                    or stripped.startswith("if enforce_expiry")
                ):
                    continue
                offenders.append(f"{path.name}:{number}: {stripped}")
        for path in sorted((root / "scripts").rglob("*.py")):
            for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                if "enforce_expiry" in line:
                    offenders.append(f"{path.name}:{number}: {line.strip()}")
        self.assertEqual(offenders, [])
