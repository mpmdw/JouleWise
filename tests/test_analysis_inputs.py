from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path
from typing import Any, Mapping
from unittest import mock

from joulewise.analysis_engine.inputs import (
    BundleEvidence,
    FloorEvidenceBinding,
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
            launch_lineage={"pack_root": str(pack)},
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
                        "condition_family_id": condition_id,
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

        with mock.patch(
            "joulewise.analysis_engine.inputs._frozen_consumer_identity_set",
            return_value=frozenset(identities),
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


if __name__ == "__main__":
    unittest.main()
