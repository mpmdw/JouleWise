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
import math
import os
import re
import stat
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any, Mapping


SCHEMA_VERSION = "joulewise.analysis_manifest.v3"
PROSPECTIVE_SCHEMA_VERSION = "joulewise.analysis_manifest.v3.prospective"
FINALIZED_SCHEMA_VERSION = "joulewise.analysis_manifest.v3.finalized"
SEMANTICS_PROJECTION_RULE_ID = "joulewise.analysis_semantics_projection.v1"
FINALIZATION_CONTRACT_ID = "joulewise.analysis_manifest_finalization.v1"
FINALIZED_NAMESPACE_RULE_ID = "prospective_manifest_id_filename.v1"
FINALIZED_BASENAME_SUFFIX = ".finalized.json"
MANIFEST_NAME = "analysis_manifest_v3.json"
PLAN_ID = "splitwise-decode-v1-m3max-qwen25-1p5b-vs-7b"
PLANNED_N_BLOCKS = 10
ESTIMATOR_ID = "abba_block_arm_mean_difference_t_v1"
FLOOR_RULE_ID = "cross_stack_armwise_max.v1"
EXACT_STACK_RULE_ID = "exact_stack_only.v1"
GOVERNED_TRANSPORT_RULE_ID = "same_stack_componentwise_worst_case.v1"
TRANSPORT_RULING_PENDING_REFUSAL = (
    "analysis_manifest_transport_ruling_pending"
)
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


PROSPECTIVE_MALFORMED_VALUE_CODE = "analysis_prospective_schema_invalid"
PROSPECTIVE_INTERNAL_ERROR_CODE = "analysis_prospective_internal_error"
FINALIZED_MALFORMED_VALUE_CODE = "analysis_manifest_finalized_invalid"
FINALIZED_INTERNAL_ERROR_CODE = "analysis_manifest_internal_error"

PROSPECTIVE_REFUSAL_CODES = frozenset(
    {
        PROSPECTIVE_MALFORMED_VALUE_CODE,
        PROSPECTIVE_INTERNAL_ERROR_CODE,
        "analysis_prospective_unknown_key",
        "analysis_prospective_not_frozen",
        "analysis_prospective_identity_mismatch",
        "analysis_prospective_plan_tree_mismatch",
        "analysis_prospective_source_hash_mismatch",
        "analysis_prospective_unsafe_path",
        "analysis_prospective_member_cover_mismatch",
        "analysis_prospective_block_cover_mismatch",
        "analysis_prospective_contrast_cover_mismatch",
        "analysis_prospective_family_invalid",
        "analysis_prospective_multiplicity_invalid",
        "analysis_prospective_floor_dependency_unresolved",
        "analysis_prospective_unresolved_slot",
    }
)
_PROSPECTIVE_PREFILL_ARMS = frozenset(
    {"prefill_p256", "prefill_p512", "prefill_p1024", "prefill_p2048"}
)
FINALIZED_REFUSAL_CODES = frozenset(
    {
        FINALIZED_MALFORMED_VALUE_CODE,
        FINALIZED_INTERNAL_ERROR_CODE,
        "analysis_manifest_lineage_mismatch",
        "analysis_manifest_collection_identity_mismatch",
        "analysis_manifest_floor_attachment_mismatch",
        "analysis_manifest_family_semantics_mismatch",
    }
)


class _ManifestInputWalkError(ValueError):
    """A wrong Python container/value encountered in an input-only walk."""

    def __init__(self, path: str, expected: str, value: object) -> None:
        self.path = path
        self.expected = expected
        self.observed_type = type(value).__name__
        super().__init__(
            f"{path}: expected {expected}, got {self.observed_type}"
        )


@dataclass(frozen=True)
class ManifestRefusal:
    """One closed-vocabulary refusal at the prospective/finalized edge."""

    reason_code: str
    detail: str
    cause: BaseException | None = field(default=None, compare=False, repr=False)


class AnalysisManifestFinalizationError(AnalysisManifestV3Error):
    """Raised when deterministic postcollection finalization refuses."""

    def __init__(self, reason_code: str, detail: str) -> None:
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}")


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


# The prospective/finalized sibling is deliberately separate from the
# historical Splitwise v3 contract above.  The historical constants and
# builder remain frozen; these key sets own only the D-117 consumption edge.
_PROSPECTIVE_TOP_KEYS = {
    "schema_version",
    "manifest_id",
    "freeze_status",
    "plan",
    "root_order_manifest",
    "stage_manifests",
    "evidence_root_id",
    "condition_families",
    "design",
    "replacement_policy",
    "families",
    "contrasts",
    "finalization_contract",
    "frozen_semantics_sha256",
}
_PROSPECTIVE_PLAN_KEYS = {"plan_id", "path", "sha256"}
_PROSPECTIVE_ROOT_ORDER_KEYS = {"path", "manifest_id", "sha256"}
_PROSPECTIVE_STAGE_KEYS = {
    "index",
    "subcampaign_id",
    "role",
    "optional",
    "planned_n_bundles",
    "manifest_path",
    "manifest_id",
    "manifest_sha256",
    "successor_stage_id",
}
_PROSPECTIVE_CONDITION_KEYS = {
    "measurement_arm",
    "arm",
    "path",
    "sha256",
    "condition_family_id",
    "canonical_domain_sha256",
}
_REPLACEMENT_POLICY_KEYS = {
    "outcome_dependent_top_up",
    "science_member_replacements",
    "allowed_replacement_reasons",
}
_PROSPECTIVE_CONTRAST_KEYS = {
    "contrast_id",
    "measurement_arm",
    "metric",
    "metric_tag",
    "target_precheck_path",
    "condition_a_id",
    "condition_b_id",
    "difference_orientation",
    "point_estimator",
    "floor_estimator_registration",
    "block_ids",
    "members",
    "family_instance_id",
    "claim_role",
    "test",
    "scientific_hypothesis_direction",
    "equivalence",
    "mde",
    "floor_dependency",
    "prompt",
}
_PROSPECTIVE_MEMBER_KEYS = {
    "run_id",
    "config",
    "config_sha256",
    "arm",
    "block_id",
    "block_number",
    "position",
    "order_index",
}
_FLOOR_DEPENDENCY_KEYS = {
    "required_artifact_schema",
    "floor_selector",
    "transport",
}
_TRANSPORT_KEYS = {"mode", "rule_id", "transport_groups"}
_TRANSPORT_GROUP_BINDING_KEYS = {
    "transport_group_id",
    "condition_family_id",
    "condition_domain_sha256",
    "group_rule_id",
}
_PROMPT_KEYS = {"path", "sha256", "status"}
_FINALIZATION_CONTRACT_KEYS = {
    "contract_id",
    "projection_rule_id",
    "namespace_rule_id",
    "output_basename_suffix",
    "required_attachments",
}
_ATTACHMENT_DECLARATION_KEYS = {"role", "schema_version"}
_REQUIRED_ATTACHMENT_ROLES = {
    "whole_window_verdict",
    "bracket_binding",
    "calibration_ledger",
    "aggregate_floor_artifact",
}
_FINALIZED_TOP_KEYS = {
    "schema_version",
    "manifest_id",
    "freeze_status",
    "lineage",
    "condition_families",
    "design",
    "replacement_policy",
    "arms",
    "entries",
    "blocks",
    "families",
    "contrasts",
    "finalization_contract",
    "evidence",
}
_FINALIZED_LINEAGE_KEYS = {
    "prospective_manifest_id",
    "prospective_manifest_path",
    "prospective_manifest_sha256",
    "plan_tree_path",
    "plan_tree_sha256",
    "collection_manifest_id",
    "projection_rule_id",
    "prospective_semantics_sha256",
    "finalized_semantics_sha256",
}
_FINALIZED_EVIDENCE_KEYS = {
    "whole_window_verdict",
    "bracket_binding",
    "calibration_ledger",
    "aggregate_floor_artifact",
}
_FINALIZED_WHOLE_WINDOW_KEYS = {
    "path",
    "sha256",
    "schema_version",
    "status",
    "evaluation_basis_sha256",
}
_FINALIZED_BRACKET_KEYS = {
    "path",
    "sha256",
    "schema_version",
    "binding_digest",
    "session_id",
}
_FINALIZED_LEDGER_KEYS = {
    "path",
    "sha256",
    "schema_version",
    "terminal_head",
}
_FINALIZED_FLOOR_KEYS = {
    "path",
    "sha256",
    "schema_version",
    "artifact_id",
}
_FINALIZED_CONTRAST_KEYS = {
    *CONTRAST_KEYS,
    "measurement_arm",
    "target_precheck_path",
    "difference_orientation",
    "floor_estimator_registration",
    "floor_dependency",
    "prompt",
}
_FINALIZED_ENTRY_KEYS = {*ENTRY_KEYS, "bundle_path"}
_WHOLE_WINDOW_SCHEMA = "joulewise.idle_admission_whole_window_verdict.v1"
_WHOLE_WINDOW_BASIS_SCHEMA = "joulewise.idle_admission_evaluation_basis.v1"
_WHOLE_WINDOW_OCCURRENCE_KEYS = {
    "bundle_id",
    "bundle_path",
    "config_sha256",
    "metadata_sha256",
    "summary_sha256",
}
_BRACKET_BINDING_SCHEMA = "joulewise.calibration_bracket_binding.v1"
_LEDGER_SCHEMA = "joulewise.calibration_observation_ledger.v1"
_FLOOR_SCHEMA = "joulewise.detection_floor_artifact.v2"


def is_abba_v3_consumable_schema(value: object) -> bool:
    """Return whether ``value`` selects either consumer-shaped ABBA v3 wire."""

    return value in {SCHEMA_VERSION, FINALIZED_SCHEMA_VERSION}


def frozen_family_block_strata(
    value: Mapping[str, Any], family_instance_id: str
) -> tuple[tuple[int, dict[str, str]], ...]:
    """Return the manifest-frozen block-number mapping for one family.

    Different measurement arms deliberately use different block IDs.  A
    multi-contrast LOO therefore cannot borrow the first contrast's IDs; its
    shared omission unit is the block number frozen in the manifest.  This
    helper is strict so callers can refuse instead of silently suppressing
    sensitivity evidence when that cross-arm mapping is absent or ambiguous.
    """

    families = value.get("families")
    contrasts = value.get("contrasts")
    blocks = value.get("blocks")
    if not all(isinstance(rows, list) for rows in (families, contrasts, blocks)):
        raise AnalysisManifestV3Error("frozen family block strata are absent")
    matching_families = [
        row
        for row in families
        if isinstance(row, Mapping)
        and row.get("family_instance_id") == family_instance_id
    ]
    if len(matching_families) != 1:
        raise AnalysisManifestV3Error("frozen family identity is absent or ambiguous")
    contrast_ids = matching_families[0].get("contrast_ids")
    if (
        not isinstance(contrast_ids, list)
        or not contrast_ids
        or any(not isinstance(contrast_id, str) for contrast_id in contrast_ids)
        or len(contrast_ids) != len(set(contrast_ids))
    ):
        raise AnalysisManifestV3Error("frozen family contrast membership is invalid")

    contrast_by_id: dict[str, Mapping[str, Any]] = {}
    for contrast in contrasts:
        if not isinstance(contrast, Mapping):
            continue
        contrast_id = contrast.get("contrast_id")
        if isinstance(contrast_id, str) and contrast_id not in contrast_by_id:
            contrast_by_id[contrast_id] = contrast
        elif isinstance(contrast_id, str):
            raise AnalysisManifestV3Error("frozen contrast identity is ambiguous")
    if any(contrast_id not in contrast_by_id for contrast_id in contrast_ids):
        raise AnalysisManifestV3Error("frozen family names an absent contrast")

    block_number_by_id: dict[str, int] = {}
    for block in blocks:
        if not isinstance(block, Mapping):
            continue
        block_id = block.get("block_id")
        block_number = block.get("block_number")
        if (
            not isinstance(block_id, str)
            or not block_id
            or isinstance(block_number, bool)
            or not isinstance(block_number, int)
        ):
            raise AnalysisManifestV3Error("frozen block stratum is invalid")
        if block_id in block_number_by_id:
            raise AnalysisManifestV3Error("frozen block identity is ambiguous")
        block_number_by_id[block_id] = block_number

    design = value.get("design")
    sampling = design.get("sampling_plan") if isinstance(design, Mapping) else None
    planned_n = (
        sampling.get("planned_n_blocks")
        if isinstance(sampling, Mapping)
        else None
    )
    if isinstance(planned_n, bool) or not isinstance(planned_n, int) or planned_n < 1:
        raise AnalysisManifestV3Error("frozen planned block count is invalid")
    expected_numbers = list(range(1, planned_n + 1))

    block_ids_by_number: dict[str, dict[int, str]] = {}
    for contrast_id in contrast_ids:
        block_ids = contrast_by_id[contrast_id].get("block_ids")
        if (
            not isinstance(block_ids, list)
            or len(block_ids) != planned_n
            or len(block_ids) != len(set(block_ids))
            or any(not isinstance(block_id, str) for block_id in block_ids)
        ):
            raise AnalysisManifestV3Error(
                f"frozen blocks are incomplete for contrast {contrast_id!r}"
            )
        try:
            mapping = {
                block_number_by_id[block_id]: block_id for block_id in block_ids
            }
        except KeyError as exc:
            raise AnalysisManifestV3Error(
                f"frozen block lacks a stratum for contrast {contrast_id!r}"
            ) from exc
        if sorted(mapping) != expected_numbers or len(mapping) != len(block_ids):
            raise AnalysisManifestV3Error(
                f"frozen strata are not contiguous and unique for contrast {contrast_id!r}"
            )
        block_ids_by_number[contrast_id] = mapping

    return tuple(
        (
            block_number,
            {
                contrast_id: block_ids_by_number[contrast_id][block_number]
                for contrast_id in contrast_ids
            },
        )
        for block_number in expected_numbers
    )


