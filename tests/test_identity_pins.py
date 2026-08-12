from __future__ import annotations

import copy
import contextlib
import hashlib
import inspect
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path
from unittest import mock

from joulewise import identity_pins
from joulewise.identity_pins import (
    IDENTITY_PIN_DERIVATION_CONTRACT,
    IDENTITY_PIN_PROJECTION_REASON_CODES,
    IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA,
    IDENTITY_PIN_PROJECTION_WORK_ORDER,
    IdentityPinProjectionError,
    derive_model_runtime_config,
    freeze_projection,
    scientific_config_identity_sha256,
    validate_projection_receipt,
    verify_frozen_projection,
)
from joulewise.provenance import model_artifact_identity
from joulewise.schemas import BenchmarkConfig
from scripts import mint_floor_artifact_generalized as generalized
from scripts import project_identity_pins


MINT_GIT_ANCHOR = identity_pins._mint_git_anchor


def render_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected JSON object: {path}")
    return value


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", "-C", str(root), *args),
        check=True,
        capture_output=True,
        text=True,
    )


def init_git(root: Path) -> None:
    git(root, "init", "-q")
    git(root, "config", "user.name", "Identity Pin Test")
    git(root, "config", "user.email", "identity-pin-test@example.invalid")


def commit_pack(repository: Path, pack: Path, message: str) -> str:
    relative = pack.relative_to(repository).as_posix()
    git(repository, "add", "--", relative)
    git(repository, "commit", "-q", "-m", message)
    return git(repository, "rev-parse", "HEAD").stdout.strip()


def commit_paths(repository: Path, paths: list[Path], message: str) -> str:
    relative = [path.relative_to(repository).as_posix() for path in paths]
    git(repository, "add", "--", *relative)
    git(repository, "commit", "-q", "-m", message)
    return git(repository, "rev-parse", "HEAD").stdout.strip()


def synthetic_config(model_root: Path, run_id: str) -> dict:
    return {
        "schema_version": "0.1",
        "run_id": run_id,
        "model": {
            "name": "synthetic-model",
            "family": "synthetic",
            "source": str(model_root),
            "revision": "synthetic-revision-v1",
            "weight_format": "mlx",
        },
        "quantization": {"name": "int4", "bits": 4},
        "hardware_target": {
            "id": "synthetic_mac",
            "transport": "local",
            "runtime_backend": "mlx",
            "telemetry_backend": "powermetrics",
        },
        "workload_profile": {
            "name": "synthetic_decode",
            "prompt_tokens": 8,
            "output_tokens": 4,
            "repetitions": 1,
            "warmup_runs": 1,
        },
        "interconnect": {"name": "local"},
        "sampling": {"power_hz": 10.0, "idle_seconds": 1.0},
        "run_metadata": {
            "project": "identity-pin-test",
            "operator": "test",
            "tags": [
                "phase2",
                "calibration-plan-sha256=" + "a" * 64,
                "rep1" if run_id.endswith("1") else "rep2",
            ],
        },
    }


def declared_identity(config: dict) -> dict:
    typed = BenchmarkConfig.from_mapping(config).to_dict()
    return {
        "hardware_target": typed["hardware_target"]["id"],
        "runtime_backend": typed["hardware_target"]["runtime_backend"],
        "telemetry_backend": typed["hardware_target"]["telemetry_backend"],
        "model_name": typed["model"]["name"],
        "model_source": typed["model"]["source"],
        "model_revision": typed["model"]["revision"],
        "quantization": typed["quantization"],
        "workload_profile": typed["workload_profile"],
    }


def probe_metadata(config: BenchmarkConfig) -> dict:
    artifact = model_artifact_identity(config.model.source)
    return {
        "platform": "synthetic-macos-identity-test",
        "machine": "arm64",
        "device": {
            "device": config.hardware_target.id,
            "telemetry": "powermetrics",
            "boundary": "synthetic package boundary",
            "rail_manifest": ["cpu_power", "gpu_power", "ane_power"],
        },
        "quantization": asdict(config.quantization),
        "adapters": {
            "runtime": {
                "name": "mlx",
                "prepare_metadata": {
                    "adapter": "mlx_runtime",
                    "version": "synthetic-mlx-1",
                    "kernel_library": "synthetic-metal-1",
                    "batching_concurrency_policy": "single-request sequential",
                    "quantization": config.quantization.name,
                },
            },
            "telemetry": {"name": "powermetrics"},
        },
        "workload_provenance": {
            "model": {
                "name": config.model.name,
                "source": config.model.source,
                "revision": config.model.revision,
                "artifact_identity": artifact,
            },
            "tokenizer": {
                "backend": "mlx",
                "identifier": str(Path(config.model.source) / "tokenizer.json"),
                "revision": config.model.revision,
                "class": "SyntheticTokenizer",
                "vocab_size": 256,
            },
            "sampler": {
                "kind": "greedy",
                "temperature": 0.0,
                "pinned": True,
                "api": "synthetic.make_sampler",
                "parameter": "temp",
            },
            "output_policy": {
                "name": "fixed_budget_exact",
                "requested_tokens": config.workload_profile.output_tokens,
                "stop_condition": "requested_tokens_emitted",
            },
        },
    }


