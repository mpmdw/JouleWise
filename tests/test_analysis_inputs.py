from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any, Mapping
from unittest import mock

from joulewise import arm_readiness, identity_pins
from joulewise.arm_readiness import committed_pack_tree_sha256
from joulewise.analysis_engine import _resolve_contrast_floor
from joulewise.analysis_engine.inputs import (
    BundleEvidence,
    FloorEvidenceBinding,
    LoadedAnalysisInputs,
    _realized_identity_matches_config,
    _typed_config,
    floor_request_for_evidence,
    floor_stack_identity,
    realized_scientific_identity,
)
try:
    from joulewise.analysis_engine.inputs import _frozen_consumer_identity_set
except ImportError:  # RED staging: production helper lands with the cure.
    _frozen_consumer_identity_set = None
from joulewise.identity_pins import scientific_config_identity_sha256
from joulewise.suite import SuiteManifest, suite_manifest_sha256
from tests import test_d117_contrast_v5_pack as d117_fixture
from tests.test_detection_floor import make_cell, make_regime


ROOT = Path(__file__).resolve().parents[1]
GSM8K_MANIFEST_PATH = (
    ROOT / "configs" / "suite_manifests" / "gsm8k_scored_v6_qwen3.json"
)
MIXED_MANIFEST_PATH = (
    ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json"
)


def _legacy_realized_identity_matches_config(
    raw_config: Mapping[str, Any] | None,
    metadata: Mapping[str, Any] | None,
) -> bool:
    """The pre-ruling scalar implementation, copied byte-for-byte in meaning."""

    identity = realized_scientific_identity(raw_config, metadata)
    typed = _typed_config(raw_config) if isinstance(raw_config, Mapping) else None
    if identity is None or typed is None or not isinstance(metadata, Mapping):
        return False
    hardware = typed.get("hardware_target")
    workload_config = typed.get("workload_profile")
    workload = metadata.get("workload_provenance")
    output_policy = workload.get("output_policy") if isinstance(workload, Mapping) else None
    connection = metadata.get("connection")
    expected_model = typed.get("model")
    expected_quantization = typed.get("quantization")
    observed_model = metadata.get("model")
    observed_quantization = metadata.get("quantization")
    if not all(
        isinstance(value, Mapping)
        for value in (
            hardware,
            workload_config,
            output_policy,
            connection,
            expected_model,
            expected_quantization,
            observed_model,
            observed_quantization,
        )
    ):
        return False
    return bool(
        identity["runtime"]["name"] == hardware.get("runtime_backend")
        and identity["telemetry"]["name"] == hardware.get("telemetry_backend")
        and identity["device_boundary"]["device"] == hardware.get("id")
        and identity["device_boundary"]["telemetry"] == hardware.get("telemetry_backend")
        and connection.get("transport") == hardware.get("transport")
        and dict(observed_model) == dict(expected_model)
        and dict(observed_quantization) == dict(expected_quantization)
        and output_policy.get("requested_tokens") == workload_config.get("output_tokens")
    )


def _scalar_config() -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "run_id": "analysis-input-scalar",
        "model": {
            "name": "model",
            "family": "family",
            "source": "/models/model",
            "revision": "revision",
            "weight_format": "mlx",
        },
        "quantization": {"name": "int4", "bits": 4},
        "hardware_target": {
            "id": "mac",
            "transport": "local",
            "runtime_backend": "mlx",
            "telemetry_backend": "powermetrics",
        },
        "workload_profile": {
            "name": "decode",
            "prompt_tokens": 128,
            "output_tokens": 512,
            "repetitions": 1,
            "warmup_runs": 1,
        },
        "interconnect": {"name": "local"},
        "sampling": {"power_hz": 10.0, "idle_seconds": 1.0},
        "run_metadata": {
            "project": "analysis-input-test",
            "operator": "test",
            "tags": ["phase2"],
        },
    }


def _metadata_for(config: Mapping[str, Any], requested_tokens: int) -> dict[str, Any]:
    typed = _typed_config(config)
    assert typed is not None
    hardware = typed["hardware_target"]
    return {
        "device": {
            "device": hardware["id"],
            "telemetry": hardware["telemetry_backend"],
            "rail_manifest": ["cpu_power", "gpu_power"],
            "boundary": "package",
        },
        "connection": {"transport": hardware["transport"]},
        "model": copy.deepcopy(typed["model"]),
        "quantization": copy.deepcopy(typed["quantization"]),
        "adapters": {
            "runtime": {
                "name": hardware["runtime_backend"],
                "prepare_metadata": {
                    "adapter": "mlx_runtime",
                    "version": "1",
                },
            },
            "telemetry": {"name": hardware["telemetry_backend"]},
        },
        "workload_provenance": {
            "model": {
                "artifact_identity": {
                    "status": "ok",
                    "kind": "file_set",
                    "algorithm": "sha256",
                    "sha256": "a" * 64,
                }
            },
            "tokenizer": {
                "backend": "mlx",
                "identifier": "tokenizer",
                "revision": "revision",
                "class": "Tokenizer",
                "vocab_size": 1000,
            },
            "output_policy": {"requested_tokens": requested_tokens},
        },
    }


