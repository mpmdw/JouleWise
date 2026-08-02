"""Frozen cross-stack ABBA analysis-manifest v3.

Version 3 is intentionally a sibling of the byte-frozen Slice-2M v1 schema
and the AP-SPEC v2 schema.  It owns the one ratified Splitwise decode
contrast: ten contiguous A/B/B/A blocks, two realized model stacks, one
two-sided Holm-family hypothesis, and an authenticated whole-window verdict
basis.  The module is stdlib-only and performs no statistical estimation.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Mapping


SCHEMA_VERSION = "joulewise.analysis_manifest.v3"
MANIFEST_NAME = "analysis_manifest_v3.json"
PLAN_ID = "splitwise-decode-v1-m3max-qwen25-1p5b-vs-7b"
PLANNED_N_BLOCKS = 10
ESTIMATOR_ID = "abba_block_arm_mean_difference_t_v1"
FLOOR_RULE_ID = "cross_stack_armwise_max.v1"
EXACT_STACK_RULE_ID = "exact_stack_only.v1"
VERDICT_BASIS_SHA256 = (
    "1e08e8eff4ede001a6d68525a7748bbf66f81278a3b963b9b24e7405d105d147"
)
CALIBRATION_PLAN_SHA256 = (
    "7b563724be38254bf0769bca5818e9bcd70f76288e79650b55c3e051bf636b04"
)
ROOT_ORDER_SHA256 = (
    "a0184a5e994c3139ed9ce8a43951368e7058a6cf635e8637f7ad693d827e0404"
)
STAGE_ORDER_SHA256S = {
    "01_decode_contrast_blocks_01_05": (
        "16866c00031e138c002b962a3873dfba49e59413f39e702329c4f5d87c164e06"
    ),
    "02_decode_contrast_blocks_06_10": (
        "8e7fc04cc3b5f27735c9ff862a690b6b8358bb7e38cedffd86995fd3465f4ab0"
    ),
}

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
MANIFEST_ID_RE = re.compile(r"^am-[0-9a-f]{64}$")
RUN_ID_RE = re.compile(
    r"^swdec-contrast-b(?P<block>[0-9]{2})-(?P<position>a1|b1|b2|a2)$"
)
POSITION_ORDER = ("A1", "B1", "B2", "A2")
POSITION_ARMS = {"A1": "A", "B1": "B", "B2": "B", "A2": "A"}

ARM_FREEZE: Mapping[str, Mapping[str, Any]] = {
    "A": {
        "condition_family_id": "sw-decode-a-qwen25-1p5b",
        "condition_family_sha256": (
            "c13a3ebf5461ed9a442a8e67555f70301848d56a55ab766570d46ca067934f12"
        ),
        "condition_family_file_sha256": (
            "3ff3a801d7f74ca3d3bd74d961aadde304e7fd1adc7940a39cf47ff0c40943cf"
        ),
        "condition_family_path": (
            "condition_families/condition_family_sw_decode_a_qwen25_1p5b.json"
        ),
        "model_tag": "qwen25-1p5b-mlx",
        "cell_id": "sw-decode-arm-a-qwen25-1p5b",
        "realized_stack_identity": {
            "model_artifact": {
                "algorithm": "sha256",
                "kind": "file_set",
                "folded_sha256": (
                    "fea4cb940b54448a693c95a0734949cbdca21a39dda990d669b7f615e4a7c712"
                ),
            },
            "tokenizer": {
                "backend": "mlx",
                "identifier": (
                    "/Users/edr/jw_models/mlx-community/"
                    "Qwen2.5-1.5B-Instruct-4bit"
                ),
                "revision": "8b403126fc14f14cfc99bb4cfa72ecbc129ea677",
                "class": "TokenizerWrapper",
                "vocab_size": 151643,
            },
            "runtime": {"name": "mlx", "adapter": "mlx_runtime", "version": None},
            "telemetry": {"name": "powermetrics"},
            "device_boundary": {
                "device": "macbook_m3_max",
                "telemetry": "powermetrics",
                "rail_manifest": ["cpu_power", "gpu_power", "ane_power"],
                "boundary": "Apple SoC CPU + GPU + ANE package power",
            },
            "model": {
                "name": "Qwen2.5-1.5B-Instruct-4bit",
                "family": "qwen2.5",
                "source": (
                    "/Users/edr/jw_models/mlx-community/"
                    "Qwen2.5-1.5B-Instruct-4bit"
                ),
                "revision": "8b403126fc14f14cfc99bb4cfa72ecbc129ea677",
                "weight_format": "mlx",
                "context_window": 32768,
            },
            "quantization": {"name": "int4", "bits": 4, "group_size": None},
        },
    },
    "B": {
        "condition_family_id": "sw-decode-b-qwen25-7b",
        "condition_family_sha256": (
            "5149a8552600341883439a73fa135caa0e6ba292544c7c6fe2e69674318df4e3"
        ),
        "condition_family_file_sha256": (
            "c153b8dcbae5761e1d39404e55415d0ed95072151fb98fe75bce3e2740d54b9e"
        ),
        "condition_family_path": (
            "condition_families/condition_family_sw_decode_b_qwen25_7b.json"
        ),
        "model_tag": "qwen25-7b-mlx",
        "cell_id": "sw-decode-arm-b-qwen25-7b",
        "realized_stack_identity": {
            "model_artifact": {
                "algorithm": "sha256",
                "kind": "file_set",
                "folded_sha256": (
                    "af17dfa81e0bd4409cc203d3c928849262342abeb8d90d2342e29f1988f6a630"
                ),
            },
            "tokenizer": {
                "backend": "mlx",
                "identifier": (
                    "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit"
                ),
                "revision": "c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed",
                "class": "TokenizerWrapper",
                "vocab_size": 151643,
            },
            "runtime": {"name": "mlx", "adapter": "mlx_runtime", "version": None},
            "telemetry": {"name": "powermetrics"},
            "device_boundary": {
                "device": "macbook_m3_max",
                "telemetry": "powermetrics",
                "rail_manifest": ["cpu_power", "gpu_power", "ane_power"],
                "boundary": "Apple SoC CPU + GPU + ANE package power",
            },
            "model": {
                "name": "Qwen2.5-7B-Instruct-4bit",
                "family": "qwen2.5",
                "source": (
                    "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit"
                ),
                "revision": "c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed",
                "weight_format": "mlx",
                "context_window": 32768,
            },
            "quantization": {"name": "int4", "bits": 4, "group_size": None},
        },
    },
}

TOP_KEYS = {
    "schema_version",
    "manifest_id",
    "freeze_status",
    "design",
    "source",
    "derivation_rule",
    "arms",
    "entries",
    "blocks",
    "families",
    "contrasts",
}
DESIGN_KEYS = {
    "design_id",
    "analysis_type",
    "null_alias",
    "unit_of_analysis",
    "difference_orientation",
    "sampling_plan",
    "randomization",
}
SAMPLING_KEYS = {
    "design",
    "planned_n_blocks",
    "freeze_basis",
    "allowed_replacement_reasons",
}
SOURCE_KEYS = {
    "generator",
    "calibration_plan",
    "root_order_manifest",
    "stage_order_manifests",
    "condition_families",
    "authenticated_verdict_basis",
}
FILE_REF_KEYS = {"path", "sha256"}
PLAN_REF_KEYS = {"path", "sha256", "plan_id"}
STAGE_REF_KEYS = {"stage_id", "path", "sha256"}
FAMILY_REF_KEYS = {
    "arm_id",
    "path",
    "file_sha256",
    "condition_family_sha256",
}
VERDICT_KEYS = {"status", "evaluation_basis_sha256"}
DERIVATION_KEYS = {
    "rule_id",
    "run_id_pattern",
    "block_id_template",
    "position_order",
    "exact_cover",
    "contiguous_block_numbers",
}
CONTIGUOUS_KEYS = {"first", "last"}
ARM_KEYS = {
    "arm_id",
    "condition_family_id",
    "condition_family_sha256",
    "model_tag",
    "cell_id",
    "realized_stack_identity",
}
ENTRY_KEYS = {
    "entry_id",
    "config",
    "config_sha256",
    "run_id",
    "model_tag",
    "role",
    "arm_id",
    "condition_id",
    "cell_id",
    "block_id",
    "block_number",
    "position",
    "order_index",
}
BLOCK_KEYS = {"block_id", "block_number", "position_entry_ids"}
FAMILY_KEYS = {
    "family_id",
    "family_instance_id",
    "plan_id",
    "claim_role",
    "metric_tag",
    "multiplicity",
    "contrast_ids",
}
MULTIPLICITY_KEYS = {"method", "alpha", "q", "m"}
CONTRAST_KEYS = {
    "contrast_id",
    "plan_id",
    "family_instance_id",
    "claim_role",
    "metric",
    "estimator",
    "condition_a_id",
    "condition_b_id",
    "cell_a_id",
    "cell_b_id",
    "block_ids",
    "sidedness",
    "hypothesized_direction",
    "equivalence",
    "mde",
    "floor_selector",
}
METRIC_KEYS = {"name", "metric_tag", "window_class", "unit", "ratio_estimand"}
FLOOR_SELECTOR_KEYS = {
    "backend",
    "metric",
    "window_class",
    "condition_family_ids",
    "floor_field",
    "transport_rule_id",
    "claim_floor_rule",
}


class AnalysisManifestV3Error(ValueError):
    """Raised when a v3 manifest cannot be built or rendered."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def calculate_manifest_id(value: Mapping[str, Any]) -> str:
    body = dict(value)
    body.pop("manifest_id", None)
    return "am-" + hashlib.sha256(canonical_json_bytes(body)).hexdigest()