def make_pack(
    root: Path,
    *,
    supersedes: list[object] | None = None,
    pack_name: str = "synthetic-pack",
) -> tuple[Path, Path]:
    pack = root / pack_name
    model = pack / "model"
    model.mkdir(parents=True)
    weight = model / "weights.safetensors"
    weight.write_bytes(b"synthetic-weight-bytes")
    configs = [
        synthetic_config(model, "synthetic-r1"),
        synthetic_config(model, "synthetic-r2"),
    ]
    inventory = []
    for index, config in enumerate(configs, start=1):
        relative = f"configs/member-{index}.json"
        raw = render_json(config)
        path = pack / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        inventory.append({"path": relative, "sha256": sha256_bytes(raw)})
    projection = {
        "work_order": IDENTITY_PIN_PROJECTION_WORK_ORDER,
        "mode": "derive_never_operator_enter",
        "state": "unprojected",
        "required_before_arm": True,
        "derivation_contract": IDENTITY_PIN_DERIVATION_CONTRACT,
        "identity_units": [
            {
                "identity_unit_id": "synthetic/decode",
                "producer_plan_reference": {
                    "plan_id": "synthetic-producer-v1",
                    "path": "producer/calibration_plan.json",
                },
                "consumer_bindings": [
                    {
                        "arm": "A",
                        "family": "synthetic-family",
                        "measurement_arm": "decode",
                    }
                ],
                "declared_identity": declared_identity(configs[0]),
                "config_inventory": inventory,
                "model_runtime_config": {
                    "model_artifact_sha256": None,
                    "runtime_identity_sha256": None,
                    "config_set_sha256": None,
                },
            }
        ],
        "projection_receipt": None,
        "supersedes": list(supersedes or []),
    }
    tree = {
        "schema_version": "joulewise.d117_plan_tree.v1",
        "draft_status": "unfrozen_draft",
        "plan": {"plan_id": "synthetic-plan-v1"},
        "window_identity": {"window_id": "synthetic-window-v1"},
        "arm_attachments": {"identity_pin_projection": projection},
    }
    tree_raw = render_json(tree)
    (pack / "plan_tree.json").write_bytes(tree_raw)
    (pack / "plan_tree.sha256").write_text(
        f"{sha256_bytes(tree_raw)}  plan_tree.json\n", encoding="ascii"
    )
    return pack, weight


def pack_bytes(pack: Path) -> dict[str, bytes]:
    return {
        path.relative_to(pack).as_posix(): path.read_bytes()
        for path in sorted(pack.rglob("*"))
        if path.is_file()
    }


def rebind_frozen_chain(
    pack: Path,
    *,
    receipt_units: list[dict] | None = None,
    projection_input_sha256: str | None = None,
    receipt_id: str | None = None,
) -> None:
    """Simulate an operator rebuilding every mutable local SHA binding."""

    tree_path = pack / "plan_tree.json"
    tree = read_json(tree_path)
    projection = tree["arm_attachments"]["identity_pin_projection"]
    reference = projection["projection_receipt"]
    receipt_path = pack / reference["path"]
    receipt = read_json(receipt_path)
    if receipt_units is not None:
        receipt["identity_units"] = copy.deepcopy(receipt_units)
        by_id = {
            unit["identity_unit_id"]: unit["model_runtime_config"]
            for unit in receipt_units
        }
        for unit in projection["identity_units"]:
            unit["model_runtime_config"] = copy.deepcopy(by_id[unit["identity_unit_id"]])
    if projection_input_sha256 is not None:
        receipt["pack"]["projection_input_sha256"] = projection_input_sha256
    if receipt_id is not None:
        receipt["receipt_id"] = receipt_id
    receipt_raw = render_json(receipt)
    receipt_sha = sha256_bytes(receipt_raw)
    receipt_path.write_bytes(receipt_raw)
    receipt_path.with_suffix(".sha256").write_text(
        f"{receipt_sha}  {receipt_path.name}\n", encoding="ascii"
    )
    projection["projection_receipt"]["sha256"] = receipt_sha
    tree_raw = render_json(tree)
    tree_path.write_bytes(tree_raw)
    (pack / "plan_tree.sha256").write_text(
        f"{sha256_bytes(tree_raw)}  plan_tree.json\n", encoding="ascii"
    )