def _strict_json_bytes(raw: bytes, label: str) -> Mapping[str, Any]:
    def object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result

    def nonfinite(value: str) -> None:
        raise ValueError(f"non-finite JSON number {value!r}")

    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=object_pairs,
            parse_constant=nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_input_unreadable", f"{label}: {exc}"
        ) from exc
    if not isinstance(value, Mapping):
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            f"{label}: top level must be an object",
        )
    return value


def _read_strict_object(path: Path, label: str) -> tuple[Mapping[str, Any], bytes]:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_input_unreadable", f"{label}: {exc}"
        ) from exc
    return _strict_json_bytes(raw, label), raw


def _refusal(
    refusals: list[ManifestRefusal], reason_code: str, detail: str
) -> None:
    item = ManifestRefusal(reason_code, detail)
    if item not in refusals:
        refusals.append(item)


def _exact_refusal_keys(
    value: Any,
    expected: set[str],
    where: str,
    refusals: list[ManifestRefusal],
    *,
    schema_code: str,
    unknown_code: str,
) -> bool:
    if not isinstance(value, Mapping):
        _refusal(refusals, schema_code, f"{where}: must be an object")
        return False
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        _refusal(
            refusals,
            schema_code,
            f"{where}: missing key(s): {', '.join(missing)}",
        )
    if extra:
        _refusal(
            refusals,
            unknown_code,
            f"{where}: unrecognized key(s): {', '.join(extra)}",
        )
    return not missing and not extra


def _contains_unresolved_slot(value: Any) -> bool:
    if isinstance(value, str):
        return value == "EMPTY" or value.startswith("TODO(")
    if isinstance(value, Mapping):
        if value.get("status") == "EMPTY":
            return True
        return any(_contains_unresolved_slot(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_unresolved_slot(item) for item in value)
    return False


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and SHA_RE.fullmatch(value) is not None


def _unique_nonempty_strings(value: Any) -> bool:
    return bool(
        isinstance(value, list)
        and value
        and all(isinstance(item, str) and item for item in value)
        and len(value) == len(set(value))
    )


def _safe_relative_file(root: Path, text: Any) -> Path | None:
    if not isinstance(text, str) or not text or "\\" in text:
        return None
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        return None
    root = Path(root).resolve()
    candidate = root.joinpath(*pure.parts)
    current = root
    try:
        for part in pure.parts:
            current = current / part
            if current.is_symlink():
                return None
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    try:
        mode = resolved.stat().st_mode
    except OSError:
        return None
    if root not in resolved.parents or not stat.S_ISREG(mode):
        return None
    return resolved


def _path_under_root(path: Path, root: Path, label: str) -> tuple[Path, str]:
    lexical_root = Path(root).absolute()
    root = lexical_root.resolve(strict=True)
    candidate = Path(path)
    candidate = candidate if candidate.is_absolute() else lexical_root / candidate
    try:
        try:
            relative = candidate.relative_to(lexical_root)
        except ValueError:
            relative = candidate.relative_to(root)
    except ValueError as exc:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            f"{label}: path is outside custody",
        ) from exc
    if any(part in {"", ".", ".."} for part in relative.parts):
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            f"{label}: path is not canonical",
        )
    current = root
    try:
        for part in relative.parts:
            current = current / part
            mode = current.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise AnalysisManifestFinalizationError(
                    "analysis_finalization_attachment_invalid",
                    f"{label}: symlinks are forbidden",
                )
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except FileNotFoundError as exc:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_missing",
            f"{label}: path does not exist",
        ) from exc
    except AnalysisManifestFinalizationError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            f"{label}: path is outside custody or unreadable",
        ) from exc
    if not stat.S_ISREG(resolved.stat().st_mode):
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            f"{label}: must be a regular file",
        )
    return resolved, relative.as_posix()


def _directory_under_root(path: Path, root: Path, label: str) -> Path:
    """Resolve a custody directory without erasing lexical symlink evidence."""

    lexical_root = Path(root).absolute()
    root = lexical_root.resolve(strict=True)
    candidate = Path(path)
    candidate = candidate if candidate.is_absolute() else lexical_root / candidate
    try:
        try:
            relative = candidate.relative_to(lexical_root)
        except ValueError:
            relative = candidate.relative_to(root)
    except ValueError as exc:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            f"{label}: path is outside custody",
        ) from exc
    if any(part in {"", ".", ".."} for part in relative.parts):
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            f"{label}: path is not canonical",
        )
    current = root
    try:
        for part in relative.parts:
            current = current / part
            if stat.S_ISLNK(current.lstat().st_mode):
                raise AnalysisManifestFinalizationError(
                    "analysis_finalization_attachment_invalid",
                    f"{label}: symlinks are forbidden",
                )
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except AnalysisManifestFinalizationError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            f"{label}: path is outside custody or unreadable",
        ) from exc
    if not resolved.is_dir():
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            f"{label}: must be a directory",
        )
    return resolved


