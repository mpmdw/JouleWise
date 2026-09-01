from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from typing import Any, Mapping

from joulewise.analysis_engine.inputs import (
    _realized_identity_matches_config,
    _typed_config,
    realized_scientific_identity,
)
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


if __name__ == "__main__":
    unittest.main()