class SharedDerivationTests(unittest.TestCase):
    def test_synthetic_pack_triple_equals_generalized_mint_rederivation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            init_git(root)
            pack, _ = make_pack(root)
            reviewed_commit = commit_pack(root, pack, "unprojected pack")
            with (
                mock.patch(
                    "joulewise.identity_pins._runtime_probe_metadata",
                    side_effect=probe_metadata,
                ),
                mock.patch(
                    "joulewise.identity_pins._mint_git_anchor",
                    return_value=(root.resolve(), reviewed_commit),
                ),
            ):
                freeze_projection(pack)
            tree = read_json(pack / "plan_tree.json")
            projection = tree["arm_attachments"]["identity_pin_projection"]
            reference = projection["projection_receipt"]
            receipt = read_json(pack / reference["path"])
            unit = receipt["identity_units"][0]
            triple = unit["model_runtime_config"]
            generalized_rederived = generalized.derive_model_runtime_config(
                unit["realized_stack_identity"], triple["config_set_sha256"]
            )
            self.assertEqual(generalized_rederived, triple)
            config = read_json(
                pack
                / projection["identity_units"][0]["config_inventory"][0]["path"]
            )
            self.assertEqual(
                triple["config_set_sha256"], scientific_config_identity_sha256(config)
            )

    def test_directory_inventory_is_lexical_and_file_symlink_records_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "z.bin").write_bytes(b"z")
            target = root / "a.safetensors"
            target.write_bytes(b"a")
            (root / "m.pt").symlink_to(target)
            nested = root / "nested"
            nested.mkdir()
            (nested / "b.gguf").write_bytes(b"b")
            (root / "linked-dir").symlink_to(nested, target_is_directory=True)

            identity = model_artifact_identity(str(root))

            self.assertEqual(identity["status"], "ok")
            self.assertEqual(
                list(identity["files"]),
                ["a.safetensors", "m.pt", "nested/b.gguf", "z.bin"],
            )
            symlink = next(row for row in identity["inventory"] if row["path"] == "m.pt")
            self.assertTrue(symlink["symlink"])
            # Resolve both sides: macOS temp dirs alias /var -> /private/var.
            self.assertEqual(Path(symlink["resolved_path"]).resolve(), target.resolve())
            self.assertNotIn("linked-dir/b.gguf", identity["files"])


class ProjectionLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        init_git(self.root)
        self.pack, self.weight = make_pack(self.root)
        commit_pack(self.root, self.pack, "unprojected pack A")
        self.git_anchor = mock.patch(
            "joulewise.identity_pins._mint_git_anchor",
            side_effect=lambda: (
                self.root.resolve(),
                git(self.root, "rev-parse", "HEAD").stdout.strip(),
            ),
        )
        self.git_anchor.start()
        self.probe = mock.patch(
            "joulewise.identity_pins._runtime_probe_metadata",
            side_effect=probe_metadata,
        )
        self.probe.start()

    def tearDown(self) -> None:
        self.probe.stop()
        self.git_anchor.stop()
        self.temporary.cleanup()

    def _freeze_linear_successor(self, directory: str) -> Path:
        old_projection = read_json(self.pack / "plan_tree.json")["arm_attachments"][
            "identity_pin_projection"
        ]
        successor, _ = make_pack(
            self.root / directory,
            pack_name="synthetic-pack-r2",
            supersedes=[
                {
                    "pack_id": self.pack.name,
                    "pack_sha256": "a" * 64,
                    "projection_receipt_sha256": old_projection[
                        "projection_receipt"
                    ]["sha256"],
                    "readiness_sha256": "b" * 64,
                }
            ],
        )
        freeze_projection(successor)
        commit_pack(self.root, successor, f"freeze successor in {directory}")
        return successor

    def test_freeze_writes_authenticated_exact_key_receipt_and_is_idempotent(self) -> None:
        first = freeze_projection(self.pack)
        after_first = pack_bytes(self.pack)
        second = freeze_projection(self.pack)

        self.assertEqual(first["status"], "PASS")
        self.assertTrue(first["mutated"])
        self.assertFalse(second["mutated"])
        self.assertEqual(pack_bytes(self.pack), after_first)
        tree = read_json(self.pack / "plan_tree.json")
        projection = tree["arm_attachments"]["identity_pin_projection"]
        self.assertEqual(projection["state"], "frozen")
        self.assertNotIn(None, projection["identity_units"][0]["model_runtime_config"].values())
        reference = projection["projection_receipt"]
        receipt_path = self.pack / reference["path"]
        receipt_raw = receipt_path.read_bytes()
        self.assertEqual(sha256_bytes(receipt_raw), reference["sha256"])
        receipt = read_json(receipt_path)
        validate_projection_receipt(receipt)
        self.assertEqual(receipt["schema_version"], IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA)
        self.assertEqual(receipt["receipt_kind"], "freeze_projection")
        self.assertEqual(receipt["status"], "PASS")
        self.assertFalse((receipt_path.parent / "projection-0002.json").exists())

    def test_verify_is_pack_read_only_and_writes_custody_receipt(self) -> None:
        freeze_projection(self.pack)
        commit_pack(self.root, self.pack, "freeze A")
        before = pack_bytes(self.pack)
        custody = self.root / "custody"

        result = verify_frozen_projection(self.pack, custody, "bracket-001")
        custody_after_first = pack_bytes(custody)
        repeated = verify_frozen_projection(self.pack, custody, "bracket-001")

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["reason_codes"], [])
        self.assertEqual(repeated, result)
        self.assertEqual(pack_bytes(custody), custody_after_first)
        self.assertEqual(pack_bytes(self.pack), before)
        receipt_path = Path(result["receipt_path"])
        self.assertEqual(
            receipt_path,
            custody
            / self.pack.name
            / "receipts"
            / "bracket-001"
            / "identity-pin-arm-verify.json",
        )
        receipt = read_json(receipt_path)
        self.assertEqual(receipt["receipt_kind"], "arm_reverification")
        self.assertEqual(receipt["status"], "PASS")

    def test_verify_refuses_when_pack_git_state_is_unresolvable(self) -> None:
        isolated_root = self.root / "isolated"
        (isolated_root / ".git").mkdir(parents=True)
        isolated_pack, _ = make_pack(isolated_root)
        freeze_projection(isolated_pack)

        result = verify_frozen_projection(
            isolated_pack, self.root / "custody", "bracket-no-git-anchor"
        )

        self.assertEqual(result["status"], "REFUSE")
        self.assertEqual(
            result["reason_codes"],
            ["readiness_identity_artifact_unreadable"],
        )

    def test_same_repository_head_unresolvable_returns_authenticated_refusal(
        self,
    ) -> None:
        freeze_projection(self.pack)
        commit_pack(self.root, self.pack, "freeze A")
        tree = read_json(self.pack / "plan_tree.json")
        reference = tree["arm_attachments"]["identity_pin_projection"][
            "projection_receipt"
        ]
        frozen_receipt = read_json(self.pack / reference["path"])
        mint_module = identity_pins._load_mint_module()
        unresolved = subprocess.CompletedProcess(
            args=("git",), returncode=128, stdout="", stderr="fatal: bad HEAD"
        )

        with (
            mock.patch(
                "joulewise.identity_pins._mint_git_anchor", new=MINT_GIT_ANCHOR
            ),
            mock.patch.object(
                mint_module.subprocess, "run", return_value=unresolved
            ) as run,
        ):
            result = verify_frozen_projection(
                self.pack, self.root / "custody", "bracket-own-head-unreadable"
            )

        self.assertEqual(result["status"], "REFUSE")
        self.assertEqual(
            result["reason_codes"], ["readiness_identity_artifact_unreadable"]
        )
        self.assertEqual(run.call_count, 1)
        arm_receipt = read_json(Path(result["receipt_path"]))
        self.assertEqual(arm_receipt["pack"], frozen_receipt["pack"])
        self.assertEqual(arm_receipt["derivation"], frozen_receipt["derivation"])

    def test_mint_whole_repository_dirty_gate_controls_freeze_and_verify(
        self,
    ) -> None:
        mint_module = identity_pins._load_mint_module()
        dirty_path = self.root / "outside-pack-subtree.txt"

        with (
            mock.patch(
                "joulewise.identity_pins._mint_git_anchor", new=MINT_GIT_ANCHOR
            ),
            mock.patch.object(mint_module, "REPO_ROOT", self.root),
        ):
            dirty_path.write_text("dirty\n", encoding="utf-8")
            with self.assertRaises(mint_module.MintError) as mint_refusal:
                mint_module._actual_v2_git_state()
            with self.assertRaises(IdentityPinProjectionError) as freeze_refusal:
                freeze_projection(self.pack)
            self.assertEqual(
                freeze_refusal.exception.reason_code,
                "readiness_identity_environment_dirty",
            )
            self.assertIn(str(mint_refusal.exception), str(freeze_refusal.exception))

            dirty_path.unlink()
            freeze_projection(self.pack)
            commit_pack(self.root, self.pack, "freeze A")
            dirty_path.write_text("dirty again\n", encoding="utf-8")
            result = verify_frozen_projection(
                self.pack, self.root / "custody", "bracket-dirty-outside"
            )

        self.assertEqual(result["status"], "REFUSE")
        self.assertEqual(
            result["reason_codes"], ["readiness_identity_environment_dirty"]
        )
        self.assertIn("outside-pack-subtree.txt", str(result["observed"]))

    def test_pack_freeze_commit_does_not_change_derivation_identity(self) -> None:
        frozen_head = git(self.root, "rev-parse", "HEAD").stdout.strip()
        freeze_projection(self.pack)
        arm_head = commit_pack(self.root, self.pack, "freeze A")
        frozen_bytes = pack_bytes(self.pack)

        repeated = freeze_projection(self.pack)
        verified = verify_frozen_projection(
            self.pack, self.root / "custody", "bracket-after-freeze-commit"
        )

        self.assertFalse(repeated["mutated"])
        self.assertEqual(verified["status"], "PASS")
        self.assertEqual(pack_bytes(self.pack), frozen_bytes)
        frozen_reference = read_json(self.pack / "plan_tree.json")[
            "arm_attachments"
        ]["identity_pin_projection"]["projection_receipt"]
        frozen_receipt = read_json(self.pack / frozen_reference["path"])
        arm_receipt = read_json(Path(verified["receipt_path"]))
        self.assertEqual(frozen_receipt["derivation"]["git_commit"], frozen_head)
        self.assertEqual(arm_receipt["derivation"]["git_commit"], arm_head)

    def test_one_byte_model_perturbation_changes_hash_and_refuses_dirty(self) -> None:
        freeze_projection(self.pack)
        commit_pack(self.root, self.pack, "freeze A")
        frozen = read_json(self.pack / "plan_tree.json")["arm_attachments"][
            "identity_pin_projection"
        ]["identity_units"][0]["model_runtime_config"]
        before = pack_bytes(self.pack)
        self.weight.write_bytes(self.weight.read_bytes() + b"!")
        expected_after_weight_edit = pack_bytes(self.pack)

        result = verify_frozen_projection(
            self.pack, self.root / "custody", "bracket-perturbed"
        )

        self.assertEqual(result["status"], "REFUSE")
        self.assertEqual(
            result["reason_codes"], ["readiness_identity_environment_dirty"]
        )
        self.assertNotEqual(
            result["observed"]["model_runtime_config"][0][
                "model_artifact_sha256"
            ],
            frozen["model_artifact_sha256"],
        )
        self.assertNotEqual(before, expected_after_weight_edit)
        self.assertEqual(pack_bytes(self.pack), expected_after_weight_edit)

        tree = read_json(self.pack / "plan_tree.json")
        projection = tree["arm_attachments"]["identity_pin_projection"]
        current_units, projection_input_sha, _ = identity_pins._derive_projection_units(
            self.pack, projection
        )
        rebind_frozen_chain(
            self.pack,
            receipt_units=current_units,
            projection_input_sha256=projection_input_sha,
        )

        rebound = verify_frozen_projection(
            self.pack, self.root / "custody", "bracket-fully-rebound"
        )

        self.assertEqual(rebound["status"], "REFUSE")
        self.assertEqual(
            rebound["reason_codes"],
            ["readiness_identity_pinset_frozen_mismatch"],
        )
        self.assertNotEqual(
            rebound["observed"]["committed_receipt_sha256"],
            rebound["observed"]["on_disk_receipt_sha256"],
        )

    def test_receipt_id_only_rebind_refuses_committed_anchor_mismatch(self) -> None:
        freeze_projection(self.pack)
        commit_pack(self.root, self.pack, "freeze A")
        rebind_frozen_chain(
            self.pack,
            receipt_id="synthetic-pack/operator-rebound-receipt-id",
        )

        result = verify_frozen_projection(
            self.pack, self.root / "custody", "bracket-receipt-id-rebound"
        )

        self.assertEqual(result["status"], "REFUSE")
        self.assertEqual(
            result["reason_codes"],
            ["readiness_identity_pinset_frozen_mismatch"],
        )
        self.assertNotEqual(
            result["observed"]["committed_receipt_sha256"],
            result["observed"]["on_disk_receipt_sha256"],
        )

    def test_frozen_pin_mutation_refuses_with_frozen_mismatch(self) -> None:
        freeze_projection(self.pack)
        commit_pack(self.root, self.pack, "freeze A")
        tree = read_json(self.pack / "plan_tree.json")
        tree["arm_attachments"]["identity_pin_projection"]["identity_units"][0][
            "model_runtime_config"
        ]["runtime_identity_sha256"] = "f" * 64
        tree_raw = render_json(tree)
        (self.pack / "plan_tree.json").write_bytes(tree_raw)
        (self.pack / "plan_tree.sha256").write_text(
            f"{sha256_bytes(tree_raw)}  plan_tree.json\n", encoding="ascii"
        )
        before = pack_bytes(self.pack)

        result = verify_frozen_projection(
            self.pack, self.root / "custody", "bracket-pin-mismatch"
        )

        self.assertEqual(result["status"], "REFUSE")
        self.assertEqual(
            result["reason_codes"], ["readiness_identity_pinset_frozen_mismatch"]
        )
        self.assertEqual(pack_bytes(self.pack), before)

    def test_successor_reissue_appends_supersession_without_reusing_receipt(self) -> None:
        freeze_projection(self.pack)
        commit_pack(self.root, self.pack, "freeze A")
        old_projection = read_json(self.pack / "plan_tree.json")["arm_attachments"][
            "identity_pin_projection"
        ]
        successor_root = self.root / "successor"
        successor, _ = make_pack(
            successor_root,
            pack_name="synthetic-pack-r2",
            supersedes=[
                {
                    "pack_id": self.pack.name,
                    "pack_sha256": "a" * 64,
                    "projection_receipt_sha256": old_projection[
                        "projection_receipt"
                    ]["sha256"],
                    "readiness_sha256": "b" * 64,
                }
            ],
        )
        freeze_projection(successor)
        commit_pack(self.root, successor, "freeze successor B")

        projection = read_json(successor / "plan_tree.json")["arm_attachments"][
            "identity_pin_projection"
        ]
        receipt = read_json(successor / projection["projection_receipt"]["path"])
        self.assertEqual(receipt["supersedes"], projection["supersedes"])
        self.assertEqual(projection["state"], "frozen")
        self.assertTrue((self.pack / old_projection["projection_receipt"]["path"]).exists())
        old_result = verify_frozen_projection(
            self.pack, self.root / "custody", "bracket-old-after-successor"
        )
        successor_result = verify_frozen_projection(
            successor, self.root / "custody", "bracket-successor"
        )
        self.assertEqual(old_result["status"], "REFUSE")
        self.assertEqual(
            old_result["observed"]["superseded_by"]["receipt_id"],
            "synthetic-pack-r2/projection-0001",
        )
        old_arm_receipt = read_json(Path(old_result["receipt_path"]))
        self.assertEqual(
            old_arm_receipt["checks"][-1]["observed"]["superseded_by"][
                "receipt_id"
            ],
            "synthetic-pack-r2/projection-0001",
        )
        self.assertEqual(successor_result["status"], "PASS")

    def test_same_commit_successor_semantically_supersedes_predecessor(self) -> None:
        freeze_projection(self.pack)
        old_projection = read_json(self.pack / "plan_tree.json")["arm_attachments"][
            "identity_pin_projection"
        ]
        successor, _ = make_pack(
            self.root / "same-commit-successor",
            pack_name="synthetic-pack-r2",
            supersedes=[
                {
                    "pack_id": self.pack.name,
                    "pack_sha256": "a" * 64,
                    "projection_receipt_sha256": old_projection[
                        "projection_receipt"
                    ]["sha256"],
                    "readiness_sha256": "b" * 64,
                }
            ],
        )
        freeze_projection(successor)
        commit_paths(
            self.root,
            [self.pack, successor],
            "freeze predecessor and successor together",
        )

        result = verify_frozen_projection(
            self.pack, self.root / "custody", "bracket-same-commit-successor"
        )

        self.assertEqual(result["status"], "REFUSE")
        self.assertEqual(
            result["observed"]["superseded_by"]["receipt_id"],
            "synthetic-pack-r2/projection-0001",
        )

    def test_five_digit_successor_receipt_number_still_supersedes(self) -> None:
        freeze_projection(self.pack)
        old_projection = read_json(self.pack / "plan_tree.json")["arm_attachments"][
            "identity_pin_projection"
        ]
        successor, _ = make_pack(
            self.root / "five-digit-successor",
            pack_name="synthetic-pack-r5d",
            supersedes=[
                {
                    "pack_id": self.pack.name,
                    "pack_sha256": "a" * 64,
                    "projection_receipt_sha256": old_projection[
                        "projection_receipt"
                    ]["sha256"],
                    "readiness_sha256": "b" * 64,
                }
            ],
        )
        receipt_dir = successor / "identity_pin_projection.receipts"
        receipt_dir.mkdir(parents=True, exist_ok=True)
        seed = receipt_dir / "projection-9999.json"
        seed.write_text("{}")
        freeze_projection(successor)
        seed.unlink()
        emitted = sorted(path.name for path in receipt_dir.glob("projection-*.json"))
        self.assertEqual(emitted, ["projection-10000.json"])
        commit_paths(
            self.root,
            [self.pack, successor],
            "freeze predecessor and five-digit successor",
        )

        result = verify_frozen_projection(
            self.pack, self.root / "custody", "bracket-five-digit-successor"
        )

        self.assertEqual(result["status"], "REFUSE")
        self.assertEqual(
            result["observed"]["superseded_by"]["receipt_id"],
            "synthetic-pack-r5d/projection-10000",
        )

    def test_nonconforming_committed_receipt_name_refuses_never_passes(self) -> None:
        freeze_projection(self.pack)
        old_projection = read_json(self.pack / "plan_tree.json")["arm_attachments"][
            "identity_pin_projection"
        ]
        successor, _ = make_pack(
            self.root / "nonconforming-successor",
            pack_name="synthetic-pack-nc",
            supersedes=[
                {
                    "pack_id": self.pack.name,
                    "pack_sha256": "a" * 64,
                    "projection_receipt_sha256": old_projection[
                        "projection_receipt"
                    ]["sha256"],
                    "readiness_sha256": "b" * 64,
                }
            ],
        )
        freeze_projection(successor)
        receipt_dir = successor / "identity_pin_projection.receipts"
        emitted = receipt_dir / "projection-0001.json"
        smuggled = receipt_dir / "projection-000a.json"
        smuggled.write_text(emitted.read_text())
        emitted.unlink()
        commit_paths(
            self.root,
            [self.pack, successor],
            "freeze predecessor and nonconforming-named successor",
        )

        result = verify_frozen_projection(
            self.pack, self.root / "custody", "bracket-nonconforming-receipt"
        )

        self.assertNotEqual(result["status"], "PASS")
        self.assertEqual(result["status"], "REFUSE")
        self.assertEqual(
            result["reason_codes"],
            ["readiness_identity_receipt_namespace_anomalous"],
        )

    def test_sibling_commit_successor_semantically_supersedes_after_merge(
        self,
    ) -> None:
        base = git(self.root, "rev-parse", "HEAD").stdout.strip()
        predecessor_branch = git(
            self.root, "branch", "--show-current"
        ).stdout.strip()
        freeze_projection(self.pack)
        commit_pack(self.root, self.pack, "freeze predecessor on first sibling")
        old_projection = read_json(self.pack / "plan_tree.json")["arm_attachments"][
            "identity_pin_projection"
        ]

        git(self.root, "checkout", "-q", "-b", "successor-sibling", base)
        successor, _ = make_pack(
            self.root / "sibling-successor",
            pack_name="synthetic-pack-r2",
            supersedes=[
                {
                    "pack_id": self.pack.name,
                    "pack_sha256": "a" * 64,
                    "projection_receipt_sha256": old_projection[
                        "projection_receipt"
                    ]["sha256"],
                    "readiness_sha256": "b" * 64,
                }
            ],
        )
        freeze_projection(successor)
        commit_pack(self.root, successor, "freeze successor on second sibling")
        git(self.root, "checkout", "-q", predecessor_branch)
        git(
            self.root,
            "merge",
            "-q",
            "--no-ff",
            "-m",
            "join sibling freezes",
            "successor-sibling",
        )

        result = verify_frozen_projection(
            self.pack, self.root / "custody", "bracket-sibling-merge-successor"
        )

        self.assertEqual(result["status"], "REFUSE")
        self.assertEqual(
            result["observed"]["superseded_by"]["receipt_id"],
            "synthetic-pack-r2/projection-0001",
        )

    def test_detached_head_still_finds_semantic_successor(self) -> None:
        freeze_projection(self.pack)
        commit_pack(self.root, self.pack, "freeze A")
        self._freeze_linear_successor("detached-successor")
        git(self.root, "checkout", "-q", "--detach", "HEAD")

        result = verify_frozen_projection(
            self.pack, self.root / "custody", "bracket-detached-head"
        )

        self.assertEqual(result["status"], "REFUSE")
        self.assertEqual(
            result["observed"]["superseded_by"]["receipt_id"],
            "synthetic-pack-r2/projection-0001",
        )

    def test_deleted_worktree_successor_still_supersedes_from_head(self) -> None:
        freeze_projection(self.pack)
        commit_pack(self.root, self.pack, "freeze A")
        successor = self._freeze_linear_successor("deleted-successor")
        shutil.rmtree(successor.parent)

        result = verify_frozen_projection(
            self.pack, self.root / "custody", "bracket-deleted-successor"
        )

        self.assertEqual(result["status"], "REFUSE")
        self.assertEqual(
            result["observed"]["superseded_by"]["receipt_id"],
            "synthetic-pack-r2/projection-0001",
        )

    def test_shallow_history_without_pack_change_commit_refuses(self) -> None:
        freeze_projection(self.pack)
        commit_pack(self.root, self.pack, "freeze A")
        unrelated = self.root / "unrelated.txt"
        unrelated.write_text("later\n", encoding="utf-8")
        commit_paths(self.root, [unrelated], "later unrelated commit")
        clone_root = self.root.parent / f"{self.root.name}-shallow"
        subprocess.run(
            (
                "git",
                "clone",
                "-q",
                "--depth=1",
                self.root.resolve().as_uri(),
                str(clone_root),
            ),
            check=True,
            capture_output=True,
            text=True,
        )
        clone_pack = clone_root / self.pack.relative_to(self.root)

        with mock.patch(
            "joulewise.identity_pins._mint_git_anchor",
            side_effect=lambda: (
                clone_root.resolve(),
                git(clone_root, "rev-parse", "HEAD").stdout.strip(),
            ),
        ):
            result = verify_frozen_projection(
                clone_pack,
                self.root / "custody",
                "bracket-shallow-history",
            )

        self.assertEqual(result["status"], "REFUSE")
        self.assertEqual(
            result["reason_codes"], ["readiness_identity_artifact_unreadable"]
        )

    def test_u8_consumption_seam_can_fail_closed_on_u11_result(self) -> None:
        freeze_projection(self.pack)
        commit_pack(self.root, self.pack, "freeze A")
        self.weight.write_bytes(self.weight.read_bytes() + b"!")

        result = verify_frozen_projection(
            self.pack, self.root / "custody", "bracket-u8-stub"
        )
        frozen_reference = read_json(self.pack / "plan_tree.json")[
            "arm_attachments"
        ]["identity_pin_projection"]["projection_receipt"]
        readiness_identity_pin_projection = {
            "frozen_receipt": {
                "path": frozen_reference["path"],
                "sha256": frozen_reference["sha256"],
            },
            "arm_receipt": {
                "path": result["receipt_path"],
                "sha256": result["receipt_sha256"],
            },
            "derivation_contract": IDENTITY_PIN_DERIVATION_CONTRACT,
            "identity_unit_ids": ["synthetic/decode"],
            "status": result["status"],
        }
        self.assertEqual(
            set(readiness_identity_pin_projection),
            {
                "frozen_receipt",
                "arm_receipt",
                "derivation_contract",
                "identity_unit_ids",
                "status",
            },
        )
        self.assertEqual(readiness_identity_pin_projection["status"], "REFUSE")
        self.assertTrue(
            set(result["reason_codes"]).issubset(IDENTITY_PIN_PROJECTION_REASON_CODES)
        )