def _canonical_sha(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _prospective_semantics(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "projection_rule_id": SEMANTICS_PROJECTION_RULE_ID,
        "design": json.loads(json.dumps(value.get("design"))),
        "replacement_policy": json.loads(
            json.dumps(value.get("replacement_policy"))
        ),
        "condition_families": json.loads(
            json.dumps(value.get("condition_families"))
        ),
        "families": json.loads(json.dumps(value.get("families"))),
        "contrasts": json.loads(json.dumps(value.get("contrasts"))),
        "required_attachments": json.loads(
            json.dumps(
                value.get("finalization_contract", {}).get(
                    "required_attachments"
                )
                if isinstance(value.get("finalization_contract"), Mapping)
                else None
            )
        ),
    }


def _finalized_semantics(value: Mapping[str, Any]) -> dict[str, Any]:
    entries = value.get("entries")
    entries = entries if isinstance(entries, list) else []
    family_by_id = {
        family.get("family_instance_id"): family
        for family in value.get("families", [])
        if isinstance(family, Mapping)
    }
    contrasts: list[dict[str, Any]] = []
    for contrast in value.get("contrasts", []):
        if not isinstance(contrast, Mapping):
            contrasts.append({})
            continue
        metric = contrast.get("metric")
        family = family_by_id.get(contrast.get("family_instance_id"), {})
        block_ids = contrast.get("block_ids")
        member_rows = []
        for entry in entries:
            if not (
                isinstance(entry, Mapping)
                and isinstance(block_ids, list)
                and entry.get("block_id") in block_ids
                and entry.get("condition_id")
                in {
                    contrast.get("condition_a_id"),
                    contrast.get("condition_b_id"),
                }
            ):
                continue
            row = {
                key: entry.get(key)
                for key in _PROSPECTIVE_MEMBER_KEYS
                if key != "arm"
            }
            row["arm"] = POSITION_ARMS.get(entry.get("position"))
            member_rows.append(row)
        member_rows.sort(key=lambda row: int(row.get("order_index", 0)))
        contrasts.append(
            {
                "contrast_id": contrast.get("contrast_id"),
                "measurement_arm": contrast.get("measurement_arm"),
                "metric": metric.get("name") if isinstance(metric, Mapping) else None,
                "metric_tag": (
                    metric.get("metric_tag") if isinstance(metric, Mapping) else None
                ),
                "target_precheck_path": contrast.get("target_precheck_path"),
                "condition_a_id": contrast.get("condition_a_id"),
                "condition_b_id": contrast.get("condition_b_id"),
                "difference_orientation": contrast.get("difference_orientation"),
                "point_estimator": contrast.get("estimator"),
                "floor_estimator_registration": contrast.get(
                    "floor_estimator_registration"
                ),
                "block_ids": contrast.get("block_ids"),
                "members": member_rows,
                "family_instance_id": contrast.get("family_instance_id"),
                "claim_role": contrast.get("claim_role"),
                "test": contrast.get("sidedness"),
                "scientific_hypothesis_direction": contrast.get(
                    "hypothesized_direction"
                ),
                "equivalence": contrast.get("equivalence"),
                "mde": contrast.get("mde"),
                "floor_dependency": contrast.get("floor_dependency"),
                "prompt": contrast.get("prompt"),
            }
        )
    return {
        "projection_rule_id": SEMANTICS_PROJECTION_RULE_ID,
        "design": json.loads(json.dumps(value.get("design"))),
        "replacement_policy": json.loads(
            json.dumps(value.get("replacement_policy"))
        ),
        "condition_families": json.loads(
            json.dumps(value.get("condition_families"))
        ),
        "families": json.loads(json.dumps(value.get("families"))),
        "contrasts": contrasts,
        "required_attachments": json.loads(
            json.dumps(
                value.get("finalization_contract", {}).get(
                    "required_attachments"
                )
                if isinstance(value.get("finalization_contract"), Mapping)
                else None
            )
        ),
    }


def analysis_semantics_projection_v1(value: Mapping[str, Any]) -> dict[str, Any]:
    """Project every field capable of changing an estimand or family result."""

    schema = value.get("schema_version") if isinstance(value, Mapping) else None
    if schema == PROSPECTIVE_SCHEMA_VERSION:
        return _prospective_semantics(value)
    if schema == FINALIZED_SCHEMA_VERSION:
        return _finalized_semantics(value)
    raise AnalysisManifestV3Error(
        f"unsupported schema for semantic projection: {schema!r}"
    )


def analysis_semantics_sha256_v1(value: Mapping[str, Any]) -> str:
    return _canonical_sha(analysis_semantics_projection_v1(value))


def _validate_file_binding(
    value: Mapping[str, Any],
    *,
    path_key: str,
    sha_key: str,
    root: Path,
    where: str,
    refusals: list[ManifestRefusal],
) -> Mapping[str, Any] | None:
    path = _safe_relative_file(root, value.get(path_key))
    if path is None:
        _refusal(
            refusals,
            "analysis_prospective_unsafe_path",
            f"{where}.{path_key}: unsafe, missing, symlinked, or non-regular",
        )
        return None
    try:
        raw = path.read_bytes()
        parsed = _strict_json_bytes(raw, where)
    except (OSError, AnalysisManifestFinalizationError) as exc:
        _refusal(
            refusals,
            "analysis_prospective_source_hash_mismatch",
            f"{where}: source is unreadable: {exc}",
        )
        return None
    if hashlib.sha256(raw).hexdigest() != value.get(sha_key):
        _refusal(
            refusals,
            "analysis_prospective_source_hash_mismatch",
            f"{where}: source byte hash mismatch",
        )
    return parsed if isinstance(parsed, Mapping) else None


_INPUT_MALFORMATION_EXCEPTIONS = (
    TypeError,
    ValueError,
    AttributeError,
    KeyError,
    IndexError,
)


def _wrong_input_type(path: str, expected: str, value: object) -> None:
    cause = TypeError(
        f"{path}: expected {expected}, got {type(value).__name__}"
    )
    raise _ManifestInputWalkError(path, expected, value) from cause


def _walk_json_value(value: object, path: str) -> None:
    """Reject Python-only values before canonicalization/helper regions."""

    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                cause = KeyError(
                    f"{path}: object key has type {type(key).__name__}"
                )
                raise _ManifestInputWalkError(
                    path, "object with string keys", value
                ) from cause
            _walk_json_value(child, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _walk_json_value(child, f"{path}[{index}]")
        return
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float) and math.isfinite(value):
        return
    _wrong_input_type(path, "a finite JSON value", value)


def _input_mapping(value: object, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _wrong_input_type(path, "object", value)
    return value


def _input_list(value: object, path: str) -> list[Any]:
    if not isinstance(value, list):
        _wrong_input_type(path, "array", value)
    return value


def _walk_prospective_input(value: object) -> None:
    """Walk only attacker-controlled prospective container structure."""

    _walk_json_value(value, "manifest")
    manifest = _input_mapping(value, "manifest")
    if set(manifest) != _PROSPECTIVE_TOP_KEYS:
        return
    for key in ("plan", "root_order_manifest", "design", "replacement_policy"):
        _input_mapping(manifest.get(key), f"manifest.{key}")

    design = _input_mapping(manifest.get("design"), "manifest.design")
    _input_mapping(design.get("sampling_plan"), "manifest.design.sampling_plan")

    for key in ("stage_manifests", "condition_families"):
        rows = _input_list(manifest.get(key), f"manifest.{key}")
        for index, row in enumerate(rows):
            _input_mapping(row, f"manifest.{key}[{index}]")

    families = _input_list(manifest.get("families"), "manifest.families")
    for index, family_value in enumerate(families):
        path = f"manifest.families[{index}]"
        family = _input_mapping(family_value, path)
        _input_list(family.get("contrast_ids"), f"{path}.contrast_ids")
        _input_mapping(family.get("multiplicity"), f"{path}.multiplicity")

    contrasts = _input_list(manifest.get("contrasts"), "manifest.contrasts")
    for index, contrast_value in enumerate(contrasts):
        path = f"manifest.contrasts[{index}]"
        contrast = _input_mapping(contrast_value, path)
        _input_list(contrast.get("block_ids"), f"{path}.block_ids")
        members = _input_list(contrast.get("members"), f"{path}.members")
        for member_index, member in enumerate(members):
            _input_mapping(member, f"{path}.members[{member_index}]")
        prompt = contrast.get("prompt")
        if prompt is not None:
            _input_mapping(prompt, f"{path}.prompt")
        dependency = _input_mapping(
            contrast.get("floor_dependency"), f"{path}.floor_dependency"
        )
        _input_mapping(
            dependency.get("floor_selector"),
            f"{path}.floor_dependency.floor_selector",
        )
        transport = _input_mapping(
            dependency.get("transport"), f"{path}.floor_dependency.transport"
        )
        groups = _input_list(
            transport.get("transport_groups"),
            f"{path}.floor_dependency.transport.transport_groups",
        )
        for group_index, group in enumerate(groups):
            _input_mapping(
                group,
                f"{path}.floor_dependency.transport.transport_groups[{group_index}]",
            )

    contract = _input_mapping(
        manifest.get("finalization_contract"), "manifest.finalization_contract"
    )
    attachments = _input_list(
        contract.get("required_attachments"),
        "manifest.finalization_contract.required_attachments",
    )
    for index, attachment in enumerate(attachments):
        _input_mapping(
            attachment,
            f"manifest.finalization_contract.required_attachments[{index}]",
        )


def _walk_finalized_input(value: object) -> None:
    """Walk only attacker-controlled finalized container structure."""

    _walk_json_value(value, "manifest")
    manifest = _input_mapping(value, "manifest")
    if set(manifest) != _FINALIZED_TOP_KEYS:
        return
    for key in (
        "lineage",
        "design",
        "replacement_policy",
        "finalization_contract",
        "evidence",
    ):
        _input_mapping(manifest.get(key), f"manifest.{key}")
    design = _input_mapping(manifest.get("design"), "manifest.design")
    _input_mapping(design.get("sampling_plan"), "manifest.design.sampling_plan")

    for key in (
        "condition_families",
        "arms",
        "entries",
        "blocks",
        "families",
        "contrasts",
    ):
        rows = _input_list(manifest.get(key), f"manifest.{key}")
        for index, row_value in enumerate(rows):
            path = f"manifest.{key}[{index}]"
            row = _input_mapping(row_value, path)
            if key == "families":
                _input_list(row.get("contrast_ids"), f"{path}.contrast_ids")
                _input_mapping(row.get("multiplicity"), f"{path}.multiplicity")
            elif key == "blocks":
                _input_mapping(
                    row.get("position_entry_ids"), f"{path}.position_entry_ids"
                )
            elif key == "contrasts":
                _input_list(row.get("block_ids"), f"{path}.block_ids")
                _input_mapping(row.get("metric"), f"{path}.metric")
                _input_mapping(
                    row.get("floor_selector"), f"{path}.floor_selector"
                )
                _input_mapping(
                    row.get("floor_dependency"), f"{path}.floor_dependency"
                )

    contract = _input_mapping(
        manifest.get("finalization_contract"), "manifest.finalization_contract"
    )
    attachments = _input_list(
        contract.get("required_attachments"),
        "manifest.finalization_contract.required_attachments",
    )
    for index, attachment in enumerate(attachments):
        _input_mapping(
            attachment,
            f"manifest.finalization_contract.required_attachments[{index}]",
        )
    evidence = _input_mapping(manifest.get("evidence"), "manifest.evidence")
    for role in _REQUIRED_ATTACHMENT_ROLES:
        _input_mapping(evidence.get(role), f"manifest.evidence.{role}")


def _validate_prospective_analysis_manifest_v3_unchecked(
    value: Mapping[str, Any],
    *,
    manifest_dir: Path,
    plan_tree_path: Path,
) -> tuple[ManifestRefusal, ...]:
    """Validate the frozen D-117 prospective declaration, fail closed."""

    refusals: list[ManifestRefusal] = []
    manifest_dir = Path(manifest_dir)
    if not _exact_refusal_keys(
        value,
        _PROSPECTIVE_TOP_KEYS,
        "manifest",
        refusals,
        schema_code="analysis_prospective_schema_invalid",
        unknown_code="analysis_prospective_unknown_key",
    ):
        if _contains_unresolved_slot(value):
            _refusal(
                refusals,
                "analysis_prospective_unresolved_slot",
                "manifest contains an EMPTY/TODO placeholder",
            )
        if value.get("freeze_status") != "frozen":
            _refusal(
                refusals,
                "analysis_prospective_not_frozen",
                "manifest.freeze_status must be 'frozen'",
            )
        return tuple(refusals)
    if value.get("schema_version") != PROSPECTIVE_SCHEMA_VERSION:
        _refusal(
            refusals,
            "analysis_prospective_schema_invalid",
            f"manifest.schema_version must be {PROSPECTIVE_SCHEMA_VERSION!r}",
        )
    if value.get("freeze_status") != "frozen":
        _refusal(
            refusals,
            "analysis_prospective_not_frozen",
            "manifest.freeze_status must be 'frozen'",
        )
    if _contains_unresolved_slot(value):
        _refusal(
            refusals,
            "analysis_prospective_unresolved_slot",
            "manifest contains an EMPTY/TODO placeholder",
        )

    plan = value.get("plan")
    if _exact_refusal_keys(
        plan,
        _PROSPECTIVE_PLAN_KEYS,
        "manifest.plan",
        refusals,
        schema_code="analysis_prospective_schema_invalid",
        unknown_code="analysis_prospective_unknown_key",
    ):
        assert isinstance(plan, Mapping)
        _validate_file_binding(
            plan,
            path_key="path",
            sha_key="sha256",
            root=manifest_dir,
            where="manifest.plan",
            refusals=refusals,
        )
    root_order = value.get("root_order_manifest")
    root_order_value = None
    if _exact_refusal_keys(
        root_order,
        _PROSPECTIVE_ROOT_ORDER_KEYS,
        "manifest.root_order_manifest",
        refusals,
        schema_code="analysis_prospective_schema_invalid",
        unknown_code="analysis_prospective_unknown_key",
    ):
        assert isinstance(root_order, Mapping)
        root_order_value = _validate_file_binding(
            root_order,
            path_key="path",
            sha_key="sha256",
            root=manifest_dir,
            where="manifest.root_order_manifest",
            refusals=refusals,
        )
        if (
            isinstance(root_order_value, Mapping)
            and root_order_value.get("manifest_id") != root_order.get("manifest_id")
        ):
            _refusal(
                refusals,
                "analysis_prospective_source_hash_mismatch",
                "manifest.root_order_manifest.manifest_id disagrees with source",
            )

    stages = value.get("stage_manifests")
    if not isinstance(stages, list) or len(stages) != 4:
        _refusal(
            refusals,
            "analysis_prospective_schema_invalid",
            "manifest.stage_manifests must contain exactly four stages",
        )
    else:
        for index, stage in enumerate(stages):
            where = f"manifest.stage_manifests[{index}]"
            if _exact_refusal_keys(
                stage,
                _PROSPECTIVE_STAGE_KEYS,
                where,
                refusals,
                schema_code="analysis_prospective_schema_invalid",
                unknown_code="analysis_prospective_unknown_key",
            ):
                assert isinstance(stage, Mapping)
                parsed = _validate_file_binding(
                    stage,
                    path_key="manifest_path",
                    sha_key="manifest_sha256",
                    root=manifest_dir,
                    where=where,
                    refusals=refusals,
                )
                if (
                    isinstance(parsed, Mapping)
                    and parsed.get("manifest_id") != stage.get("manifest_id")
                ):
                    _refusal(
                        refusals,
                        "analysis_prospective_source_hash_mismatch",
                        f"{where}.manifest_id disagrees with source",
                    )
        if [stage.get("index") for stage in stages if isinstance(stage, Mapping)] != [
            1,
            2,
            3,
            4,
        ]:
            _refusal(
                refusals,
                "analysis_prospective_schema_invalid",
                "manifest.stage_manifests indexes must be contiguous 1..4",
            )

    conditions = value.get("condition_families")
    condition_ids: set[str] = set()
    condition_id_by_slot: dict[tuple[str, str], str] = {}
    condition_sha_by_id: dict[str, str] = {}
    prefill_arm: str | None = None
    observed_condition_slots: set[tuple[Any, Any]] = set()
    if not isinstance(conditions, list) or len(conditions) != 4:
        _refusal(
            refusals,
            "analysis_prospective_schema_invalid",
            "manifest.condition_families must contain exactly four bindings",
        )
    else:
        for index, condition in enumerate(conditions):
            where = f"manifest.condition_families[{index}]"
            if not _exact_refusal_keys(
                condition,
                _PROSPECTIVE_CONDITION_KEYS,
                where,
                refusals,
                schema_code="analysis_prospective_schema_invalid",
                unknown_code="analysis_prospective_unknown_key",
            ):
                continue
            assert isinstance(condition, Mapping)
            condition_id = condition.get("condition_family_id")
            if not isinstance(condition_id, str) or not condition_id or condition_id in condition_ids:
                _refusal(
                    refusals,
                    "analysis_prospective_schema_invalid",
                    f"{where}.condition_family_id must be nonempty and unique",
                )
            else:
                condition_ids.add(condition_id)
            slot = (condition.get("measurement_arm"), condition.get("arm"))
            if all(isinstance(item, str) for item in slot):
                observed_condition_slots.add(slot)
            else:
                _refusal(
                    refusals,
                    "analysis_prospective_schema_invalid",
                    f"{where}: measurement_arm/arm must be strings",
                )
            if all(isinstance(item, str) for item in slot) and isinstance(
                condition_id, str
            ):
                condition_id_by_slot[slot] = condition_id
            parsed = _validate_file_binding(
                condition,
                path_key="path",
                sha_key="sha256",
                root=manifest_dir,
                where=where,
                refusals=refusals,
            )
            if (
                isinstance(parsed, Mapping)
                and parsed.get("condition_family_id") != condition_id
            ):
                _refusal(
                    refusals,
                    "analysis_prospective_source_hash_mismatch",
                    f"{where}.condition_family_id disagrees with source",
                )
            from joulewise.detection_floor import (
                CONDITION_FAMILY_DOMAIN,
                canonical_domain_sha256,
            )

            expected_domain_sha = (
                canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, parsed)
                if isinstance(parsed, Mapping)
                else None
            )
            if (
                not _is_sha(condition.get("canonical_domain_sha256"))
                or condition.get("canonical_domain_sha256")
                != expected_domain_sha
            ):
                _refusal(
                    refusals,
                    "analysis_prospective_source_hash_mismatch",
                    f"{where}.canonical_domain_sha256 does not bind the source definition",
                )
            elif isinstance(condition_id, str):
                condition_sha_by_id[condition_id] = str(expected_domain_sha)
        non_decode_arms = {
            measurement_arm
            for measurement_arm, _arm in observed_condition_slots
            if measurement_arm != "decode"
        }
        candidate_prefill_arm = (
            next(iter(non_decode_arms)) if len(non_decode_arms) == 1 else None
        )
        if candidate_prefill_arm in _PROSPECTIVE_PREFILL_ARMS:
            prefill_arm = candidate_prefill_arm
        expected_condition_slots = (
            {
                ("decode", "A"),
                ("decode", "B"),
                (prefill_arm, "A"),
                (prefill_arm, "B"),
            }
            if prefill_arm is not None
            else set()
        )
        if observed_condition_slots != expected_condition_slots:
            _refusal(
                refusals,
                "analysis_prospective_contrast_cover_mismatch",
                "condition-family bindings must cover decode A/B and exactly one "
                "supported prefill arm A/B (prefill_p256, prefill_p512, "
                "prefill_p1024, or prefill_p2048)",
            )

    _exact_refusal_keys(
        value.get("design"),
        DESIGN_KEYS,
        "manifest.design",
        refusals,
        schema_code="analysis_prospective_schema_invalid",
        unknown_code="analysis_prospective_unknown_key",
    )
    design = value.get("design")
    if isinstance(design, Mapping):
        _exact_refusal_keys(
            design.get("sampling_plan"),
            SAMPLING_KEYS,
            "manifest.design.sampling_plan",
            refusals,
            schema_code="analysis_prospective_schema_invalid",
            unknown_code="analysis_prospective_unknown_key",
        )
        if (
            design.get("analysis_type") != "comparative_contrast"
            or design.get("null_alias") is not False
            or design.get("difference_orientation")
            != "condition_b_minus_condition_a"
            or not isinstance(design.get("sampling_plan"), Mapping)
            or design["sampling_plan"].get("design") != "fixed_n"
            or design["sampling_plan"].get("planned_n_blocks") != 10
        ):
            _refusal(
                refusals,
                "analysis_prospective_schema_invalid",
                "manifest.design must freeze fixed-n ten-block B-minus-A contrasts",
            )
    replacement = value.get("replacement_policy")
    if _exact_refusal_keys(
        replacement,
        _REPLACEMENT_POLICY_KEYS,
        "manifest.replacement_policy",
        refusals,
        schema_code="analysis_prospective_schema_invalid",
        unknown_code="analysis_prospective_unknown_key",
    ):
        assert isinstance(replacement, Mapping)
        if (
            replacement.get("outcome_dependent_top_up") != "forbidden"
            or replacement.get("science_member_replacements") != 0
            or not isinstance(replacement.get("allowed_replacement_reasons"), list)
        ):
            _refusal(
                refusals,
                "analysis_prospective_schema_invalid",
                "manifest.replacement_policy is not a frozen no-top-up policy",
            )

    families = value.get("families")
    family_by_id: dict[str, Mapping[str, Any]] = {}
    family_contrast_ids: list[str] = []
    if not isinstance(families, list) or not families:
        _refusal(
            refusals,
            "analysis_prospective_family_invalid",
            "manifest.families must be a nonempty array",
        )
    else:
        for index, family in enumerate(families):
            where = f"manifest.families[{index}]"
            if not _exact_refusal_keys(
                family,
                FAMILY_KEYS,
                where,
                refusals,
                schema_code="analysis_prospective_family_invalid",
                unknown_code="analysis_prospective_unknown_key",
            ):
                continue
            assert isinstance(family, Mapping)
            family_id = family.get("family_instance_id")
            ids = family.get("contrast_ids")
            multiplicity = family.get("multiplicity")
            if (
                not isinstance(family_id, str)
                or not family_id
                or family_id in family_by_id
                or not _unique_nonempty_strings(ids)
            ):
                _refusal(
                    refusals,
                    "analysis_prospective_family_invalid",
                    f"{where}: invalid family identity or contrast membership",
                )
                continue
            family_by_id[family_id] = family
            family_contrast_ids.extend(ids)
            if not _exact_refusal_keys(
                multiplicity,
                MULTIPLICITY_KEYS,
                f"{where}.multiplicity",
                refusals,
                schema_code="analysis_prospective_multiplicity_invalid",
                unknown_code="analysis_prospective_unknown_key",
            ):
                continue
            assert isinstance(multiplicity, Mapping)
            if (
                not isinstance(multiplicity.get("method"), str)
                or not isinstance(multiplicity.get("m"), int)
                or isinstance(multiplicity.get("m"), bool)
                or (
                    multiplicity.get("alpha") is not None
                    and (
                        not isinstance(multiplicity.get("alpha"), (int, float))
                        or isinstance(multiplicity.get("alpha"), bool)
                    )
                )
                or (
                    multiplicity.get("q") is not None
                    and (
                        not isinstance(multiplicity.get("q"), (int, float))
                        or isinstance(multiplicity.get("q"), bool)
                    )
                )
            ):
                _refusal(
                    refusals,
                    "analysis_prospective_multiplicity_invalid",
                    f"{where}.multiplicity has wrong scalar types",
                )
                continue
            try:
                # This is the production compatibility table, exercised with
                # null p-values so prospective admission cannot drift from
                # the post-preparation adjustment boundary.
                from joulewise.analysis_engine.multiplicity import adjust_p_values

                adjust_p_values(
                    {contrast_id: None for contrast_id in ids},
                    method=multiplicity.get("method"),
                    m=multiplicity.get("m"),
                    alpha=multiplicity.get("alpha"),
                    q=multiplicity.get("q"),
                )
            except ValueError:
                _refusal(
                    refusals,
                    "analysis_prospective_multiplicity_invalid",
                    f"{where}.multiplicity is incompatible with the production adjustment method",
                )

    contrasts = value.get("contrasts")
    expected_arms = (
        {"decode", prefill_arm} if prefill_arm is not None else {"decode"}
    )
    contrast_ids: list[str] = []
    all_run_ids: list[str] = []
    all_order_indexes: list[int] = []
    all_block_ids: list[str] = []
    if not isinstance(contrasts, list) or len(contrasts) != 2:
        _refusal(
            refusals,
            "analysis_prospective_contrast_cover_mismatch",
            "manifest.contrasts must contain decode and the same single supported "
            "prefill arm",
        )
    else:
        for index, contrast in enumerate(contrasts):
            where = f"manifest.contrasts[{index}]"
            if not _exact_refusal_keys(
                contrast,
                _PROSPECTIVE_CONTRAST_KEYS,
                where,
                refusals,
                schema_code="analysis_prospective_schema_invalid",
                unknown_code="analysis_prospective_unknown_key",
            ):
                continue
            assert isinstance(contrast, Mapping)
            contrast_id = contrast.get("contrast_id")
            if not isinstance(contrast_id, str) or not contrast_id or contrast_id in contrast_ids:
                _refusal(
                    refusals,
                    "analysis_prospective_contrast_cover_mismatch",
                    f"{where}.contrast_id must be nonempty and unique",
                )
            else:
                contrast_ids.append(contrast_id)
            if contrast.get("difference_orientation") != "condition_b_minus_condition_a":
                _refusal(
                    refusals,
                    "analysis_prospective_schema_invalid",
                    f"{where}.difference_orientation must be B-minus-A",
                )
            if contrast.get("test") not in {"two_sided", "greater", "less"}:
                _refusal(
                    refusals,
                    "analysis_prospective_schema_invalid",
                    f"{where}.test is unresolved or unsupported",
                )
            if contrast.get("scientific_hypothesis_direction") not in {
                "positive",
                "negative",
            }:
                _refusal(
                    refusals,
                    "analysis_prospective_schema_invalid",
                    f"{where}.scientific_hypothesis_direction is invalid",
                )
            prompt = contrast.get("prompt")
            if prompt is not None:
                if _exact_refusal_keys(
                    prompt,
                    _PROMPT_KEYS,
                    f"{where}.prompt",
                    refusals,
                    schema_code="analysis_prospective_schema_invalid",
                    unknown_code="analysis_prospective_unknown_key",
                ):
                    assert isinstance(prompt, Mapping)
                    _validate_file_binding(
                        prompt,
                        path_key="path",
                        sha_key="sha256",
                        root=manifest_dir,
                        where=f"{where}.prompt",
                        refusals=refusals,
                    )
                    if not isinstance(prompt.get("status"), str) or not prompt.get(
                        "status"
                    ):
                        _refusal(
                            refusals,
                            "analysis_prospective_schema_invalid",
                            f"{where}.prompt.status must be a frozen nonempty value",
                        )
            family_id = contrast.get("family_instance_id")
            family = (
                family_by_id.get(family_id)
                if isinstance(family_id, str)
                else None
            )
            if not isinstance(family, Mapping) or contrast_id not in family.get("contrast_ids", []):
                _refusal(
                    refusals,
                    "analysis_prospective_family_invalid",
                    f"{where}.family_instance_id is not its frozen family",
                )
            if contrast.get("condition_a_id") not in condition_ids or contrast.get(
                "condition_b_id"
            ) not in condition_ids:
                _refusal(
                    refusals,
                    "analysis_prospective_contrast_cover_mismatch",
                    f"{where}: condition identities are not bound",
                )
            measurement_arm = contrast.get("measurement_arm")
            if (
                not isinstance(measurement_arm, str)
                or
                contrast.get("condition_a_id")
                != condition_id_by_slot.get((measurement_arm, "A"))
                or contrast.get("condition_b_id")
                != condition_id_by_slot.get((measurement_arm, "B"))
            ):
                _refusal(
                    refusals,
                    "analysis_prospective_contrast_cover_mismatch",
                    f"{where}: conditions do not match the contrast measurement arm",
                )
            floor_dependency = contrast.get("floor_dependency")
            if not _exact_refusal_keys(
                floor_dependency,
                _FLOOR_DEPENDENCY_KEYS,
                f"{where}.floor_dependency",
                refusals,
                schema_code="analysis_prospective_floor_dependency_unresolved",
                unknown_code="analysis_prospective_unknown_key",
            ):
                continue
            assert isinstance(floor_dependency, Mapping)
            selector = floor_dependency.get("floor_selector")
            if not _exact_refusal_keys(
                selector,
                FLOOR_SELECTOR_KEYS,
                f"{where}.floor_dependency.floor_selector",
                refusals,
                schema_code="analysis_prospective_floor_dependency_unresolved",
                unknown_code="analysis_prospective_unknown_key",
            ):
                continue
            assert isinstance(selector, Mapping)
            transport = floor_dependency.get("transport")
            if (
                floor_dependency.get("required_artifact_schema") != _FLOOR_SCHEMA
                or selector.get("metric") != contrast.get("metric")
                or selector.get("condition_family_ids")
                != [contrast.get("condition_a_id"), contrast.get("condition_b_id")]
                or selector.get("backend") not in {"from_bundle", "powermetrics"}
                or selector.get("floor_field") != "floor_gate_j"
                or selector.get("claim_floor_rule") != FLOOR_RULE_ID
            ):
                _refusal(
                    refusals,
                    "analysis_prospective_floor_dependency_unresolved",
                    f"{where}.floor_dependency does not freeze the exact selector/transport",
                )
            if _exact_refusal_keys(
                transport,
                _TRANSPORT_KEYS,
                f"{where}.floor_dependency.transport",
                refusals,
                schema_code="analysis_prospective_floor_dependency_unresolved",
                unknown_code="analysis_prospective_unknown_key",
            ):
                assert isinstance(transport, Mapping)
                mode = transport.get("mode")
                rule_id = transport.get("rule_id")
                expected_rule = (
                    EXACT_STACK_RULE_ID
                    if mode == "exact_stack_only"
                    else GOVERNED_TRANSPORT_RULE_ID
                    if mode == "governed_transport"
                    else None
                )
                bindings = transport.get("transport_groups")
                binding_conditions: list[str] = []
                if not isinstance(bindings, list) or len(bindings) != 2:
                    _refusal(
                        refusals,
                        "analysis_prospective_floor_dependency_unresolved",
                        f"{where}.floor_dependency.transport must bind two transport groups",
                    )
                else:
                    for binding_index, binding in enumerate(bindings):
                        binding_where = (
                            f"{where}.floor_dependency.transport."
                            f"transport_groups[{binding_index}]"
                        )
                        if not _exact_refusal_keys(
                            binding,
                            _TRANSPORT_GROUP_BINDING_KEYS,
                            binding_where,
                            refusals,
                            schema_code=(
                                "analysis_prospective_floor_dependency_unresolved"
                            ),
                            unknown_code="analysis_prospective_unknown_key",
                        ):
                            continue
                        assert isinstance(binding, Mapping)
                        condition_id = binding.get("condition_family_id")
                        if isinstance(condition_id, str):
                            binding_conditions.append(condition_id)
                        if (
                            not isinstance(binding.get("transport_group_id"), str)
                            or not binding.get("transport_group_id")
                            or condition_id
                            not in {
                                contrast.get("condition_a_id"),
                                contrast.get("condition_b_id"),
                            }
                            or binding.get("condition_domain_sha256")
                            != condition_sha_by_id.get(condition_id)
                            or binding.get("group_rule_id")
                            != GOVERNED_TRANSPORT_RULE_ID
                        ):
                            _refusal(
                                refusals,
                                "analysis_prospective_floor_dependency_unresolved",
                                f"{binding_where} does not freeze the condition-domain/group rule",
                            )
                if (
                    expected_rule is None
                    or rule_id != expected_rule
                    or selector.get("transport_rule_id") != expected_rule
                    or binding_conditions
                    != [
                        contrast.get("condition_a_id"),
                        contrast.get("condition_b_id"),
                    ]
                ):
                    _refusal(
                        refusals,
                        "analysis_prospective_floor_dependency_unresolved",
                        f"{where}.floor_dependency transport mode/rules are inconsistent",
                    )
            block_ids = contrast.get("block_ids")
            members = contrast.get("members")
            if (
                not isinstance(block_ids, list)
                or len(block_ids) != 10
                or not all(isinstance(block_id, str) and block_id for block_id in block_ids)
                or len(block_ids) != len(set(block_ids))
            ):
                _refusal(
                    refusals,
                    "analysis_prospective_block_cover_mismatch",
                    f"{where}.block_ids must contain ten unique blocks",
                )
                block_ids = []
            all_block_ids.extend(block_ids)
            if not isinstance(members, list) or len(members) != 40:
                _refusal(
                    refusals,
                    "analysis_prospective_member_cover_mismatch",
                    f"{where}.members must contain exactly 40 rows",
                )
                continue
            block_positions: dict[str, list[str]] = {}
            block_numbers: dict[str, set[int]] = {}
            for member_index, member in enumerate(members):
                member_where = f"{where}.members[{member_index}]"
                if not _exact_refusal_keys(
                    member,
                    _PROSPECTIVE_MEMBER_KEYS,
                    member_where,
                    refusals,
                    schema_code="analysis_prospective_schema_invalid",
                    unknown_code="analysis_prospective_unknown_key",
                ):
                    continue
                assert isinstance(member, Mapping)
                run_id = member.get("run_id")
                order_index = member.get("order_index")
                if isinstance(run_id, str):
                    all_run_ids.append(run_id)
                if isinstance(order_index, int) and not isinstance(order_index, bool):
                    all_order_indexes.append(order_index)
                block_id = member.get("block_id")
                block_number = member.get("block_number")
                position = member.get("position")
                if isinstance(block_id, str) and isinstance(position, str):
                    block_positions.setdefault(block_id, []).append(position)
                if (
                    isinstance(block_id, str)
                    and isinstance(block_number, int)
                    and not isinstance(block_number, bool)
                ):
                    block_numbers.setdefault(block_id, set()).add(block_number)
                if block_id not in block_ids or member.get("arm") != POSITION_ARMS.get(position):
                    _refusal(
                        refusals,
                        "analysis_prospective_member_cover_mismatch",
                        f"{member_where}: block/arm/position binding is invalid",
                    )
                _validate_file_binding(
                    member,
                    path_key="config",
                    sha_key="config_sha256",
                    root=manifest_dir,
                    where=member_where,
                    refusals=refusals,
                )
            if any(
                positions != list(POSITION_ORDER)
                for positions in block_positions.values()
            ) or set(block_positions) != set(block_ids):
                _refusal(
                    refusals,
                    "analysis_prospective_block_cover_mismatch",
                    f"{where}: every block must contain ordered A1/B1/B2/A2 positions",
                )
            ordered_numbers = [
                next(iter(block_numbers.get(block_id, set())), None)
                if len(block_numbers.get(block_id, set())) == 1
                else None
                for block_id in block_ids
            ]
            if ordered_numbers != list(range(1, 11)):
                _refusal(
                    refusals,
                    "analysis_prospective_block_cover_mismatch",
                    f"{where}: block_ids must bind contiguous block numbers 1..10",
                )
        observed_arms = {
            contrast.get("measurement_arm")
            for contrast in contrasts
            if isinstance(contrast, Mapping)
        }
        if prefill_arm is None or observed_arms != expected_arms:
            _refusal(
                refusals,
                "analysis_prospective_contrast_cover_mismatch",
                "manifest.contrasts must cover decode and the condition-family "
                "prefill arm exactly",
            )
    if (
        len(all_run_ids) != 80
        or len(set(all_run_ids)) != 80
        or sorted(all_order_indexes) != list(range(1, 81))
    ):
        _refusal(
            refusals,
            "analysis_prospective_member_cover_mismatch",
            "the two contrasts must freeze 80 unique members ordered 1..80",
        )
    if len(all_block_ids) != 20 or len(set(all_block_ids)) != 20:
        _refusal(
            refusals,
            "analysis_prospective_block_cover_mismatch",
            "the two contrasts must freeze twenty distinct ABBA blocks",
        )
    if sorted(family_contrast_ids) != sorted(contrast_ids) or len(
        family_contrast_ids
    ) != len(set(family_contrast_ids)):
        _refusal(
            refusals,
            "analysis_prospective_family_invalid",
            "families must cover each frozen contrast exactly once",
        )

    contract = value.get("finalization_contract")
    if _exact_refusal_keys(
        contract,
        _FINALIZATION_CONTRACT_KEYS,
        "manifest.finalization_contract",
        refusals,
        schema_code="analysis_prospective_schema_invalid",
        unknown_code="analysis_prospective_unknown_key",
    ):
        assert isinstance(contract, Mapping)
        attachments = contract.get("required_attachments")
        roles: set[str] = set()
        if not isinstance(attachments, list) or len(attachments) != 4:
            _refusal(
                refusals,
                "analysis_prospective_schema_invalid",
                "finalization contract must declare four attachment roles",
            )
        else:
            for index, attachment in enumerate(attachments):
                if _exact_refusal_keys(
                    attachment,
                    _ATTACHMENT_DECLARATION_KEYS,
                    f"manifest.finalization_contract.required_attachments[{index}]",
                    refusals,
                    schema_code="analysis_prospective_schema_invalid",
                    unknown_code="analysis_prospective_unknown_key",
                ):
                    assert isinstance(attachment, Mapping)
                    if isinstance(attachment.get("role"), str):
                        roles.add(attachment["role"])
                    if not isinstance(attachment.get("schema_version"), str) or not attachment.get("schema_version"):
                        _refusal(
                            refusals,
                            "analysis_prospective_schema_invalid",
                            "attachment schema versions must be nonempty strings",
                        )
        expected_attachment_schemas = {
            "whole_window_verdict": _WHOLE_WINDOW_SCHEMA,
            "bracket_binding": _BRACKET_BINDING_SCHEMA,
            "calibration_ledger": _LEDGER_SCHEMA,
            "aggregate_floor_artifact": _FLOOR_SCHEMA,
        }
        observed_attachment_schemas = {
            attachment.get("role"): attachment.get("schema_version")
            for attachment in attachments
            if isinstance(attachment, Mapping)
            and isinstance(attachment.get("role"), str)
        } if isinstance(attachments, list) else {}
        if (
            contract.get("contract_id") != FINALIZATION_CONTRACT_ID
            or contract.get("projection_rule_id") != SEMANTICS_PROJECTION_RULE_ID
            or contract.get("namespace_rule_id") != FINALIZED_NAMESPACE_RULE_ID
            or contract.get("output_basename_suffix") != FINALIZED_BASENAME_SUFFIX
            or roles != _REQUIRED_ATTACHMENT_ROLES
            or observed_attachment_schemas != expected_attachment_schemas
        ):
            _refusal(
                refusals,
                "analysis_prospective_schema_invalid",
                "manifest.finalization_contract differs from the governed contract",
            )

    try:
        semantic_sha = analysis_semantics_sha256_v1(value)
    except AnalysisManifestV3Error as exc:
        _refusal(
            refusals,
            "analysis_prospective_schema_invalid",
            f"semantic projection is not canonical: {exc}",
        )
    else:
        if value.get("frozen_semantics_sha256") != semantic_sha:
            _refusal(
                refusals,
                "analysis_prospective_identity_mismatch",
                "manifest.frozen_semantics_sha256 does not match the frozen projection",
            )
    expected_id = calculate_manifest_id(value)
    if value.get("manifest_id") != expected_id:
        _refusal(
            refusals,
            "analysis_prospective_identity_mismatch",
            "manifest.manifest_id does not match canonical content",
        )

    try:
        tree_raw = Path(plan_tree_path).read_bytes()
        tree = _strict_json_bytes(tree_raw, "plan tree")
    except (OSError, AnalysisManifestFinalizationError) as exc:
        _refusal(
            refusals,
            "analysis_prospective_plan_tree_mismatch",
            f"plan tree is unreadable: {exc}",
        )
    else:
        tree_plan = tree.get("plan") if isinstance(tree, Mapping) else None
        downstream = (
            tree.get("downstream_contract") if isinstance(tree, Mapping) else None
        )
        if not isinstance(tree_plan, Mapping) or not isinstance(plan, Mapping) or (
            tree_plan.get("plan_id") != plan.get("plan_id")
            or tree_plan.get("actual_sha256") != plan.get("sha256")
            or tree_plan.get("declared_sha256") != plan.get("sha256")
        ):
            _refusal(
                refusals,
                "analysis_prospective_plan_tree_mismatch",
                "plan tree does not bind the prospective calibration plan",
            )
        if isinstance(downstream, Mapping):
            manifest_path = _safe_relative_file(
                manifest_dir, downstream.get("analysis_manifest_path")
            )
            if manifest_path is None:
                _refusal(
                    refusals,
                    "analysis_prospective_plan_tree_mismatch",
                    "plan tree analysis-manifest path is unsafe or missing",
                )
            else:
                raw = manifest_path.read_bytes()
                try:
                    parsed = _strict_json_bytes(raw, "plan-tree prospective pin")
                except AnalysisManifestFinalizationError:
                    parsed = None
                if (
                    hashlib.sha256(raw).hexdigest()
                    != downstream.get("analysis_manifest_sha256")
                    or parsed != value
                ):
                    _refusal(
                        refusals,
                        "analysis_prospective_plan_tree_mismatch",
                        "plan tree does not authenticate these exact prospective bytes",
                    )
        else:
            _refusal(
                refusals,
                "analysis_prospective_plan_tree_mismatch",
                "plan tree lacks downstream_contract",
            )
    return tuple(refusals)


def validate_prospective_analysis_manifest_v3(
    value: Mapping[str, Any],
    *,
    manifest_dir: Path,
    plan_tree_path: Path,
) -> tuple[ManifestRefusal, ...]:
    """Total boundary with region-based malformed/defect classification."""

    try:
        _walk_prospective_input(value)
    except _ManifestInputWalkError as exc:
        return (
            ManifestRefusal(
                PROSPECTIVE_MALFORMED_VALUE_CODE,
                f"malformed prospective value at {exc.path}: expected "
                f"{exc.expected}, got {exc.observed_type}",
                cause=exc,
            ),
        )
    except _INPUT_MALFORMATION_EXCEPTIONS as exc:
        return (
            ManifestRefusal(
                PROSPECTIVE_MALFORMED_VALUE_CODE,
                "malformed prospective value during input walk: "
                f"{type(exc).__name__}: {exc}",
                cause=exc,
            ),
        )
    except Exception as exc:
        return (
            ManifestRefusal(
                PROSPECTIVE_INTERNAL_ERROR_CODE,
                "prospective input-walk internal defect: "
                f"{type(exc).__name__}: {exc}",
                cause=exc,
            ),
        )

    try:
        return _validate_prospective_analysis_manifest_v3_unchecked(
            value,
            manifest_dir=manifest_dir,
            plan_tree_path=plan_tree_path,
        )
    except Exception as exc:
        return (
            ManifestRefusal(
                PROSPECTIVE_INTERNAL_ERROR_CODE,
                f"prospective validator internal defect: {type(exc).__name__}: {exc}",
                cause=exc,
            ),
        )


def build_prospective_analysis_manifest_v3(
    campaign_dir: Path, *, plan_tree_path: Path
) -> dict[str, Any]:
    """Load the immutable prospective bytes after full governed validation."""

    path = Path(campaign_dir) / MANIFEST_NAME
    value, _ = _read_strict_object(path, "prospective analysis manifest")
    refusals = validate_prospective_analysis_manifest_v3(
        value,
        manifest_dir=Path(campaign_dir),
        plan_tree_path=Path(plan_tree_path),
    )
    if refusals:
        raise AnalysisManifestV3Error(
            "; ".join(f"{item.reason_code}: {item.detail}" for item in refusals)
        )
    return json.loads(json.dumps(value))


def _declared_attachment_schemas(
    prospective: Mapping[str, Any],
) -> dict[str, str]:
    contract = prospective["finalization_contract"]
    return {
        str(row["role"]): str(row["schema_version"])
        for row in contract["required_attachments"]
    }


def _verify_basis_members(
    prospective: Mapping[str, Any],
    verdict: Mapping[str, Any],
    *,
    manifest_dir: Path,
    runs_root: Path,
) -> tuple[Mapping[str, Any], dict[str, Path]]:
    basis = verdict.get("evaluation_basis")
    if (
        not isinstance(basis, Mapping)
        or basis.get("schema_version") != _WHOLE_WINDOW_BASIS_SCHEMA
        or not _is_sha(basis.get("sha256"))
        or basis.get("sha256")
        != _canonical_sha({key: value for key, value in basis.items() if key != "sha256"})
    ):
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_evaluation_basis_mismatch",
            "whole-window evaluation basis is absent or not self-authenticating",
        )
    occurrences = basis.get("member_occurrences")
    if not isinstance(occurrences, list):
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_evaluation_basis_mismatch",
            "evaluation_basis.member_occurrences must be an array",
        )
    expected_members = {
        str(member["run_id"]): member
        for contrast in prospective["contrasts"]
        for member in contrast["members"]
    }
    by_id: dict[str, Mapping[str, Any]] = {}
    bundle_paths: dict[str, Path] = {}
    for index, occurrence in enumerate(occurrences):
        if (
            not isinstance(occurrence, Mapping)
            or set(occurrence) != _WHOLE_WINDOW_OCCURRENCE_KEYS
        ):
            raise AnalysisManifestFinalizationError(
                "analysis_finalization_evaluation_basis_mismatch",
                f"member_occurrences[{index}] is not an exact production occurrence",
            )
        bundle_id = occurrence.get("bundle_id")
        if not isinstance(bundle_id, str) or not bundle_id or bundle_id in by_id:
            raise AnalysisManifestFinalizationError(
                "analysis_finalization_evaluation_basis_mismatch",
                "evaluation-basis bundle identities must be nonempty and unique",
            )
        bundle_path = occurrence.get("bundle_path")
        bundle = _safe_relative_file(Path(runs_root), f"{bundle_path}/config.json")
        if bundle is None:
            raise AnalysisManifestFinalizationError(
                "analysis_finalization_attachment_invalid",
                f"evaluation-basis bundle {bundle_id!r} escapes custody or lacks config.json",
            )
        bundle_dir = bundle.parent
        if bundle_dir.name != bundle_id:
            raise AnalysisManifestFinalizationError(
                "analysis_finalization_member_cover_mismatch",
                f"evaluation-basis path for {bundle_id!r} does not preserve identity",
            )
        for filename, key in (
            ("config.json", "config_sha256"),
            ("metadata.json", "metadata_sha256"),
            ("summary_metrics.json", "summary_sha256"),
        ):
            path = _safe_relative_file(Path(runs_root), f"{bundle_path}/{filename}")
            if path is None or hashlib.sha256(path.read_bytes()).hexdigest() != occurrence.get(key):
                raise AnalysisManifestFinalizationError(
                    "analysis_finalization_attachment_invalid",
                    f"evaluation-basis bytes for {bundle_id!r}/{filename} do not match",
                )
        member = expected_members.get(bundle_id)
        source_path = (
            _safe_relative_file(manifest_dir, member.get("config"))
            if isinstance(member, Mapping)
            else None
        )
        if source_path is None:
            raise AnalysisManifestFinalizationError(
                "analysis_finalization_member_cover_mismatch",
                f"evaluation-basis bundle {bundle_id!r} is not a frozen member",
            )
        try:
            from joulewise.schemas import BenchmarkConfig

            source = _strict_json_bytes(
                source_path.read_bytes(), f"frozen config for {bundle_id}"
            )
            normalized = (
                json.dumps(
                    BenchmarkConfig.from_mapping(source).to_dict(),
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            ).encode("utf-8")
        except Exception as exc:
            raise AnalysisManifestFinalizationError(
                "analysis_finalization_member_cover_mismatch",
                f"frozen config for {bundle_id!r} cannot derive bundle bytes: {exc}",
            ) from exc
        if hashlib.sha256(bundle.read_bytes()).hexdigest() != hashlib.sha256(
            normalized
        ).hexdigest():
            raise AnalysisManifestFinalizationError(
                "analysis_finalization_member_cover_mismatch",
                f"bundle config for {bundle_id!r} differs from its frozen source",
            )
        by_id[bundle_id] = occurrence
        bundle_paths[bundle_id] = bundle_dir
    expected = set(expected_members)
    verdict_ids = verdict.get("bundle_ids")
    if (
        not isinstance(verdict_ids, list)
        or len(verdict_ids) != len(set(verdict_ids))
        or set(verdict_ids) != expected
        or set(by_id) != expected
    ):
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_member_cover_mismatch",
            "passed verdict/evaluation basis does not cover all 80 frozen members",
        )
    return basis, bundle_paths