def render_manifest(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    ).encode("utf-8")


def _exact_keys(value: Any, expected: set[str], where: str, errors: list[str]) -> bool:
    if not isinstance(value, Mapping):
        errors.append(f"{where}: must be an object")
        return False
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        errors.append(f"{where}: missing key(s): {', '.join(missing)}")
    if extra:
        errors.append(f"{where}: unrecognized key(s): {', '.join(extra)}")
    return not missing and not extra


def _read_object(path: Path) -> tuple[Mapping[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AnalysisManifestV3Error(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(value, Mapping):
        raise AnalysisManifestV3Error(f"{path}: top level must be an object")
    return value, raw


def _source_refs() -> dict[str, Any]:
    return {
        "generator": "configs/campaigns/splitwise_decode_v1/generate_configs.py",
        "calibration_plan": {
            "path": "calibration_plan.json",
            "sha256": CALIBRATION_PLAN_SHA256,
            "plan_id": PLAN_ID,
        },
        "root_order_manifest": {
            "path": "order_manifest.json",
            "sha256": ROOT_ORDER_SHA256,
        },
        "stage_order_manifests": [
            {
                "stage_id": stage_id,
                "path": f"{stage_id}/order_manifest.json",
                "sha256": digest,
            }
            for stage_id, digest in STAGE_ORDER_SHA256S.items()
        ],
        "condition_families": [
            {
                "arm_id": arm_id,
                "path": freeze["condition_family_path"],
                "file_sha256": freeze["condition_family_file_sha256"],
                "condition_family_sha256": freeze["condition_family_sha256"],
            }
            for arm_id, freeze in ARM_FREEZE.items()
        ],
        "authenticated_verdict_basis": {
            "status": "passed",
            "evaluation_basis_sha256": VERDICT_BASIS_SHA256,
        },
    }


def _arms() -> list[dict[str, Any]]:
    return [
        {
            key: json.loads(json.dumps(freeze[key]))
            for key in (
                "condition_family_id",
                "condition_family_sha256",
                "model_tag",
                "cell_id",
                "realized_stack_identity",
            )
        }
        | {"arm_id": arm_id}
        for arm_id, freeze in ARM_FREEZE.items()
    ]


def _family_and_contrast() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    arm_a = ARM_FREEZE["A"]
    arm_b = ARM_FREEZE["B"]
    block_ids = [f"sw-decode-contrast-b{index:02d}" for index in range(1, 11)]
    family_id = "splitwise-decode-cross-model-primary"
    family_instance_id = "fam-splitwise-decode-cross-model-primary"
    contrast_id = "ctr-sw-decode-qwen25-1p5b-vs-7b"
    family = {
        "family_id": family_id,
        "family_instance_id": family_instance_id,
        "plan_id": PLAN_ID,
        "claim_role": "primary",
        "metric_tag": "phase_decode_energy",
        "multiplicity": {"method": "holm", "alpha": 0.05, "q": None, "m": 1},
        "contrast_ids": [contrast_id],
    }
    contrast = {
        "contrast_id": contrast_id,
        "plan_id": PLAN_ID,
        "family_instance_id": family_instance_id,
        "claim_role": "primary",
        "metric": {
            "name": "phase_energy_j.decode",
            "metric_tag": "phase_decode_energy",
            "window_class": "phase",
            "unit": "J",
            "ratio_estimand": None,
        },
        "estimator": ESTIMATOR_ID,
        "condition_a_id": arm_a["condition_family_id"],
        "condition_b_id": arm_b["condition_family_id"],
        "cell_a_id": arm_a["cell_id"],
        "cell_b_id": arm_b["cell_id"],
        "block_ids": block_ids,
        "sidedness": "two_sided",
        "hypothesized_direction": "positive",
        "equivalence": None,
        "mde": None,
        "floor_selector": {
            "backend": "from_bundle",
            "metric": "phase_energy_j.decode",
            "window_class": "phase",
            "condition_family_ids": [
                arm_a["condition_family_id"],
                arm_b["condition_family_id"],
            ],
            "floor_field": "floor_gate_j",
            "transport_rule_id": EXACT_STACK_RULE_ID,
            "claim_floor_rule": FLOOR_RULE_ID,
        },
    }
    return [family], [contrast]


def build_analysis_manifest_v3(campaign_dir: Path) -> dict[str, Any]:
    """Build v3 solely from the already-frozen campaign bytes."""

    campaign_dir = Path(campaign_dir)
    order, order_raw = _read_object(campaign_dir / "order_manifest.json")
    if hashlib.sha256(order_raw).hexdigest() != ROOT_ORDER_SHA256:
        raise AnalysisManifestV3Error("root order-manifest bytes differ from the ratified pin")
    rows = order.get("executed_order")
    if not isinstance(rows, list) or len(rows) != 40:
        raise AnalysisManifestV3Error("root order manifest must contain exactly 40 entries")

    entries: list[dict[str, Any]] = []
    position_ids: dict[int, dict[str, str]] = {}
    for order_index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            raise AnalysisManifestV3Error("order-manifest entries must be objects")
        run_id = row.get("run_id")
        match = RUN_ID_RE.fullmatch(run_id) if isinstance(run_id, str) else None
        if match is None:
            raise AnalysisManifestV3Error(f"invalid governed run id: {run_id!r}")
        block_number = int(match.group("block"))
        position = match.group("position").upper()
        arm_id = POSITION_ARMS[position]
        freeze = ARM_FREEZE[arm_id]
        config = row.get("config")
        if not isinstance(config, str):
            raise AnalysisManifestV3Error(f"{run_id}: config path is invalid")
        try:
            config_raw = (campaign_dir / config).read_bytes()
        except OSError as exc:
            raise AnalysisManifestV3Error(f"cannot read config {config}: {exc}") from exc
        entry_id = f"entry-{run_id}"
        entries.append(
            {
                "entry_id": entry_id,
                "config": config,
                "config_sha256": hashlib.sha256(config_raw).hexdigest(),
                "run_id": run_id,
                "model_tag": freeze["model_tag"],
                "role": "condition",
                "arm_id": arm_id,
                "condition_id": freeze["condition_family_id"],
                "cell_id": freeze["cell_id"],
                "block_id": f"sw-decode-contrast-b{block_number:02d}",
                "block_number": block_number,
                "position": position,
                "order_index": order_index,
            }
        )
        position_ids.setdefault(block_number, {})[position] = entry_id

    blocks = [
        {
            "block_id": f"sw-decode-contrast-b{block_number:02d}",
            "block_number": block_number,
            "position_entry_ids": {
                position: position_ids[block_number][position]
                for position in POSITION_ORDER
            },
        }
        for block_number in range(1, PLANNED_N_BLOCKS + 1)
    ]
    families, contrasts = _family_and_contrast()
    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": "",
        "freeze_status": "frozen",
        "design": {
            "design_id": "splitwise_decode_cross_model_abba_v1",
            "analysis_type": "comparative_contrast",
            "null_alias": False,
            "unit_of_analysis": "abba_block_arm_mean_difference",
            "difference_orientation": "condition_b_minus_condition_a",
            "sampling_plan": {
                "design": "fixed_n",
                "planned_n_blocks": PLANNED_N_BLOCKS,
                "freeze_basis": "frozen_before_measurement",
                "allowed_replacement_reasons": [
                    "bundle_incomplete",
                    "run_failed",
                    "strict_invalid",
                    "unsupported_before_measurement",
                ],
            },
            "randomization": {
                "scheme": "deterministic_abba",
                "exchangeability": "none",
                "seed": None,
            },
        },
        "source": _source_refs(),
        "derivation_rule": {
            "rule_id": "swdec_contrast_run_id_to_abba_block.v1",
            "run_id_pattern": RUN_ID_RE.pattern,
            "block_id_template": "sw-decode-contrast-bNN",
            "position_order": list(POSITION_ORDER),
            "exact_cover": True,
            "contiguous_block_numbers": {"first": 1, "last": 10},
        },
        "arms": _arms(),
        "entries": entries,
        "blocks": blocks,
        "families": families,
        "contrasts": contrasts,
    }
    manifest["manifest_id"] = calculate_manifest_id(manifest)
    errors = validate_analysis_manifest_v3(manifest, manifest_dir=campaign_dir)
    if errors:
        raise AnalysisManifestV3Error(
            "built analysis manifest v3 is invalid: " + "; ".join(errors)
        )
    return manifest


def _validate_file_ref(
    value: Any,
    expected: Mapping[str, Any],
    where: str,
    errors: list[str],
    *,
    manifest_dir: Path | None,
    keyset: set[str] = FILE_REF_KEYS,
) -> None:
    if not _exact_keys(value, keyset, where, errors):
        return
    assert isinstance(value, Mapping)
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append(f"{where}.{key}: differs from ratified freeze")
    path_text = value.get("path")
    if manifest_dir is not None and isinstance(path_text, str):
        path = manifest_dir / path_text
        try:
            raw = path.read_bytes()
        except OSError as exc:
            errors.append(f"{where}.path: cannot read source: {exc}")
        else:
            expected_sha = value.get("sha256", value.get("file_sha256"))
            if hashlib.sha256(raw).hexdigest() != expected_sha:
                errors.append(f"{where}: source byte hash mismatch")


def normalized_realized_stack_identity(value: Any) -> Mapping[str, Any] | None:
    """Normalize the v3 file/file-set digest spelling for evidence matching."""

    if not isinstance(value, Mapping):
        return None
    result = json.loads(json.dumps(value))
    artifact = result.get("model_artifact")
    if not isinstance(artifact, dict):
        return None
    digest = artifact.get("folded_sha256") or artifact.get("sha256")
    kind = artifact.get("kind")
    if (
        kind not in {"file", "file_set"}
        or artifact.get("algorithm") != "sha256"
        or not isinstance(digest, str)
        or SHA_RE.fullmatch(digest) is None
    ):
        return None
    artifact.pop("sha256", None)
    artifact.pop("folded_sha256", None)
    artifact["digest_sha256"] = digest
    return result


def validate_analysis_manifest_v3(
    value: Mapping[str, Any],
    *,
    manifest_dir: Path | None = None,
) -> list[str]:
    """Return structural, source-linkage, and frozen-semantics errors."""

    errors: list[str] = []
    if not _exact_keys(value, TOP_KEYS, "manifest", errors):
        return errors
    if value.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"manifest.schema_version: expected {SCHEMA_VERSION!r}")
    if value.get("freeze_status") != "frozen":
        errors.append("manifest.freeze_status: must be 'frozen'")
    manifest_id = value.get("manifest_id")
    if not isinstance(manifest_id, str) or MANIFEST_ID_RE.fullmatch(manifest_id) is None:
        errors.append("manifest.manifest_id: invalid")
    else:
        try:
            expected_id = calculate_manifest_id(value)
        except (TypeError, ValueError) as exc:
            errors.append(f"manifest: not canonical JSON: {exc}")
        else:
            if manifest_id != expected_id:
                errors.append("manifest.manifest_id: canonical identity mismatch")

    design = value.get("design")
    if _exact_keys(design, DESIGN_KEYS, "manifest.design", errors):
        assert isinstance(design, Mapping)
        expected = {
            "design_id": "splitwise_decode_cross_model_abba_v1",
            "analysis_type": "comparative_contrast",
            "null_alias": False,
            "unit_of_analysis": "abba_block_arm_mean_difference",
            "difference_orientation": "condition_b_minus_condition_a",
            "randomization": {
                "scheme": "deterministic_abba",
                "exchangeability": "none",
                "seed": None,
            },
        }
        for key, expected_value in expected.items():
            if design.get(key) != expected_value:
                errors.append(f"manifest.design.{key}: differs from ratified freeze")
        sampling = design.get("sampling_plan")
        if _exact_keys(sampling, SAMPLING_KEYS, "manifest.design.sampling_plan", errors):
            expected_sampling = {
                "design": "fixed_n",
                "planned_n_blocks": 10,
                "freeze_basis": "frozen_before_measurement",
                "allowed_replacement_reasons": [
                    "bundle_incomplete",
                    "run_failed",
                    "strict_invalid",
                    "unsupported_before_measurement",
                ],
            }
            if sampling != expected_sampling:
                errors.append("manifest.design.sampling_plan: differs from ratified freeze")

    source = value.get("source")
    expected_source = _source_refs()
    if _exact_keys(source, SOURCE_KEYS, "manifest.source", errors):
        assert isinstance(source, Mapping)
        if source.get("generator") != expected_source["generator"]:
            errors.append("manifest.source.generator: invalid")
        _validate_file_ref(
            source.get("calibration_plan"),
            expected_source["calibration_plan"],
            "manifest.source.calibration_plan",
            errors,
            manifest_dir=manifest_dir,
            keyset=PLAN_REF_KEYS,
        )
        _validate_file_ref(
            source.get("root_order_manifest"),
            expected_source["root_order_manifest"],
            "manifest.source.root_order_manifest",
            errors,
            manifest_dir=manifest_dir,
        )
        stages = source.get("stage_order_manifests")
        if not isinstance(stages, list) or len(stages) != 2:
            errors.append("manifest.source.stage_order_manifests: expected two stages")
        else:
            for index, expected_ref in enumerate(expected_source["stage_order_manifests"]):
                _validate_file_ref(
                    stages[index],
                    expected_ref,
                    f"manifest.source.stage_order_manifests[{index}]",
                    errors,
                    manifest_dir=manifest_dir,
                    keyset=STAGE_REF_KEYS,
                )
        family_refs = source.get("condition_families")
        if not isinstance(family_refs, list) or len(family_refs) != 2:
            errors.append("manifest.source.condition_families: expected two arm definitions")
        else:
            for index, expected_ref in enumerate(expected_source["condition_families"]):
                ref = family_refs[index]
                if _exact_keys(
                    ref,
                    FAMILY_REF_KEYS,
                    f"manifest.source.condition_families[{index}]",
                    errors,
                ):
                    if ref != expected_ref:
                        errors.append(
                            f"manifest.source.condition_families[{index}]: differs from ratified freeze"
                        )
                    if manifest_dir is not None:
                        try:
                            raw = (manifest_dir / ref["path"]).read_bytes()
                        except OSError as exc:
                            errors.append(
                                f"manifest.source.condition_families[{index}].path: {exc}"
                            )
                        else:
                            if hashlib.sha256(raw).hexdigest() != ref["file_sha256"]:
                                errors.append(
                                    f"manifest.source.condition_families[{index}]: source byte hash mismatch"
                                )
        verdict = source.get("authenticated_verdict_basis")
        if _exact_keys(verdict, VERDICT_KEYS, "manifest.source.authenticated_verdict_basis", errors):
            if verdict != expected_source["authenticated_verdict_basis"]:
                errors.append("manifest.source.authenticated_verdict_basis: invalid PASSED basis")

    derivation = value.get("derivation_rule")
    if _exact_keys(derivation, DERIVATION_KEYS, "manifest.derivation_rule", errors):
        expected_derivation = {
            "rule_id": "swdec_contrast_run_id_to_abba_block.v1",
            "run_id_pattern": RUN_ID_RE.pattern,
            "block_id_template": "sw-decode-contrast-bNN",
            "position_order": list(POSITION_ORDER),
            "exact_cover": True,
            "contiguous_block_numbers": {"first": 1, "last": 10},
        }
        if derivation != expected_derivation:
            errors.append("manifest.derivation_rule: differs from governed exact-cover rule")
        contiguous = derivation.get("contiguous_block_numbers") if isinstance(derivation, Mapping) else None
        _exact_keys(contiguous, CONTIGUOUS_KEYS, "manifest.derivation_rule.contiguous_block_numbers", errors)

    arms = value.get("arms")
    arm_by_id: dict[str, Mapping[str, Any]] = {}
    if not isinstance(arms, list) or len(arms) != 2:
        errors.append("manifest.arms: must contain exactly A and B")
    else:
        for index, arm in enumerate(arms):
            where = f"manifest.arms[{index}]"
            if not _exact_keys(arm, ARM_KEYS, where, errors):
                continue
            arm_id = arm.get("arm_id")
            if arm_id not in ARM_FREEZE or arm_id in arm_by_id:
                errors.append(f"{where}.arm_id: invalid or duplicate")
                continue
            arm_by_id[str(arm_id)] = arm
            freeze = ARM_FREEZE[str(arm_id)]
            expected_arm = {
                key: freeze[key]
                for key in (
                    "condition_family_id",
                    "condition_family_sha256",
                    "model_tag",
                    "cell_id",
                    "realized_stack_identity",
                )
            } | {"arm_id": arm_id}
            if arm != expected_arm:
                errors.append(f"{where}: differs from ratified arm identity")
            if normalized_realized_stack_identity(arm.get("realized_stack_identity")) is None:
                errors.append(f"{where}.realized_stack_identity: invalid artifact identity")

    entries = value.get("entries")
    entry_by_id: dict[str, Mapping[str, Any]] = {}
    entry_positions: dict[tuple[int, str], str] = {}
    consumed_order_rows: list[Mapping[str, Any]] = []
    if manifest_dir is not None:
        try:
            root_order, _ = _read_object(manifest_dir / "order_manifest.json")
            raw_rows = root_order.get("executed_order")
            if isinstance(raw_rows, list) and all(isinstance(row, Mapping) for row in raw_rows):
                consumed_order_rows = list(raw_rows)
        except AnalysisManifestV3Error as exc:
            errors.append(str(exc))
    if not isinstance(entries, list) or len(entries) != 40:
        errors.append("manifest.entries: must contain exactly 40 governed positions")
        entries = []
    for index, entry in enumerate(entries):
        where = f"manifest.entries[{index}]"
        if not _exact_keys(entry, ENTRY_KEYS, where, errors):
            continue
        assert isinstance(entry, Mapping)
        entry_id = entry.get("entry_id")
        run_id = entry.get("run_id")
        match = RUN_ID_RE.fullmatch(run_id) if isinstance(run_id, str) else None
        if not isinstance(entry_id, str) or not entry_id or entry_id in entry_by_id:
            errors.append(f"{where}.entry_id: invalid or duplicate")
            continue
        entry_by_id[entry_id] = entry
        if match is None:
            errors.append(f"{where}.run_id: violates governed derivation pattern")
            continue
        block_number = int(match.group("block"))
        position = match.group("position").upper()
        arm_id = POSITION_ARMS[position]
        freeze = ARM_FREEZE[arm_id]
        expected_semantics = {
            "entry_id": f"entry-{run_id}",
            "model_tag": freeze["model_tag"],
            "role": "condition",
            "arm_id": arm_id,
            "condition_id": freeze["condition_family_id"],
            "cell_id": freeze["cell_id"],
            "block_id": f"sw-decode-contrast-b{block_number:02d}",
            "block_number": block_number,
            "position": position,
            "order_index": index + 1,
        }
        for key, expected_value in expected_semantics.items():
            if entry.get(key) != expected_value:
                errors.append(f"{where}.{key}: disagrees with governed derivation")
        position_key = (block_number, position)
        if position_key in entry_positions:
            errors.append(f"{where}: duplicate physical ABBA position")
        entry_positions[position_key] = entry_id
        config = entry.get("config")
        digest = entry.get("config_sha256")
        if not isinstance(config, str) or not config or Path(config).is_absolute() or ".." in Path(config).parts:
            errors.append(f"{where}.config: must be a safe relative path")
        elif manifest_dir is not None:
            try:
                raw = (manifest_dir / config).read_bytes()
            except OSError as exc:
                errors.append(f"{where}.config: cannot read: {exc}")
            else:
                if not isinstance(digest, str) or hashlib.sha256(raw).hexdigest() != digest:
                    errors.append(f"{where}.config_sha256: source byte hash mismatch")
        if consumed_order_rows and index < len(consumed_order_rows):
            order_row = consumed_order_rows[index]
            for entry_key, order_key in (
                ("run_id", "run_id"),
                ("config", "config"),
                ("model_tag", "model_tag"),
                ("block_number", "block_index"),
                ("order_index", "index"),
            ):
                if entry.get(entry_key) != order_row.get(order_key):
                    errors.append(f"{where}.{entry_key}: disagrees with root order manifest")
            if entry.get("position") in POSITION_ORDER:
                expected_position = POSITION_ORDER.index(str(entry["position"])) + 1
                if order_row.get("position_in_block") != expected_position:
                    errors.append(f"{where}.position: disagrees with root order manifest")

    expected_position_keys = {
        (block, position)
        for block in range(1, PLANNED_N_BLOCKS + 1)
        for position in POSITION_ORDER
    }
    if set(entry_positions) != expected_position_keys:
        errors.append("manifest.entries: positions must exactly cover contiguous blocks 01..10")

    blocks = value.get("blocks")
    consumed_entry_ids: list[str] = []
    if not isinstance(blocks, list) or len(blocks) != PLANNED_N_BLOCKS:
        errors.append("manifest.blocks: must contain exactly ten contiguous blocks")
        blocks = []
    for index, block in enumerate(blocks, start=1):
        where = f"manifest.blocks[{index - 1}]"
        if not _exact_keys(block, BLOCK_KEYS, where, errors):
            continue
        assert isinstance(block, Mapping)
        if block.get("block_number") != index or block.get("block_id") != f"sw-decode-contrast-b{index:02d}":
            errors.append(f"{where}: block identity is not contiguous")
        positions = block.get("position_entry_ids")
        if not _exact_keys(positions, set(POSITION_ORDER), f"{where}.position_entry_ids", errors):
            continue
        assert isinstance(positions, Mapping)
        for position in POSITION_ORDER:
            entry_id = positions.get(position)
            consumed_entry_ids.append(str(entry_id))
            if entry_id != entry_positions.get((index, position)):
                errors.append(f"{where}.position_entry_ids.{position}: wrong entry")
    if len(consumed_entry_ids) != len(set(consumed_entry_ids)) or set(consumed_entry_ids) != set(entry_by_id):
        errors.append("manifest.blocks: every position entry must be consumed exactly once")

    expected_families, expected_contrasts = _family_and_contrast()
    families = value.get("families")
    if families != expected_families:
        errors.append("manifest.families: must be the frozen Holm alpha=0.05 m=1 family")
    elif isinstance(families, list) and families:
        family = families[0]
        _exact_keys(family, FAMILY_KEYS, "manifest.families[0]", errors)
        if isinstance(family, Mapping):
            _exact_keys(family.get("multiplicity"), MULTIPLICITY_KEYS, "manifest.families[0].multiplicity", errors)
    contrasts = value.get("contrasts")
    if contrasts != expected_contrasts:
        errors.append("manifest.contrasts: differs from ratified v3 contrast")
    elif isinstance(contrasts, list) and contrasts:
        contrast = contrasts[0]
        _exact_keys(contrast, CONTRAST_KEYS, "manifest.contrasts[0]", errors)
        if isinstance(contrast, Mapping):
            _exact_keys(contrast.get("metric"), METRIC_KEYS, "manifest.contrasts[0].metric", errors)
            _exact_keys(
                contrast.get("floor_selector"),
                FLOOR_SELECTOR_KEYS,
                "manifest.contrasts[0].floor_selector",
                errors,
            )
    return errors


def write_manifest_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        "wb", dir=path.parent, prefix=f".{path.name}.", delete=False
    )
    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(render_manifest(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise


__all__ = [
    "ARM_FREEZE",
    "AnalysisManifestV3Error",
    "CALIBRATION_PLAN_SHA256",
    "ESTIMATOR_ID",
    "EXACT_STACK_RULE_ID",
    "FLOOR_RULE_ID",
    "MANIFEST_NAME",
    "PLANNED_N_BLOCKS",
    "SCHEMA_VERSION",
    "STAGE_ORDER_SHA256S",
    "VERDICT_BASIS_SHA256",
    "build_analysis_manifest_v3",
    "calculate_manifest_id",
    "canonical_json_bytes",
    "normalized_realized_stack_identity",
    "render_manifest",
    "validate_analysis_manifest_v3",
    "write_manifest_atomic",
]
