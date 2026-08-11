from __future__ import annotations

import copy
import contextlib
import hashlib
import inspect
import io
import json
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path
from unittest import mock

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


def render_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected JSON object: {path}")
    return value


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


class SharedDerivationTests(unittest.TestCase):
    def test_synthetic_pack_triple_equals_generalized_mint_rederivation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack, _ = make_pack(Path(temporary))
            with mock.patch(
                "joulewise.identity_pins._runtime_probe_metadata",
                side_effect=probe_metadata,
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
        self.pack, self.weight = make_pack(self.root)
        self.probe = mock.patch(
            "joulewise.identity_pins._runtime_probe_metadata",
            side_effect=probe_metadata,
        )
        self.probe.start()

    def tearDown(self) -> None:
        self.probe.stop()
        self.temporary.cleanup()

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

    def test_pack_freeze_commit_does_not_change_derivation_identity(self) -> None:
        with mock.patch(
            "joulewise.identity_pins._repo_git_commit", return_value="a" * 40
        ):
            freeze_projection(self.pack)
        frozen_bytes = pack_bytes(self.pack)

        with mock.patch(
            "joulewise.identity_pins._repo_git_commit", return_value="b" * 40
        ):
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
        self.assertEqual(frozen_receipt["derivation"]["git_commit"], "a" * 40)
        self.assertEqual(arm_receipt["derivation"]["git_commit"], "b" * 40)

    def test_one_byte_model_perturbation_changes_hash_and_refuses_dirty(self) -> None:
        freeze_projection(self.pack)
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
        observed = result["identity_units"][0]
        self.assertNotEqual(
            observed["model_artifact_sha256"], frozen["model_artifact_sha256"]
        )
        self.assertNotEqual(before, expected_after_weight_edit)
        self.assertEqual(pack_bytes(self.pack), expected_after_weight_edit)

    def test_frozen_pin_mutation_refuses_with_frozen_mismatch(self) -> None:
        freeze_projection(self.pack)
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

        projection = read_json(successor / "plan_tree.json")["arm_attachments"][
            "identity_pin_projection"
        ]
        receipt = read_json(successor / projection["projection_receipt"]["path"])
        self.assertEqual(receipt["supersedes"], projection["supersedes"])
        self.assertEqual(projection["state"], "frozen")
        self.assertTrue((self.pack / old_projection["projection_receipt"]["path"]).exists())

    def test_u8_consumption_seam_can_fail_closed_on_u11_result(self) -> None:
        freeze_projection(self.pack)
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