def _derive_arms_and_entries(
    prospective: Mapping[str, Any],
    *,
    manifest_dir: Path,
    runs_root: Path,
    bundle_paths: Mapping[str, Path],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    # Local import avoids a module-import cycle: inputs imports this module to
    # validate both v3 siblings.  Realized identity reads config/metadata only,
    # never summary metrics or an effect estimate.
    from joulewise.analysis_engine.inputs import realized_scientific_identity

    condition_by_slot = {
        (row["measurement_arm"], row["arm"]): row
        for row in prospective["condition_families"]
    }
    arms: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    blocks: list[dict[str, Any]] = []
    for contrast in prospective["contrasts"]:
        measurement_arm = contrast["measurement_arm"]
        entry_ids_by_block: dict[str, dict[str, str]] = {}
        for arm_label, condition_key in (
            ("A", "condition_a_id"),
            ("B", "condition_b_id"),
        ):
            condition = condition_by_slot[(measurement_arm, arm_label)]
            condition_id = condition["condition_family_id"]
            if condition_id != contrast[condition_key]:
                raise AnalysisManifestFinalizationError(
                    "analysis_finalization_semantics_mismatch",
                    f"{measurement_arm}/{arm_label} condition binding changed",
                )
            members = [row for row in contrast["members"] if row["arm"] == arm_label]
            identities: list[Mapping[str, Any]] = []
            for member in members:
                bundle = bundle_paths.get(member["run_id"])
                if bundle is None:
                    raise AnalysisManifestFinalizationError(
                        "analysis_finalization_member_cover_mismatch",
                        f"authenticated bundle path is missing for {member['run_id']}",
                    )
                try:
                    raw_config = json.loads((bundle / "config.json").read_bytes())
                    metadata = json.loads((bundle / "metadata.json").read_bytes())
                except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise AnalysisManifestFinalizationError(
                        "analysis_finalization_attachment_invalid",
                        f"cannot derive realized identity for {member['run_id']}: {exc}",
                    ) from exc
                identity = realized_scientific_identity(raw_config, metadata)
                if identity is None:
                    raise AnalysisManifestFinalizationError(
                        "analysis_finalization_attachment_invalid",
                        f"realized stack identity is incomplete for {member['run_id']}",
                    )
                identities.append(identity)
            identity_encodings = {
                canonical_json_bytes(identity) for identity in identities
            }
            if len(identity_encodings) != 1:
                raise AnalysisManifestFinalizationError(
                    "analysis_finalization_member_cover_mismatch",
                    f"realized stack identity varies within {measurement_arm}/{arm_label}",
                )
            arm_id = f"{measurement_arm}:{arm_label}"
            cell_id = f"cell-{measurement_arm}-{arm_label.lower()}"
            model_tag = f"model-{condition_id}"
            arms.append(
                {
                    "arm_id": arm_id,
                    "condition_family_id": condition_id,
                    "condition_family_sha256": condition[
                        "canonical_domain_sha256"
                    ],
                    "model_tag": model_tag,
                    "cell_id": cell_id,
                    "realized_stack_identity": json.loads(
                        json.dumps(identities[0])
                    ),
                }
            )
            for member in members:
                entry_id = f"entry-{member['run_id']}"
                entries.append(
                    {
                        "entry_id": entry_id,
                        "config": member["config"],
                        "config_sha256": member["config_sha256"],
                        "run_id": member["run_id"],
                        "bundle_path": bundle_paths[
                            member["run_id"]
                        ].relative_to(runs_root).as_posix(),
                        "model_tag": model_tag,
                        "role": "condition",
                        "arm_id": arm_id,
                        "condition_id": condition_id,
                        "cell_id": cell_id,
                        "block_id": member["block_id"],
                        "block_number": member["block_number"],
                        "position": member["position"],
                        "order_index": member["order_index"],
                    }
                )
                entry_ids_by_block.setdefault(member["block_id"], {})[
                    member["position"]
                ] = entry_id
        member_by_block = {
            block_id: [
                row for row in contrast["members"] if row["block_id"] == block_id
            ]
            for block_id in contrast["block_ids"]
        }
        for block_id in contrast["block_ids"]:
            rows = member_by_block[block_id]
            blocks.append(
                {
                    "block_id": block_id,
                    "block_number": rows[0]["block_number"],
                    "position_entry_ids": {
                        position: entry_ids_by_block[block_id][position]
                        for position in POSITION_ORDER
                    },
                }
            )
    arms.sort(key=lambda row: row["arm_id"])
    entries.sort(key=lambda row: row["order_index"])
    blocks.sort(key=lambda row: (row["block_number"], row["block_id"]))
    return arms, entries, blocks


def _floor_consumer_contexts(
    prospective: Mapping[str, Any],
    bundle_paths: Mapping[str, Path],
) -> dict[str, tuple[str, str]]:
    """Derive each frozen condition's backend and governed stack hash."""

    from joulewise.identity_pins import build_stack_identity, stack_identity_sha256

    contexts: dict[str, tuple[str, str]] = {}
    for contrast in prospective["contrasts"]:
        for arm_label, condition_key in (
            ("A", "condition_a_id"),
            ("B", "condition_b_id"),
        ):
            condition_id = str(contrast[condition_key])
            observed: set[tuple[str, str]] = set()
            for member in contrast["members"]:
                if member["arm"] != arm_label:
                    continue
                bundle = bundle_paths[member["run_id"]]
                raw_config = _strict_json_bytes(
                    (bundle / "config.json").read_bytes(),
                    f"floor selector config for {member['run_id']}",
                )
                metadata = _strict_json_bytes(
                    (bundle / "metadata.json").read_bytes(),
                    f"floor selector metadata for {member['run_id']}",
                )
                hardware = raw_config.get("hardware_target")
                backend = (
                    hardware.get("telemetry_backend")
                    if isinstance(hardware, Mapping)
                    else None
                )
                stack = build_stack_identity(raw_config, metadata)
                if not isinstance(backend, str) or not backend or stack is None:
                    raise AnalysisManifestFinalizationError(
                        "analysis_finalization_floor_dependency_unsatisfied",
                        f"realized floor selector is incomplete for {member['run_id']}",
                    )
                observed.add((backend, stack_identity_sha256(stack)))
            if len(observed) != 1:
                raise AnalysisManifestFinalizationError(
                    "analysis_finalization_floor_dependency_unsatisfied",
                    f"realized floor selector varies within condition {condition_id}",
                )
            contexts[condition_id] = next(iter(observed))
    return contexts


def _authenticate_floor_dependencies(
    prospective: Mapping[str, Any],
    floor: Mapping[str, Any],
    *,
    bundle_paths: Mapping[str, Path],
) -> None:
    """Authenticate every frozen selector and its complete transport group."""

    contexts = _floor_consumer_contexts(prospective, bundle_paths)
    condition_shas = {
        row["condition_family_id"]: row["canonical_domain_sha256"]
        for row in prospective["condition_families"]
    }
    cells = [row for row in floor.get("cells", []) if isinstance(row, Mapping)]
    groups = [
        row for row in floor.get("transport_groups", []) if isinstance(row, Mapping)
    ]
    for contrast in prospective["contrasts"]:
        dependency = contrast["floor_dependency"]
        selector = dependency["floor_selector"]
        transport = dependency["transport"]
        bindings = transport["transport_groups"]
        binding_by_condition = {
            row["condition_family_id"]: row for row in bindings
        }
        for condition_id in selector["condition_family_ids"]:
            binding = binding_by_condition[condition_id]
            expected_backend, expected_stack_sha = contexts[condition_id]
            if selector["backend"] not in {"from_bundle", expected_backend}:
                raise AnalysisManifestFinalizationError(
                    "analysis_finalization_floor_dependency_unsatisfied",
                    f"selector backend does not match {condition_id}",
                )
            if (
                binding["condition_domain_sha256"] != condition_shas[condition_id]
                or binding["group_rule_id"] != GOVERNED_TRANSPORT_RULE_ID
            ):
                raise AnalysisManifestFinalizationError(
                    "analysis_finalization_floor_dependency_unsatisfied",
                    f"condition-domain/transport rule does not match {condition_id}",
                )
            matching_groups = [
                group
                for group in groups
                if group.get("transport_group_id")
                == binding["transport_group_id"]
            ]
            if len(matching_groups) != 1:
                raise AnalysisManifestFinalizationError(
                    "analysis_finalization_floor_dependency_unsatisfied",
                    f"declared transport group is absent or ambiguous for {condition_id}",
                )
            group = matching_groups[0]
            allowed = group.get("allowed_consumer_condition_families")
            allowed_matches = [
                row
                for row in allowed or []
                if isinstance(row, Mapping)
                and row.get("condition_family_id") == condition_id
                and row.get("condition_family_sha256")
                == condition_shas[condition_id]
            ]
            composed_field = "composed_" + selector["floor_field"]
            if (
                group.get("rule_id") != binding["group_rule_id"]
                or group.get("backend") != expected_backend
                or group.get("metric") != selector["metric"]
                or group.get("window_class") != selector["window_class"]
                or group.get("stack_identity_sha256") != expected_stack_sha
                or len(allowed_matches) != 1
                or isinstance(group.get(composed_field), bool)
                or not isinstance(group.get(composed_field), (int, float))
            ):
                raise AnalysisManifestFinalizationError(
                    "analysis_finalization_floor_dependency_unsatisfied",
                    f"transport group does not satisfy the complete selector for {condition_id}",
                )
            direct = [
                cell
                for cell in cells
                if isinstance(cell.get("key"), Mapping)
                and cell["key"].get("backend") == expected_backend
                and cell["key"].get("metric") == selector["metric"]
                and cell["key"].get("window_class") == selector["window_class"]
                and cell["key"].get("condition_family_id") == condition_id
                and cell["key"].get("condition_family_sha256")
                == condition_shas[condition_id]
                and cell.get("transport_group_id")
                == binding["transport_group_id"]
                and isinstance(cell.get("source_regime"), Mapping)
                and cell["source_regime"].get("stack_identity_sha256")
                == expected_stack_sha
                and isinstance(cell.get("eligibility"), Mapping)
                and cell["eligibility"].get("claim_usable") is True
                and not isinstance(cell.get(selector["floor_field"]), bool)
                and isinstance(cell.get(selector["floor_field"]), (int, float))
            ]
            if transport["mode"] == "exact_stack_only" and len(direct) != 1:
                raise AnalysisManifestFinalizationError(
                    "analysis_finalization_floor_dependency_unsatisfied",
                    f"exact-stack floor cell is absent or ambiguous for {condition_id}",
                )


def _authenticate_finalization_inputs(
    prospective: Mapping[str, Any],
    *,
    manifest_dir: Path,
    custody_root: Path,
    runs_root: Path,
    whole_window_verdict_path: Path,
    bracket_binding_path: Path,
    calibration_ledger_path: Path,
    aggregate_floor_artifact_path: Path,
) -> dict[str, Any]:
    schemas = _declared_attachment_schemas(prospective)
    custody_input = Path(custody_root).absolute()
    custody = custody_input.resolve(strict=True)
    resolved_runs = _directory_under_root(runs_root, custody_input, "runs root")

    verdict_path, verdict_relative = _path_under_root(
        whole_window_verdict_path, custody_input, "whole-window verdict"
    )
    verdict, verdict_raw = _read_strict_object(verdict_path, "whole-window verdict")
    if (
        schemas.get("whole_window_verdict") != _WHOLE_WINDOW_SCHEMA
        or verdict.get("schema_version") != schemas.get("whole_window_verdict")
        or verdict.get("record_type") != "idle_admission_whole_window_verdict"
    ):
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            "whole-window verdict schema/role mismatch",
        )
    if verdict.get("status") != "passed" or verdict.get("claim_licensing") is not True:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_verdict_not_passed",
            "whole-window verdict must be claim-licensing and passed",
        )
    basis, bundle_paths = _verify_basis_members(
        prospective,
        verdict,
        manifest_dir=manifest_dir,
        runs_root=resolved_runs,
    )

    bracket_path, bracket_relative = _path_under_root(
        bracket_binding_path, custody_input, "bracket binding"
    )
    bracket, bracket_raw = _read_strict_object(bracket_path, "bracket binding")
    try:
        bracket_runs_root = (
            _directory_under_root(
                Path(bracket["runs_root"]),
                custody_input,
                "bracket-authenticated runs root",
            )
            if isinstance(bracket.get("runs_root"), str)
            else None
        )
    except (KeyError, AnalysisManifestFinalizationError) as exc:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_bracket_binding_mismatch",
            f"bracket runs root is not a canonical non-symlink directory: {exc}",
        ) from exc
    if (
        schemas.get("bracket_binding") != _BRACKET_BINDING_SCHEMA
        or bracket.get("schema_version") != schemas.get("bracket_binding")
        or bracket.get("plan_id") != prospective["plan"]["plan_id"]
        or bracket.get("plan_sha256") != prospective["plan"]["sha256"]
        or bracket.get("evidence_root_id") != prospective["evidence_root_id"]
        or bracket_runs_root != resolved_runs
        or bracket.get("binding_digest")
        != _canonical_sha(
            {key: value for key, value in bracket.items() if key != "binding_digest"}
        )
    ):
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_bracket_binding_mismatch",
            "bracket binding does not authenticate the frozen plan/root/session",
        )

    ledger_path, ledger_relative = _path_under_root(
        calibration_ledger_path, custody_input, "calibration ledger"
    )
    ledger_raw = ledger_path.read_bytes()
    if schemas.get("calibration_ledger") != _LEDGER_SCHEMA:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            "calibration-ledger schema declaration is unsupported",
        )
    head_pin_path, _head_pin_relative = _path_under_root(
        ledger_path.with_name("calibration_ledger_head.json"),
        custody_input,
        "calibration ledger head pin",
    )
    try:
        from joulewise.calibration_ledger import (
            canonical_json_bytes as calibration_ledger_canonical_json_bytes,
            load_calibration_ledger_snapshot,
            terminal_head_pin_for_session,
        )

        terminal_head = terminal_head_pin_for_session(
            ledger_path, session_id=str(bracket.get("session_id"))
        )
    except Exception as exc:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_ledger_head_mismatch",
            f"calibration ledger has no authenticated terminal session head: {exc}",
        ) from exc
    if terminal_head != bracket.get("terminal_head"):
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_ledger_head_mismatch",
            "bracket terminal head is not the actual ledger terminal head",
        )
    snapshot = load_calibration_ledger_snapshot(
        ledger_path,
        head_pin_path,
        require_committed_pin=False,
        verify_custody=True,
    )
    if snapshot.refusal_reasons:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_ledger_head_mismatch",
            "calibration ledger snapshot refused: "
            + ", ".join(snapshot.refusal_reasons),
        )
    try:
        from joulewise.calibration_bracketing import (
            validate_calibration_bracket_binding,
        )

        bracket_pair = validate_calibration_bracket_binding(
            bracket,
            snapshot,
            window_id=str(bracket.get("window_id")),
            plan_id=prospective["plan"]["plan_id"],
            plan_sha256=prospective["plan"]["sha256"],
            evidence_root_id=prospective["evidence_root_id"],
            # The authoritative validator binds the recorded path spelling;
            # lexical safety/equality was established above without erasing it.
            runs_root=Path(bracket["runs_root"]),
        )
    except (KeyError, OSError, RuntimeError, TypeError, ValueError) as exc:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_bracket_binding_mismatch",
            f"authoritative bracket validation failed: {exc}",
        ) from exc
    if bracket_pair is None:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_bracket_binding_mismatch",
            "authoritative bracket validator rejected the binding",
        )

    try:
        from joulewise.schemas import CampaignPolicy
        from joulewise.whole_window import (
            AuthenticatedConsumptionSession,
            _registered_policy,
            whole_window_refusal_reasons,
        )

        policy_record = verdict.get("campaign_policy")
        policy_sha = (
            policy_record.get("sha256")
            if isinstance(policy_record, Mapping)
            else None
        )
        registered_policy = _registered_policy(policy_sha)
        if not isinstance(registered_policy, Mapping):
            raise ValueError("campaign policy is not registered")
        policy = CampaignPolicy.from_mapping(dict(registered_policy))
        semantics_id = basis.get("consumption_semantics_id")
        session = AuthenticatedConsumptionSession(
            resolved_runs,
            set(bundle_paths),
            evaluation_basis_sha256=str(basis["sha256"]),
            consumption_semantics_id=str(semantics_id),
            calibration_ledger_snapshot=snapshot,
        )
        session._prepare(bundle_paths=bundle_paths, policy=policy)
        verdict_reasons = whole_window_refusal_reasons(
            resolved_runs,
            set(bundle_paths),
            evaluation_basis_sha256=str(basis["sha256"]),
            consumption_session=session,
            consumption_semantics_id=str(semantics_id),
        )
    except (KeyError, OSError, RuntimeError, TypeError, ValueError) as exc:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            f"authoritative whole-window validation failed: {exc}",
        ) from exc
    evaluated_bracket_binding = session._basis_bracket_binding()
    if not isinstance(evaluated_bracket_binding, Mapping):
        # Older evaluation bases can omit endpoint selectors. The parsed binding
        # was already rejoined above to the prospective identity and unique
        # authenticated ledger session, so it is the same canonical object.
        evaluated_bracket_binding = bracket
    if (
        bracket_raw
        != calibration_ledger_canonical_json_bytes(evaluated_bracket_binding)
        + b"\n"
    ):
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_bracket_binding_mismatch",
            "bracket binding bytes are not canonical / differ from the evaluated binding",
        )
    if verdict_reasons:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            "authoritative whole-window validator refused: "
            + ", ".join(verdict_reasons),
        )
    try:
        campaign_rows = [
            _strict_json_bytes(line.encode("utf-8"), "campaign-log verdict")
            for line in (resolved_runs / "campaign_log.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
    except (OSError, UnicodeDecodeError, AnalysisManifestFinalizationError) as exc:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            f"whole-window campaign log is unreadable: {exc}",
        ) from exc
    matching_rows = [
        row
        for row in campaign_rows
        if isinstance(row, Mapping)
        and row.get("record_type") == "idle_admission_whole_window_verdict"
        and canonical_json_bytes(row) == canonical_json_bytes(verdict)
    ]
    if len(matching_rows) != 1:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            "whole-window attachment is not exactly one authoritative campaign-log row",
        )

    floor_path, floor_relative = _path_under_root(
        aggregate_floor_artifact_path, custody_input, "aggregate floor artifact"
    )
    floor, floor_raw = _read_strict_object(floor_path, "aggregate floor artifact")
    if (
        schemas.get("aggregate_floor_artifact") != _FLOOR_SCHEMA
        or floor.get("schema_version") != schemas.get("aggregate_floor_artifact")
        or not isinstance(floor.get("artifact_id"), str)
        or not floor.get("artifact_id")
    ):
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_floor_dependency_unsatisfied",
            "aggregate floor artifact schema/identity is invalid",
        )
    try:
        from joulewise.detection_floor import validate_floor_artifact

        floor_errors = validate_floor_artifact(floor)
    except Exception as exc:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_floor_dependency_unsatisfied",
            f"aggregate floor artifact validation failed: {exc}",
        ) from exc
    if floor_errors:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_floor_dependency_unsatisfied",
            "aggregate floor artifact is invalid: " + "; ".join(floor_errors),
        )
    if any(
        contrast["floor_dependency"]["required_artifact_schema"]
        != floor.get("schema_version")
        for contrast in prospective["contrasts"]
    ):
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_floor_dependency_unsatisfied",
            "aggregate floor artifact schema does not satisfy the frozen dependency",
        )
    _authenticate_floor_dependencies(
        prospective,
        floor,
        bundle_paths=bundle_paths,
    )

    arms, entries, blocks = _derive_arms_and_entries(
        prospective,
        manifest_dir=manifest_dir,
        runs_root=resolved_runs,
        bundle_paths=bundle_paths,
    )
    return {
        "runs_root": resolved_runs,
        "arms": arms,
        "entries": entries,
        "blocks": blocks,
        "whole_window_verdict": {
            "path": verdict_relative,
            "sha256": hashlib.sha256(verdict_raw).hexdigest(),
            "schema_version": verdict["schema_version"],
            "status": verdict["status"],
            "evaluation_basis_sha256": basis["sha256"],
        },
        "bracket_binding": {
            "path": bracket_relative,
            "sha256": hashlib.sha256(bracket_raw).hexdigest(),
            "schema_version": bracket["schema_version"],
            "binding_digest": bracket["binding_digest"],
            "session_id": bracket["session_id"],
        },
        "calibration_ledger": {
            "path": ledger_relative,
            "sha256": hashlib.sha256(ledger_raw).hexdigest(),
            "schema_version": schemas["calibration_ledger"],
            "terminal_head": terminal_head,
        },
        "aggregate_floor_artifact": {
            "path": floor_relative,
            "sha256": hashlib.sha256(floor_raw).hexdigest(),
            "schema_version": floor["schema_version"],
            "artifact_id": floor["artifact_id"],
        },
    }