def _suite_config(manifest_sha256: str) -> dict[str, Any]:
    config = _scalar_config()
    config["workload_profile"] = {
        "name": "gsm8k_scored_v6",
        "suite_manifest_ref": "suite_manifest.json",
        "suite_manifest_sha256": manifest_sha256,
        "repetitions": 1,
        "warmup_runs": 1,
    }
    return config


def _stack_metadata_for(config: Mapping[str, Any]) -> dict[str, Any]:
    metadata = _metadata_for(config, 512)
    typed = _typed_config(config)
    assert typed is not None
    metadata.update(platform="synthetic-macos-analysis-test", machine="arm64")
    metadata["adapters"]["runtime"]["prepare_metadata"].update(
        kernel_library="synthetic-metal",
        batching_concurrency_policy="single-request sequential",
        quantization=typed["quantization"]["name"],
    )
    metadata["workload_provenance"]["model"].update(
        name=typed["model"]["name"],
        source=typed["model"]["source"],
        revision=typed["model"]["revision"],
    )
    metadata["workload_provenance"]["sampler"] = {
        "kind": "greedy",
        "temperature": 0.0,
        "pinned": True,
        "api": "synthetic.make_sampler",
        "parameter": "temp",
    }
    metadata["workload_provenance"]["output_policy"].update(
        name="fixed_budget_exact",
        stop_condition="requested_tokens_emitted",
    )
    return metadata


def _bundle_evidence(
    bundle_id: str,
    config: Mapping[str, Any],
    metadata: Mapping[str, Any],
    *,
    launch_lineage: Mapping[str, Any] | None = None,
) -> BundleEvidence:
    return BundleEvidence(
        entry={},
        bundle_id=bundle_id,
        relative_path=bundle_id,
        path=Path(bundle_id),
        summary=None,
        metadata=metadata,
        raw_config=config,
        strict_problems=(),
        base_reason_codes=(),
        config_sha256=None,
        summary_sha256=None,
        replacement_classification="registered",
        inclusion_status="included",
        launch_lineage=launch_lineage,
    )