class DerivationOnlyArmPathTests(unittest.TestCase):
    def test_cli_and_public_arm_callables_accept_no_identity_values(self) -> None:
        parser_args = project_identity_pins.parse_args(
            [
                "verify",
                "pack",
                "--window-custody-root",
                "custody",
                "--bracket-session-id",
                "session",
            ]
        )
        self.assertEqual(
            set(vars(parser_args)),
            {"command", "pack_root", "window_custody_root", "bracket_session_id"},
        )
        forbidden = {"model", "runtime", "config", "identity", "pin", "override"}
        for callable_ in (freeze_projection, verify_frozen_projection):
            names = set(inspect.signature(callable_).parameters)
            with self.subTest(callable=callable_.__name__):
                self.assertFalse(
                    any(word in name for name in names for word in forbidden), names
                )

    def test_cli_refuses_unknown_identity_override_options(self) -> None:
        for option in (
            "--model-artifact-sha256",
            "--runtime-identity-sha256",
            "--config-set-sha256",
            "--identity-override",
        ):
            with (
                self.subTest(option=option),
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit),
            ):
                project_identity_pins.parse_args(
                    ["freeze", "pack", option, "a" * 64]
                )

    def test_unprojected_pack_refuses_serialized_operator_pin_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack, _ = make_pack(Path(temporary))
            tree_path = pack / "plan_tree.json"
            tree = read_json(tree_path)
            runtime = tree["arm_attachments"]["identity_pin_projection"][
                "identity_units"
            ][0]["model_runtime_config"]
            runtime.update(
                {
                    "model_artifact_sha256": "a" * 64,
                    "runtime_identity_sha256": "b" * 64,
                    "config_set_sha256": "c" * 64,
                }
            )
            tree_path.write_bytes(render_json(tree))

            with self.assertRaises(IdentityPinProjectionError) as raised:
                freeze_projection(pack)

            self.assertEqual(
                raised.exception.reason_code,
                "readiness_identity_artifact_unreadable",
            )

    def test_projection_reason_vocabulary_is_closed(self) -> None:
        self.assertEqual(
            IDENTITY_PIN_PROJECTION_REASON_CODES,
            {
                "readiness_identity_artifact_unreadable",
                "readiness_identity_environment_dirty",
                "readiness_identity_projection_mint_divergence",
                "readiness_identity_pinset_frozen_mismatch",
                "readiness_identity_receipt_namespace_anomalous",
            },
        )
        with self.assertRaises(ValueError):
            IdentityPinProjectionError("operator_identity_override", "invalid")

    def test_projection_reasons_are_registered_in_d078_decision_vocabulary(self) -> None:
        decision_log = Path("docs/decision_log.md").read_text(encoding="utf-8")
        marker = (
            "### D-078 registry amendment — 2026-08-11: "
            "identity-pin readiness refusals"
        )
        self.assertEqual(decision_log.count(marker), 1)
        amendment = decision_log.split(marker, 1)[1]
        for reason in IDENTITY_PIN_PROJECTION_REASON_CODES:
            with self.subTest(reason=reason):
                self.assertIn(f"`{reason}`", amendment)


if __name__ == "__main__":
    unittest.main()