def _build_finalized_manifest(
    prospective: Mapping[str, Any],
    *,
    prospective_relative: str,
    prospective_sha256: str,
    plan_tree_relative: str,
    plan_tree_sha256: str,
    attachments: Mapping[str, Any],
) -> dict[str, Any]:
    family_by_id = {
        row["family_instance_id"]: row for row in prospective["families"]
    }
    arm_by_slot = {
        tuple(row["arm_id"].split(":", 1)): row for row in attachments["arms"]
    }
    contrasts: list[dict[str, Any]] = []
    for source in prospective["contrasts"]:
        family = family_by_id[source["family_instance_id"]]
        arm_a = arm_by_slot[(source["measurement_arm"], "A")]
        arm_b = arm_by_slot[(source["measurement_arm"], "B")]
        contrasts.append(
            {
                "contrast_id": source["contrast_id"],
                "plan_id": prospective["plan"]["plan_id"],
                "family_instance_id": source["family_instance_id"],
                "claim_role": source["claim_role"],
                "metric": {
                    "name": source["metric"],
                    "metric_tag": source["metric_tag"],
                    "window_class": source["target_precheck_path"][0],
                    "unit": "J",
                    "ratio_estimand": None,
                },
                "estimator": source["point_estimator"],
                "condition_a_id": source["condition_a_id"],
                "condition_b_id": source["condition_b_id"],
                "cell_a_id": arm_a["cell_id"],
                "cell_b_id": arm_b["cell_id"],
                "block_ids": list(source["block_ids"]),
                "sidedness": source["test"],
                "hypothesized_direction": source[
                    "scientific_hypothesis_direction"
                ],
                "equivalence": json.loads(json.dumps(source["equivalence"])),
                "mde": source["mde"],
                "floor_selector": json.loads(
                    json.dumps(source["floor_dependency"]["floor_selector"])
                ),
                "measurement_arm": source["measurement_arm"],
                "target_precheck_path": list(source["target_precheck_path"]),
                "difference_orientation": source["difference_orientation"],
                "floor_estimator_registration": json.loads(
                    json.dumps(source["floor_estimator_registration"])
                ),
                "floor_dependency": json.loads(
                    json.dumps(source["floor_dependency"])
                ),
                "prompt": json.loads(json.dumps(source["prompt"])),
            }
        )
    prospective_semantics_sha = analysis_semantics_sha256_v1(prospective)
    manifest: dict[str, Any] = {
        "schema_version": FINALIZED_SCHEMA_VERSION,
        "manifest_id": "",
        "freeze_status": "finalized",
        "lineage": {
            "prospective_manifest_id": prospective["manifest_id"],
            "prospective_manifest_path": prospective_relative,
            "prospective_manifest_sha256": prospective_sha256,
            "plan_tree_path": plan_tree_relative,
            "plan_tree_sha256": plan_tree_sha256,
            # Collection records are authored before a finalized identity can
            # exist, so their lookup identity remains the prospective ID.
            "collection_manifest_id": prospective["manifest_id"],
            "projection_rule_id": SEMANTICS_PROJECTION_RULE_ID,
            "prospective_semantics_sha256": prospective_semantics_sha,
            "finalized_semantics_sha256": "",
        },
        "condition_families": json.loads(
            json.dumps(prospective["condition_families"])
        ),
        "design": json.loads(json.dumps(prospective["design"])),
        "replacement_policy": json.loads(
            json.dumps(prospective["replacement_policy"])
        ),
        "arms": json.loads(json.dumps(attachments["arms"])),
        "entries": json.loads(json.dumps(attachments["entries"])),
        "blocks": json.loads(json.dumps(attachments["blocks"])),
        "families": json.loads(json.dumps(prospective["families"])),
        "contrasts": contrasts,
        "finalization_contract": json.loads(
            json.dumps(prospective["finalization_contract"])
        ),
        "evidence": {
            role: json.loads(json.dumps(attachments[role]))
            for role in sorted(_REQUIRED_ATTACHMENT_ROLES)
        },
    }
    finalized_semantics_sha = analysis_semantics_sha256_v1(manifest)
    if finalized_semantics_sha != prospective_semantics_sha:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_semantics_mismatch",
            "finalized consumer projection does not equal frozen prospective semantics",
        )
    manifest["lineage"]["finalized_semantics_sha256"] = finalized_semantics_sha
    manifest["manifest_id"] = calculate_manifest_id(manifest)
    return manifest