class RealizedIdentityDispatchTests(unittest.TestCase):
    def test_scalar_path_matches_legacy_for_true_and_false_verdicts(self) -> None:
        config = _scalar_config()
        matching = _metadata_for(config, 512)
        mismatching = _metadata_for(config, 511)
        for label, metadata, expected in (
            ("matching", matching, True),
            ("mismatching", mismatching, False),
        ):
            with self.subTest(label=label):
                self.assertEqual(
                    _legacy_realized_identity_matches_config(config, metadata),
                    expected,
                )
                self.assertEqual(
                    _realized_identity_matches_config(config, metadata), expected
                )

    def test_all_retained_non_suite_bundles_keep_legacy_identity_verdicts(self) -> None:
        candidates = (ROOT / "runs", ROOT.parent / "JouleWise" / "runs")
        runs_root = next((path for path in candidates if path.is_dir()), None)
        if runs_root is None:
            self.skipTest("retained runs corpus is absent")
        bundle_paths = sorted(
            [*runs_root.glob("example-mac-mlx-local__r[123]")]
            + [*runs_root.glob("example-mac-mlx-qwen35-122b-512t__r[123]")]
        )
        self.assertEqual(len(bundle_paths), 6)
        for path in bundle_paths:
            with self.subTest(bundle=path.name):
                config = json.loads((path / "config.json").read_text(encoding="utf-8"))
                metadata = json.loads(
                    (path / "metadata.json").read_text(encoding="utf-8")
                )
                self.assertNotIn(
                    "suite_manifest_sha256", config["workload_profile"]
                )
                self.assertEqual(
                    _realized_identity_matches_config(config, metadata),
                    _legacy_realized_identity_matches_config(config, metadata),
                )

    def test_suite_shape_matches_manifest_hash_and_uniform_planned_budget(self) -> None:
        raw_manifest = json.loads(GSM8K_MANIFEST_PATH.read_text(encoding="utf-8"))
        manifest = SuiteManifest.from_mapping(raw_manifest)
        manifest_hash = suite_manifest_sha256(raw_manifest)
        config = _suite_config(manifest_hash)
        metadata = _metadata_for(config, 8 * 384)
        metadata["workload_provenance"]["suite"] = {
            "manifest_sha256": manifest_hash,
            "item_count": 8,
        }
        self.assertTrue(
            _realized_identity_matches_config(config, metadata, manifest)
        )

    def test_suite_shape_refuses_each_hash_count_and_budget_mismatch(self) -> None:
        raw_manifest = json.loads(GSM8K_MANIFEST_PATH.read_text(encoding="utf-8"))
        manifest = SuiteManifest.from_mapping(raw_manifest)
        manifest_hash = suite_manifest_sha256(raw_manifest)
        config = _suite_config(manifest_hash)
        baseline = _metadata_for(config, 8 * 384)
        baseline["workload_provenance"]["suite"] = {
            "manifest_sha256": manifest_hash,
            "item_count": 8,
        }
        mutations = {
            "manifest_hash": lambda value: value["workload_provenance"]["suite"].update(
                manifest_sha256="b" * 64
            ),
            "item_count": lambda value: value["workload_provenance"]["suite"].update(
                item_count=7
            ),
            "boolean_item_count": lambda value: value["workload_provenance"]["suite"].update(
                item_count=True
            ),
            "requested_tokens": lambda value: value["workload_provenance"][
                "output_policy"
            ].update(requested_tokens=3071),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                metadata = copy.deepcopy(baseline)
                mutate(metadata)
                self.assertFalse(
                    _realized_identity_matches_config(config, metadata, manifest)
                )
        self.assertFalse(
            _realized_identity_matches_config(config, baseline, None)
        )

    def test_suite_shape_refuses_a_manifest_without_one_output_cap(self) -> None:
        raw_manifest = json.loads(MIXED_MANIFEST_PATH.read_text(encoding="utf-8"))
        manifest = SuiteManifest.from_mapping(raw_manifest)
        manifest_hash = suite_manifest_sha256(raw_manifest)
        config = _suite_config(manifest_hash)
        metadata = _metadata_for(config, sum(
            item.shape.planned_output_tokens for item in manifest.items
        ))
        metadata["workload_provenance"]["suite"] = {
            "manifest_sha256": manifest_hash,
            "item_count": len(manifest.items),
        }
        self.assertGreater(
            len({item.shape.planned_output_tokens for item in manifest.items}), 1
        )
        self.assertFalse(
            _realized_identity_matches_config(config, metadata, manifest)
        )


class FrozenConsumerIdentitySetTests(unittest.TestCase):
    def _generated_frozen_gate_pack(
        self, root: Path
    ) -> tuple[d117_fixture.D117ContrastV5PackTests, Path]:
        fixture = d117_fixture.D117ContrastV5PackTests()
        fixture.setUp()
        fixture.init_fixture_git(root)
        fixture.configure(fixture.write_prefill_pin(root))
        pack = fixture.generate_pack(root)
        fixture.commit_fixture(root, "generated unprojected v5 pack")
        fixture.freeze_identity_fixture(root, pack)

        tree = json.loads((pack / "plan_tree.json").read_text(encoding="utf-8"))
        projection = tree["arm_attachments"]["identity_pin_projection"]
        identity_reference = projection["projection_receipt"]
        assert isinstance(identity_reference, Mapping)
        freeze_receipt = {
            "schema_version": "joulewise.arm_readiness_freeze_receipt.v1",
            "receipt_kind": "freeze",
            "receipt_id": "freeze-0001",
            "status": "PASS",
            "arm_disposition": "NOT_APPLICABLE",
            "issued_at_utc": "2026-09-02T00:00:00Z",
            "pack_identity": {
                "pack_id": pack.name,
                "plan_id": tree["plan"]["plan_id"],
                "window_id": tree["window_identity"]["window_id"],
                "pack_root": str(pack.resolve()),
                "plan_path": tree["plan"]["path"],
                "plan_sha256": tree["plan"]["actual_sha256"],
            },
            "row_registry": copy.deepcopy(
                tree["arm_attachments"]["arm_readiness"]["row_registry"]
            ),
            "evidence": [
                {
                    "evidence_id": "u11-freeze-projection",
                    "receipt_kind": "freeze_projection",
                    "namespace": "PACK",
                    "path": identity_reference["path"],
                    "sha256": identity_reference["sha256"],
                    "schema_version": identity_pins.IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA,
                    "status": "PASS",
                }
            ],
            "rows": [
                {
                    "row_id": "desk.identity_pin_projection",
                    "evaluation_phase": "FREEZE_AND_ARM",
                    "applicability": "REQUIRED",
                    "verdict": "PASS",
                    "predicate_id": "desk.identity_pin_projection.v1",
                    "evidence_ids": ["u11-freeze-projection"],
                }
            ],
            "refusals": [],
            "supersedes": None,
            "assurance": copy.deepcopy(arm_readiness.ASSURANCE),
        }
        arm_readiness.validate_freeze_receipt(freeze_receipt)
        freeze_raw = arm_readiness.render_json(freeze_receipt)
        freeze_sha = hashlib.sha256(freeze_raw).hexdigest()
        freeze_relative = "arm_readiness.freeze.receipts/freeze-0001.json"
        freeze_path = pack / freeze_relative
        freeze_path.parent.mkdir(parents=True, exist_ok=True)
        freeze_path.write_bytes(freeze_raw)
        freeze_path.with_name(f"{freeze_path.name}.sha256").write_bytes(
            arm_readiness.gnu_sidecar(freeze_sha, freeze_path.name)
        )
        tree["arm_attachments"]["arm_readiness"]["freeze_receipt"] = {
            "path": freeze_relative,
            "sha256": freeze_sha,
        }
        fixture.write_identity_tree(pack, tree)
        fixture.commit_fixture(root, "bind synthetic U8 freeze receipt")
        return fixture, pack

    def _generated_transport_case(
        self,
        pack: Path,
        *,
        include_lineage: bool = True,
    ) -> tuple[
        Mapping[str, Any],
        FloorEvidenceBinding,
        Mapping[str, Any],
        str,
        list[BundleEvidence],
    ]:
        tree = json.loads((pack / "plan_tree.json").read_text(encoding="utf-8"))
        projection = tree["arm_attachments"]["identity_pin_projection"]
        identity_receipt = json.loads(
            (pack / projection["projection_receipt"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        unit = next(
            item
            for item in identity_receipt["identity_units"]
            if item["identity_unit_id"] == "A/decode"
        )
        distinct: dict[str, Mapping[str, Any]] = {}
        for row in unit["config_inventory"]:
            config = json.loads((pack / row["path"]).read_text(encoding="utf-8"))
            distinct.setdefault(scientific_config_identity_sha256(config), config)
        configs = list(distinct.values())[:2]
        self.assertEqual(len(configs), 2)
        lineage = (
            {
                "pack_root": str(pack.resolve()),
                "pack_sha256": committed_pack_tree_sha256(pack),
            }
            if include_lineage
            else None
        )
        evidence = [
            _bundle_evidence(
                f"generated-{index}",
                config,
                _stack_metadata_for(config),
                launch_lineage=lineage,
            )
            for index, config in enumerate(configs)
        ]
        stack = floor_stack_identity(configs[0], evidence[0].metadata)
        assert stack is not None
        stack_sha = identity_pins.stack_identity_sha256(stack)
        condition_id = unit["consumer_bindings"][0]["family"]
        selector = {
            "metric": "phase_energy_j.decode",
            "window_class": "phase",
        }
        artifact = {
            "cells": [],
            "transport_groups": [
                {
                    "backend": "powermetrics",
                    **selector,
                    "stack_identity_sha256": stack_sha,
                    "source_cell_ids": ["transport-source"],
                    "allowed_consumer_condition_families": [
                        {
                            "condition_family_id": condition_id,
                            "condition_family_sha256": "c" * 64,
                        }
                    ],
                }
            ],
        }
        binding = FloorEvidenceBinding(
            bound_cell_ids=frozenset({"transport-source"}),
            cell_scientific_identity_sha256={},
            cell_stack_identity_sha256={},
            bound_bundle_sha256s=frozenset(),
            problems_by_cell={},
            global_problems=(),
        )
        return artifact, binding, {"floor_selector": selector}, condition_id, evidence

    def _generated_exact_case(
        self,
        pack: Path,
    ) -> tuple[
        Mapping[str, Any],
        FloorEvidenceBinding,
        Mapping[str, Any],
        str,
        list[BundleEvidence],
    ]:
        tree = json.loads((pack / "plan_tree.json").read_text(encoding="utf-8"))
        projection = tree["arm_attachments"]["identity_pin_projection"]
        identity_receipt = json.loads(
            (pack / projection["projection_receipt"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        unit = next(
            item
            for item in identity_receipt["identity_units"]
            if item["identity_unit_id"] == "A/decode"
        )
        config = json.loads(
            (pack / unit["config_inventory"][0]["path"]).read_text(
                encoding="utf-8"
            )
        )
        lineage = {
            "pack_root": str(pack.resolve()),
            "pack_sha256": committed_pack_tree_sha256(pack),
        }
        evidence = [
            _bundle_evidence(
                "generated-exact",
                config,
                _stack_metadata_for(config),
                launch_lineage=lineage,
            )
        ]
        stack = floor_stack_identity(config, evidence[0].metadata)
        assert stack is not None
        condition_id = unit["consumer_bindings"][0]["family"]
        selector = {
            "metric": "phase_energy_j.decode",
            "window_class": "phase",
        }
        cell = make_cell(
            cell_id="exact-cell",
            regime=make_regime(stack_identity=stack),
            condition=condition_id,
            metric=selector["metric"],
        )
        cell["key"]["window_class"] = selector["window_class"]
        artifact = {
            "artifact_id": "identity-refusal-test-floor",
            "calibration_scope": "window_a",
            "cells": [cell],
            "transport_groups": [],
        }
        stack_sha = identity_pins.stack_identity_sha256(stack)
        binding = FloorEvidenceBinding(
            bound_cell_ids=frozenset({"exact-cell"}),
            cell_scientific_identity_sha256={
                "exact-cell": scientific_config_identity_sha256(config)
            },
            cell_stack_identity_sha256={"exact-cell": stack_sha},
            bound_bundle_sha256s=frozenset(),
            problems_by_cell={},
            global_problems=(),
        )
        return artifact, binding, {"floor_selector": selector}, condition_id, evidence

    def _production_floor_resolution(
        self,
        case: tuple[
            Mapping[str, Any],
            FloorEvidenceBinding,
            Mapping[str, Any],
            str,
            list[BundleEvidence],
        ],
    ):
        artifact, binding, contrast, condition_id, evidence = case
        production_contrast = copy.deepcopy(dict(contrast))
        production_contrast["floor_selector"]["condition_family_ids"] = [
            condition_id
        ]
        cells = artifact.get("cells", [])
        condition_sha = (
            cells[0].get("key", {}).get("condition_family_sha256")
            if cells
            else next(
                family["condition_family_sha256"]
                for group in artifact.get("transport_groups", [])
                for family in group.get(
                    "allowed_consumer_condition_families", []
                )
                if family.get("condition_family_id") == condition_id
            )
        )
        inputs = LoadedAnalysisInputs(
            manifest={
                "schema_version": "joulewise.analysis_manifest.v3.finalized",
                "arms": [
                    {
                        "condition_family_id": condition_id,
                        "condition_family_sha256": condition_sha,
                    }
                ],
            },
            manifest_sha256="a" * 64,
            floor_artifact=artifact,
            floor_sha256="b" * 64,
            registered={},
            effective={},
            extra_audits=(),
            valid_replacements=(),
            unregistered_matching=(),
            top_up_entry_ids=frozenset(),
            floor_binding=binding,
        )
        return _resolve_contrast_floor(
            inputs,
            production_contrast,
            {condition_id: evidence},
            None,
        )[0]

    def test_production_refuses_unauthenticated_frozen_identity_set_with_named_reason(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="analysis-v5-receipt-label-") as temporary:
            root = Path(temporary)
            _fixture, pack = self._generated_frozen_gate_pack(root)
            case = self._generated_exact_case(pack)
            tree = json.loads((pack / "plan_tree.json").read_text(encoding="utf-8"))
            receipt_path = pack / tree["arm_attachments"][
                "identity_pin_projection"
            ]["projection_receipt"]["path"]
            raw = bytearray(receipt_path.read_bytes())
            raw[len(raw) // 2] ^= 1
            receipt_path.write_bytes(bytes(raw))

            resolution = self._production_floor_resolution(case)

            self.assertEqual(resolution.status, "refused")
            self.assertEqual(
                resolution.reason_codes,
                ("consumer_identity_set_unauthenticated",),
            )
            self.assertNotIn("consumer_term_unknown", resolution.reason_codes)

    def test_production_refuses_identity_outside_authenticated_set_with_named_reason(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="analysis-v5-member-label-") as temporary:
            root = Path(temporary)
            _fixture, pack = self._generated_frozen_gate_pack(root)
            case = self._generated_exact_case(pack)
            raw_config = case[4][0].raw_config
            assert isinstance(raw_config, dict)
            raw_config["run_metadata"]["tags"].append("identity-drift")

            resolution = self._production_floor_resolution(case)

            self.assertEqual(resolution.status, "refused")
            self.assertEqual(
                resolution.reason_codes,
                ("consumer_identity_undeclared",),
            )

    def test_production_refuses_legacy_multi_identity_without_declaration_with_named_reason(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="analysis-v5-legacy-label-") as temporary:
            root = Path(temporary)
            _fixture, pack = self._generated_frozen_gate_pack(root)
            case = self._generated_transport_case(pack, include_lineage=False)

            resolution = self._production_floor_resolution(case)

            self.assertEqual(resolution.status, "refused")
            self.assertEqual(
                resolution.reason_codes,
                ("consumer_identity_undeclared",),
            )

    def test_production_accepts_same_authenticated_fixture_without_receipt_perturbation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="analysis-v5-receipt-control-") as temporary:
            root = Path(temporary)
            _fixture, pack = self._generated_frozen_gate_pack(root)

            resolution = self._production_floor_resolution(
                self._generated_exact_case(pack)
            )

            self.assertIn(resolution.status, {"exact", "transported"})
            self.assertEqual(resolution.reason_codes, ())

    def test_missing_pack_root_refuses_with_unauthenticated_label(self) -> None:
        with tempfile.TemporaryDirectory(prefix="analysis-v5-missing-root-") as temporary:
            root = Path(temporary)
            _fixture, pack = self._generated_frozen_gate_pack(root)
            case = self._generated_exact_case(pack)
            missing_pack = root / "missing-pack-root"
            self.assertFalse(missing_pack.exists())
            for row in case[4]:
                assert isinstance(row.launch_lineage, dict)
                row.launch_lineage["pack_root"] = str(missing_pack.resolve())

            self.assertEqual(
                _frozen_consumer_identity_set(case[4], case[3]),
                frozenset(),
            )
            resolution = self._production_floor_resolution(case)

            self.assertEqual(resolution.status, "refused")
            self.assertEqual(
                resolution.reason_codes,
                ("consumer_identity_set_unauthenticated",),
            )

    def test_u8_freeze_receipt_reaches_committed_v3_member_identity_set(self) -> None:
        pack = ROOT / "configs/campaigns/d117_floor_qwen25_1p5b_v3"
        receipt = json.loads(
            (
                pack
                / "identity_pin_projection.receipts"
                / "projection-0001.json"
            ).read_text(encoding="utf-8")
        )
        unit = receipt["identity_units"][0]
        condition_family_id = unit["consumer_bindings"][0]["family"]
        evidence = _bundle_evidence(
            "v3-lineage-probe",
            _scalar_config(),
            _metadata_for(_scalar_config(), 512),
            launch_lineage={
                "pack_root": str(pack),
                "pack_sha256": committed_pack_tree_sha256(pack),
            },
        )
        expected = frozenset(
            scientific_config_identity_sha256(
                json.loads((pack / row["path"]).read_text(encoding="utf-8"))
            )
            for row in unit["config_inventory"]
        )

        self.assertEqual(
            _frozen_consumer_identity_set([evidence], condition_family_id),
            expected,
        )

    def test_successor_lineage_requires_every_row_to_name_one_pack_root(self) -> None:
        evidence = _bundle_evidence(
            "missing-pack-root",
            _scalar_config(),
            _metadata_for(_scalar_config(), 512),
            launch_lineage={"pack_sha256": "a" * 64},
        )

        self.assertEqual(
            _frozen_consumer_identity_set([evidence], "condition-family"),
            frozenset(),
        )

    def test_generated_pack_gate_and_caller_refuse_stale_receipt_bytes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="analysis-v5-pack-tamper-") as temporary:
            root = Path(temporary)
            _fixture, pack = self._generated_frozen_gate_pack(root)
            case = self._generated_transport_case(pack)
            self.assertIsNotNone(floor_request_for_evidence(*case))

            tree = json.loads((pack / "plan_tree.json").read_text(encoding="utf-8"))
            receipt_path = pack / tree["arm_attachments"]["identity_pin_projection"][
                "projection_receipt"
            ]["path"]
            raw = bytearray(receipt_path.read_bytes())
            raw[len(raw) // 2] ^= 1
            receipt_path.write_bytes(bytes(raw))

            self.assertIsNone(floor_request_for_evidence(*case))

    def test_self_consistent_forged_pack_requires_launch_tree_digest_binding(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="analysis-v5-pack-forgery-") as temporary:
            root = Path(temporary)
            fixture, pack = self._generated_frozen_gate_pack(root)
            transport_case = self._generated_transport_case(pack)
            lineage = transport_case[4][0].launch_lineage
            assert isinstance(lineage, Mapping)
            honest_sha = lineage["pack_sha256"]

            raw_config = transport_case[4][0].raw_config
            assert isinstance(raw_config, dict)
            raw_config["run_metadata"]["tags"].append("identity-drift")

            tree = json.loads((pack / "plan_tree.json").read_text(encoding="utf-8"))
            projection = tree["arm_attachments"]["identity_pin_projection"]
            receipt_path = pack / projection["projection_receipt"]["path"]
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            unit = next(
                item
                for item in receipt["identity_units"]
                if item["identity_unit_id"] == "A/decode"
            )
            inventory_row = unit["config_inventory"][0]
            config_raw = (
                json.dumps(raw_config, indent=2, sort_keys=True) + "\n"
            ).encode("utf-8")
            (pack / inventory_row["path"]).write_bytes(config_raw)
            inventory_row["sha256"] = hashlib.sha256(config_raw).hexdigest()
            identities = {
                scientific_config_identity_sha256(
                    json.loads(
                        (pack / row["path"]).read_text(encoding="utf-8")
                    )
                )
                for row in unit["config_inventory"]
            }
            new_set_sha = identity_pins.identity_unit_config_set_sha256(identities)
            unit["model_runtime_config"]["config_set_sha256"] = new_set_sha
            projection_unit = next(
                item
                for item in projection["identity_units"]
                if item["identity_unit_id"] == "A/decode"
            )
            projection_unit["model_runtime_config"][
                "config_set_sha256"
            ] = new_set_sha
            for projection_row in projection_unit["config_inventory"]:
                if projection_row["path"] == inventory_row["path"]:
                    projection_row["sha256"] = inventory_row["sha256"]

            receipt_raw = identity_pins._render_json(receipt)
            receipt_sha = hashlib.sha256(receipt_raw).hexdigest()
            receipt_path.write_bytes(receipt_raw)
            receipt_path.with_suffix(".sha256").write_bytes(
                arm_readiness.gnu_sidecar(receipt_sha, receipt_path.name)
            )
            projection["projection_receipt"]["sha256"] = receipt_sha

            freeze_reference = tree["arm_attachments"]["arm_readiness"][
                "freeze_receipt"
            ]
            freeze_path = pack / freeze_reference["path"]
            freeze_receipt = json.loads(freeze_path.read_text(encoding="utf-8"))
            for item in freeze_receipt["evidence"]:
                if item["evidence_id"] == "u11-freeze-projection":
                    item["sha256"] = receipt_sha
            freeze_raw = arm_readiness.render_json(freeze_receipt)
            freeze_sha = hashlib.sha256(freeze_raw).hexdigest()
            freeze_path.write_bytes(freeze_raw)
            freeze_path.with_name(f"{freeze_path.name}.sha256").write_bytes(
                arm_readiness.gnu_sidecar(freeze_sha, freeze_path.name)
            )
            freeze_reference["sha256"] = freeze_sha
            fixture.write_identity_tree(pack, tree)
            fixture.commit_fixture(root, "forge: A/decode declares drifted identity")
            forged_sha = committed_pack_tree_sha256(pack)
            self.assertNotEqual(forged_sha, honest_sha)

            exact_case = self._generated_exact_case(pack)
            for row in exact_case[4]:
                assert isinstance(row.launch_lineage, dict)
                row.launch_lineage["pack_sha256"] = honest_sha
            self.assertEqual(
                exact_case[4][0].raw_config["run_metadata"]["tags"].count(
                    "identity-drift"
                ),
                1,
            )
            drifted_identity = scientific_config_identity_sha256(
                exact_case[4][0].raw_config
            )
            exact_case[1].cell_scientific_identity_sha256[
                "exact-cell"
            ] = drifted_identity

            resolution = self._production_floor_resolution(exact_case)

            self.assertEqual(resolution.status, "refused")
            self.assertEqual(
                resolution.reason_codes,
                ("consumer_identity_set_unauthenticated",),
            )
            self.assertIsNone(floor_request_for_evidence(*transport_case))

            for row in exact_case[4]:
                assert isinstance(row.launch_lineage, dict)
                row.launch_lineage["pack_sha256"] = forged_sha
            declared = _frozen_consumer_identity_set(exact_case[4], exact_case[3])
            self.assertIn(drifted_identity, declared)
            control = self._production_floor_resolution(exact_case)
            self.assertEqual(control.status, "exact")
            self.assertEqual(control.reason_codes, ())

    def test_generated_pack_gate_refuses_plan_receipt_config_set_mismatch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="analysis-v5-config-set-") as temporary:
            root = Path(temporary)
            fixture, pack = self._generated_frozen_gate_pack(root)
            tree = json.loads((pack / "plan_tree.json").read_text(encoding="utf-8"))
            unit = next(
                item
                for item in tree["arm_attachments"]["identity_pin_projection"][
                    "identity_units"
                ]
                if item["identity_unit_id"] == "A/decode"
            )
            unit["model_runtime_config"]["config_set_sha256"] = "f" * 64
            fixture.write_identity_tree(pack, tree)
            fixture.commit_fixture(root, "drift plan config-set binding")

            self.assertIsNone(
                floor_request_for_evidence(*self._generated_transport_case(pack))
            )

    def test_generated_multi_identity_evidence_without_lineage_refuses(self) -> None:
        with tempfile.TemporaryDirectory(prefix="analysis-v5-no-lineage-") as temporary:
            root = Path(temporary)
            _fixture, pack = self._generated_frozen_gate_pack(root)

            self.assertIsNone(
                floor_request_for_evidence(
                    *self._generated_transport_case(pack, include_lineage=False)
                )
            )

    def test_multi_identity_transport_requires_declared_subset_and_skips_exact_cell(
        self,
    ) -> None:
        first = _suite_config("a" * 64)
        second = _suite_config("b" * 64)
        first_metadata = _stack_metadata_for(first)
        second_metadata = _stack_metadata_for(second)
        evidence = [
            _bundle_evidence("first", first, first_metadata),
            _bundle_evidence("second", second, second_metadata),
        ]
        identities = {
            scientific_config_identity_sha256(first),
            scientific_config_identity_sha256(second),
        }
        stack = floor_stack_identity(first, first_metadata)
        assert stack is not None
        stack_sha = hashlib.sha256(
            b"joulewise.stack_identity.v1\0"
            + json.dumps(
                stack,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        condition_id = "rotating-decode-family"
        selector = {
            "metric": "phase_energy_j.decode",
            "window_class": "phase",
        }
        artifact = {
            "cells": [
                {
                    "cell_id": "exact-cell",
                    "key": {
                        "backend": "powermetrics",
                        **selector,
                        "condition_family_id": "different-exact-cell-family",
                        "condition_family_sha256": "d" * 64,
                    },
                }
            ],
            "transport_groups": [
                {
                    "backend": "powermetrics",
                    **selector,
                    "stack_identity_sha256": stack_sha,
                    "source_cell_ids": ["transport-source"],
                    "allowed_consumer_condition_families": [
                        {
                            "condition_family_id": condition_id,
                            "condition_family_sha256": "c" * 64,
                        }
                    ],
                }
            ],
        }
        binding = FloorEvidenceBinding(
            bound_cell_ids=frozenset({"exact-cell", "transport-source"}),
            cell_scientific_identity_sha256={
                "exact-cell": scientific_config_identity_sha256(first)
            },
            cell_stack_identity_sha256={"exact-cell": stack_sha},
            bound_bundle_sha256s=frozenset(),
            problems_by_cell={},
            global_problems=(),
        )
        contrast = {"floor_selector": selector}

        with (
            mock.patch(
                "joulewise.analysis_engine.inputs._frozen_consumer_identity_set",
                return_value=frozenset(identities),
            ),
            mock.patch(
                "joulewise.analysis_engine.inputs.scientific_config_identity_sha256",
                side_effect=AssertionError("identity was recomputed"),
            ),
        ):
            request = floor_request_for_evidence(
                artifact,
                binding,
                contrast,
                condition_id,
                evidence,
            )

        self.assertIsNotNone(request)
        self.assertEqual(request.condition_family_sha256, "c" * 64)

        artifact["cells"][0]["key"]["condition_family_id"] = condition_id
        with mock.patch(
            "joulewise.analysis_engine.inputs._frozen_consumer_identity_set",
            return_value=frozenset(identities),
        ):
            same_condition_refused = floor_request_for_evidence(
                artifact,
                binding,
                contrast,
                condition_id,
                evidence,
            )
        self.assertIsNone(same_condition_refused)

        with mock.patch(
            "joulewise.analysis_engine.inputs._frozen_consumer_identity_set",
            return_value=frozenset({scientific_config_identity_sha256(first)}),
        ):
            refused = floor_request_for_evidence(
                artifact,
                binding,
                contrast,
                condition_id,
                evidence,
            )
        self.assertIsNone(refused)

    def test_generated_multi_identity_transport_uses_real_frozen_gate_and_skips_exact_cell(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="analysis-v5-real-gate-") as temporary:
            root = Path(temporary)
            _fixture, pack = self._generated_frozen_gate_pack(root)
            case = self._generated_transport_case(pack)
            artifact, _binding, contrast, condition_id, evidence = case

            resolution = self._production_floor_resolution(case)
            self.assertNotIn(
                "consumer_identity_set_unauthenticated",
                resolution.reason_codes,
            )
            declared = _frozen_consumer_identity_set(evidence, condition_id)
            evidence_identities = {
                scientific_config_identity_sha256(row.raw_config)
                for row in evidence
            }
            self.assertTrue(evidence_identities.issubset(declared))
            self.assertEqual(len(evidence_identities), 2)

            request = floor_request_for_evidence(*case)

            self.assertIsNotNone(request)
            self.assertEqual(request.condition_family_sha256, "c" * 64)

            artifact["cells"].append(
                {
                    "cell_id": "exact-cell",
                    "key": {
                        "backend": "powermetrics",
                        **contrast["floor_selector"],
                        "condition_family_id": condition_id,
                        "condition_family_sha256": "d" * 64,
                    },
                }
            )
            self.assertIsNone(floor_request_for_evidence(*case))


if __name__ == "__main__":
    unittest.main()