def _write_append_only(path: Path, raw: bytes) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.is_file() and not path.is_symlink() and path.read_bytes() == raw:
            return
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_output_conflict",
            f"occupied finalized namespace differs: {path}",
        )
    handle = tempfile.NamedTemporaryFile(
        "wb", dir=path.parent, prefix=f".{path.name}.", delete=False
    )
    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if path.is_file() and not path.is_symlink() and path.read_bytes() == raw:
                return
            raise AnalysisManifestFinalizationError(
                "analysis_finalization_output_conflict",
                f"concurrent finalized namespace differs: {path}",
            )
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def finalize_prospective_analysis_manifest_v3(
    prospective_manifest_path: Path,
    *,
    plan_tree_path: Path,
    custody_root: Path,
    runs_root: Path,
    whole_window_verdict_path: Path,
    bracket_binding_path: Path,
    calibration_ledger_path: Path,
    aggregate_floor_artifact_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """Derive one immutable finalized artifact without reading an effect value."""

    try:
        custody_input = Path(custody_root).absolute()
        custody = Path(custody_root).resolve(strict=True)
        output = Path(output_dir).resolve(strict=True)
    except OSError as exc:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_input_unreadable",
            f"custody/output root is unavailable: {exc}",
        ) from exc
    if output != custody:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_noncanonical",
            "output_dir must equal custody_root so consumer-relative lineage is stable",
        )
    prospective_path, prospective_relative = _path_under_root(
        prospective_manifest_path, custody_input, "prospective manifest"
    )
    tree_path, tree_relative = _path_under_root(
        plan_tree_path, custody_input, "plan tree"
    )
    prospective, prospective_raw = _read_strict_object(
        prospective_path, "prospective analysis manifest"
    )
    refusals = validate_prospective_analysis_manifest_v3(
        prospective,
        manifest_dir=prospective_path.parent,
        plan_tree_path=tree_path,
    )
    if refusals:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_prospective_invalid",
            "; ".join(f"{item.reason_code}: {item.detail}" for item in refusals),
        )
    attachments = _authenticate_finalization_inputs(
        prospective,
        manifest_dir=prospective_path.parent,
        custody_root=custody_input,
        runs_root=runs_root,
        whole_window_verdict_path=whole_window_verdict_path,
        bracket_binding_path=bracket_binding_path,
        calibration_ledger_path=calibration_ledger_path,
        aggregate_floor_artifact_path=aggregate_floor_artifact_path,
    )
    tree_raw = tree_path.read_bytes()
    manifest = _build_finalized_manifest(
        prospective,
        prospective_relative=prospective_relative,
        prospective_sha256=hashlib.sha256(prospective_raw).hexdigest(),
        plan_tree_relative=tree_relative,
        plan_tree_sha256=hashlib.sha256(tree_raw).hexdigest(),
        attachments=attachments,
    )
    filename = f"{prospective['manifest_id']}{FINALIZED_BASENAME_SUFFIX}"
    path = output / filename
    raw = render_manifest(manifest)
    refusals = validate_finalized_analysis_manifest_v3(
        manifest, manifest_path=path, custody_root=custody_input
    )
    if refusals:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_noncanonical",
            "; ".join(f"{item.reason_code}: {item.detail}" for item in refusals),
        )
    _write_append_only(path, raw)
    return manifest


def _validate_finalized_analysis_manifest_v3_unchecked(
    value: Mapping[str, Any],
    *,
    manifest_path: Path,
    custody_root: Path,
) -> tuple[ManifestRefusal, ...]:
    """Validate a finalized artifact and independently replay its lineage."""

    refusals: list[ManifestRefusal] = []
    if not _exact_refusal_keys(
        value,
        _FINALIZED_TOP_KEYS,
        "manifest",
        refusals,
        schema_code="analysis_manifest_finalized_invalid",
        unknown_code="analysis_manifest_finalized_invalid",
    ):
        return tuple(refusals)
    if (
        value.get("schema_version") != FINALIZED_SCHEMA_VERSION
        or value.get("freeze_status") != "finalized"
    ):
        _refusal(
            refusals,
            "analysis_manifest_finalized_invalid",
            "schema_version/freeze_status is not finalized v3",
        )
    lineage = value.get("lineage")
    if not _exact_refusal_keys(
        lineage,
        _FINALIZED_LINEAGE_KEYS,
        "manifest.lineage",
        refusals,
        schema_code="analysis_manifest_lineage_mismatch",
        unknown_code="analysis_manifest_finalized_invalid",
    ):
        return tuple(refusals)
    assert isinstance(lineage, Mapping)
    custody = Path(custody_root)
    prospective_path = _safe_relative_file(
        custody, lineage.get("prospective_manifest_path")
    )
    tree_path = _safe_relative_file(custody, lineage.get("plan_tree_path"))
    if prospective_path is None or tree_path is None:
        _refusal(
            refusals,
            "analysis_manifest_lineage_mismatch",
            "prospective/plan-tree lineage path is unsafe or missing",
        )
        return tuple(refusals)
    prospective_raw = prospective_path.read_bytes()
    tree_raw = tree_path.read_bytes()
    try:
        prospective = _strict_json_bytes(
            prospective_raw, "finalized prospective lineage"
        )
    except AnalysisManifestFinalizationError:
        prospective = None
    if (
        not isinstance(prospective, Mapping)
        or hashlib.sha256(prospective_raw).hexdigest()
        != lineage.get("prospective_manifest_sha256")
        or prospective.get("manifest_id")
        != lineage.get("prospective_manifest_id")
        or hashlib.sha256(tree_raw).hexdigest()
        != lineage.get("plan_tree_sha256")
    ):
        _refusal(
            refusals,
            "analysis_manifest_lineage_mismatch",
            "prospective or plan-tree bytes differ from finalized lineage",
        )
        return tuple(refusals)
    prospective_refusals = validate_prospective_analysis_manifest_v3(
        prospective,
        manifest_dir=prospective_path.parent,
        plan_tree_path=tree_path,
    )
    prospective_internal = next(
        (
            item
            for item in prospective_refusals
            if item.reason_code == PROSPECTIVE_INTERNAL_ERROR_CODE
        ),
        None,
    )
    if prospective_internal is not None:
        if prospective_internal.cause is not None:
            raise prospective_internal.cause
        raise RuntimeError(prospective_internal.detail)
    if prospective_refusals:
        _refusal(
            refusals,
            "analysis_manifest_lineage_mismatch",
            "; ".join(
                f"{item.reason_code}: {item.detail}"
                for item in prospective_refusals
            ),
        )
        return tuple(refusals)
    if (
        lineage.get("collection_manifest_id") != prospective["manifest_id"]
        or lineage.get("projection_rule_id") != SEMANTICS_PROJECTION_RULE_ID
    ):
        _refusal(
            refusals,
            "analysis_manifest_collection_identity_mismatch",
            "collection lookup identity/projection rule differs from prospective authority",
        )

    finalized_families = value.get("families")
    if isinstance(finalized_families, list):
        for family in finalized_families:
            contrast_ids = (
                family.get("contrast_ids")
                if isinstance(family, Mapping)
                else None
            )
            family_id = (
                family.get("family_instance_id")
                if isinstance(family, Mapping)
                else None
            )
            if not isinstance(contrast_ids, list) or len(contrast_ids) <= 1:
                continue
            if not isinstance(family_id, str):
                _refusal(
                    refusals,
                    "analysis_manifest_family_semantics_mismatch",
                    "multi-contrast family lacks a frozen identity",
                )
                continue
            try:
                frozen_family_block_strata(value, family_id)
            except AnalysisManifestV3Error as exc:
                _refusal(
                    refusals,
                    "analysis_manifest_family_semantics_mismatch",
                    f"multi-contrast family lacks complete frozen block strata: {exc}",
                )

    evidence = value.get("evidence")
    if not _exact_refusal_keys(
        evidence,
        _FINALIZED_EVIDENCE_KEYS,
        "manifest.evidence",
        refusals,
        schema_code="analysis_manifest_finalized_invalid",
        unknown_code="analysis_manifest_finalized_invalid",
    ):
        return tuple(refusals)
    assert isinstance(evidence, Mapping)
    for role, keys in (
        ("whole_window_verdict", _FINALIZED_WHOLE_WINDOW_KEYS),
        ("bracket_binding", _FINALIZED_BRACKET_KEYS),
        ("calibration_ledger", _FINALIZED_LEDGER_KEYS),
        ("aggregate_floor_artifact", _FINALIZED_FLOOR_KEYS),
    ):
        if not _exact_refusal_keys(
            evidence.get(role),
            keys,
            f"manifest.evidence.{role}",
            refusals,
            schema_code="analysis_manifest_finalized_invalid",
            unknown_code="analysis_manifest_finalized_invalid",
        ):
            return tuple(refusals)
    bracket_ref = evidence["bracket_binding"]
    bracket_path = _safe_relative_file(custody, bracket_ref["path"])
    if bracket_path is None:
        _refusal(
            refusals,
            "analysis_manifest_lineage_mismatch",
            "bracket binding path is unsafe or missing",
        )
        return tuple(refusals)
    try:
        bracket = _strict_json_bytes(
            bracket_path.read_bytes(), "finalized bracket lineage"
        )
        if not isinstance(bracket, Mapping) or not isinstance(
            bracket.get("runs_root"), str
        ):
            raise AnalysisManifestFinalizationError(
                "analysis_finalization_bracket_binding_mismatch",
                "bracket binding runs_root must be a string",
            )
        runs_root = Path(bracket["runs_root"])
        attachments = _authenticate_finalization_inputs(
            prospective,
            manifest_dir=prospective_path.parent,
            custody_root=custody,
            runs_root=runs_root,
            whole_window_verdict_path=custody / evidence["whole_window_verdict"]["path"],
            bracket_binding_path=bracket_path,
            calibration_ledger_path=custody / evidence["calibration_ledger"]["path"],
            aggregate_floor_artifact_path=custody
            / evidence["aggregate_floor_artifact"]["path"],
        )
    except AnalysisManifestFinalizationError as exc:
        reason = (
            "analysis_manifest_floor_attachment_mismatch"
            if "floor" in str(exc)
            else "analysis_manifest_lineage_mismatch"
        )
        _refusal(refusals, reason, f"attachment replay refused: {exc}")
        return tuple(refusals)
    expected = _build_finalized_manifest(
        prospective,
        prospective_relative=lineage["prospective_manifest_path"],
        prospective_sha256=lineage["prospective_manifest_sha256"],
        plan_tree_relative=lineage["plan_tree_path"],
        plan_tree_sha256=lineage["plan_tree_sha256"],
        attachments=attachments,
    )
    if expected != value:
        expected_semantics = analysis_semantics_sha256_v1(expected)
        observed_semantics = analysis_semantics_sha256_v1(value)
        if expected_semantics != observed_semantics:
            _refusal(
                refusals,
                "analysis_manifest_family_semantics_mismatch",
                "finalized semantic projection differs from the prospective projection",
            )
        else:
            _refusal(
                refusals,
                "analysis_manifest_lineage_mismatch",
                "finalized consumer projection/evidence lineage is not deterministic",
            )
    if (
        lineage.get("prospective_semantics_sha256")
        != prospective["frozen_semantics_sha256"]
        or lineage.get("finalized_semantics_sha256")
        != analysis_semantics_sha256_v1(value)
        or lineage.get("prospective_semantics_sha256")
        != lineage.get("finalized_semantics_sha256")
    ):
        _refusal(
            refusals,
            "analysis_manifest_family_semantics_mismatch",
            "stored semantic hashes do not match independently recomputed projections",
        )
    if value.get("manifest_id") != calculate_manifest_id(value):
        _refusal(
            refusals,
            "analysis_manifest_finalized_invalid",
            "finalized manifest identity is not content-derived",
        )
    expected_name = f"{prospective['manifest_id']}{FINALIZED_BASENAME_SUFFIX}"
    if Path(manifest_path).name != expected_name:
        _refusal(
            refusals,
            "analysis_manifest_lineage_mismatch",
            "finalized manifest occupies the wrong deterministic namespace",
        )
    return tuple(refusals)


def validate_finalized_analysis_manifest_v3(
    value: Mapping[str, Any],
    *,
    manifest_path: Path,
    custody_root: Path,
) -> tuple[ManifestRefusal, ...]:
    """Total boundary with region-based malformed/defect classification."""

    try:
        _walk_finalized_input(value)
    except _ManifestInputWalkError as exc:
        return (
            ManifestRefusal(
                FINALIZED_MALFORMED_VALUE_CODE,
                f"malformed finalized value at {exc.path}: expected "
                f"{exc.expected}, got {exc.observed_type}",
                cause=exc,
            ),
        )
    except _INPUT_MALFORMATION_EXCEPTIONS as exc:
        return (
            ManifestRefusal(
                FINALIZED_MALFORMED_VALUE_CODE,
                "malformed finalized value during input walk: "
                f"{type(exc).__name__}: {exc}",
                cause=exc,
            ),
        )
    except Exception as exc:
        return (
            ManifestRefusal(
                FINALIZED_INTERNAL_ERROR_CODE,
                "finalized input-walk internal defect: "
                f"{type(exc).__name__}: {exc}",
                cause=exc,
            ),
        )

    try:
        return _validate_finalized_analysis_manifest_v3_unchecked(
            value,
            manifest_path=manifest_path,
            custody_root=custody_root,
        )
    except Exception as exc:
        return (
            ManifestRefusal(
                FINALIZED_INTERNAL_ERROR_CODE,
                f"finalized validator internal defect: {type(exc).__name__}: {exc}",
                cause=exc,
            ),
        )


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
    "AnalysisManifestFinalizationError",
    "AnalysisManifestV3Error",
    "CALIBRATION_PLAN_SHA256",
    "ESTIMATOR_ID",
    "EXACT_STACK_RULE_ID",
    "FLOOR_RULE_ID",
    "GOVERNED_TRANSPORT_RULE_ID",
    "FINALIZATION_CONTRACT_ID",
    "FINALIZED_BASENAME_SUFFIX",
    "FINALIZED_INTERNAL_ERROR_CODE",
    "FINALIZED_MALFORMED_VALUE_CODE",
    "FINALIZED_NAMESPACE_RULE_ID",
    "FINALIZED_REFUSAL_CODES",
    "FINALIZED_SCHEMA_VERSION",
    "MANIFEST_NAME",
    "ManifestRefusal",
    "PLANNED_N_BLOCKS",
    "PROSPECTIVE_SCHEMA_VERSION",
    "PROSPECTIVE_INTERNAL_ERROR_CODE",
    "PROSPECTIVE_MALFORMED_VALUE_CODE",
    "PROSPECTIVE_REFUSAL_CODES",
    "SCHEMA_VERSION",
    "SEMANTICS_PROJECTION_RULE_ID",
    "STAGE_ORDER_SHA256S",
    "TRANSPORT_RULING_PENDING_REFUSAL",
    "VERDICT_BASIS_SHA256",
    "analysis_semantics_projection_v1",
    "analysis_semantics_sha256_v1",
    "build_analysis_manifest_v3",
    "build_prospective_analysis_manifest_v3",
    "calculate_manifest_id",
    "canonical_json_bytes",
    "finalize_prospective_analysis_manifest_v3",
    "frozen_family_block_strata",
    "is_abba_v3_consumable_schema",
    "normalized_realized_stack_identity",
    "render_manifest",
    "validate_analysis_manifest_v3",
    "validate_finalized_analysis_manifest_v3",
    "validate_prospective_analysis_manifest_v3",
    "write_manifest_atomic",
]
