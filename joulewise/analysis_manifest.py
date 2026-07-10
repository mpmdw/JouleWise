"""Frozen Slice-2M analysis-manifest construction and validation.

The module is intentionally stdlib-only.  It owns semantic identifiers,
canonical manifest identity, AP-2/registry linkage, and validation of the
generated config and order-manifest bytes.  It does not consume bundles or
perform statistical analysis.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "joulewise.analysis_manifest.v1"
REGISTRY_SCHEMA_VERSION = "joulewise.analysis_registry.v1"
ANALYSIS_MANIFEST_NAME = "analysis_manifest.json"
ORDER_MANIFEST_NAME = "order_manifest.json"
REGISTRY_RELATIVE_PATH = Path("configs/analysis_registry/slice_2m_ap2.v1.json")
AP_RELATIVE_PATH = Path("docs/contracts/analysis_plans.md")
ROOT = Path(__file__).resolve().parents[1]

PROFILE_NAMES = ("short_short", "long_short", "short_long", "mid_mid")
SENTINEL_WORKLOAD = "short_short_sentinel"
ENTRY_ROLES = {"condition", "drift_sentinel_start", "drift_sentinel_end"}
ID_RE = re.compile(r"^[a-z0-9_-]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MANIFEST_ID_RE = re.compile(r"^am-[0-9a-f]{64}$")

TOP_KEYS = {
    "schema_version",
    "manifest_id",
    "freeze_status",
    "design",
    "source",
    "entries",
    "sentinel_links",
    "families",
    "contrasts",
}
DESIGN_KEYS = {
    "design_id",
    "analysis_plan_ids",
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
RANDOMIZATION_KEYS = {"scheme", "exchangeability", "seed"}
SOURCE_KEYS = {"generator", "registry_template", "order_manifest", "ap_rows"}
SOURCE_FILE_KEYS = {"path", "sha256"}
AP_ROW_KEYS = {
    "plan_id",
    "path",
    "section_sha256",
    "family_id",
    "claim_role",
    "selection_scope",
    "multiplicity_rule",
}
ENTRY_KEYS = {
    "entry_id",
    "config",
    "config_sha256",
    "run_id",
    "model_tag",
    "planned_rep_index",
    "role",
    "condition_id",
    "cell_id",
    "block_id",
    "sentinel_link_id",
    "order_index",
    "position_in_block",
}
SENTINEL_LINK_KEYS = {
    "sentinel_link_id",
    "block_id",
    "start_entry_id",
    "end_entry_id",
    "linked_condition_entry_ids",
    "diagnostic",
}
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
}
REGISTRY_KEYS = {
    "schema_version",
    "registry_id",
    "plan_id",
    "family_id",
    "claim_role",
    "multiplicity",
    "metrics",
    "condition_pairs",
}
REGISTRY_MULTIPLICITY_KEYS = {"method", "alpha", "q"}
REGISTRY_PAIR_KEYS = {"condition_a", "condition_b"}


class AnalysisManifestError(ValueError):
    """Raised when a registry or generated manifest is invalid."""


@dataclass(frozen=True)
class AnalysisRegistry:
    path: Path
    raw_bytes: bytes
    value: Mapping[str, Any]


@dataclass(frozen=True)
class AnalysisPlanRow:
    path: Path
    raw_section: bytes
    values: Mapping[str, str]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def calculate_manifest_id(value: Mapping[str, Any]) -> str:
    body = dict(value)
    body.pop("manifest_id", None)
    return "am-" + sha256_bytes(canonical_json_bytes(body))


def render_manifest(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _exact_keys(value: Any, expected: set[str], where: str, errors: list[str]) -> bool:
    if not isinstance(value, Mapping):
        errors.append(f"{where}: must be an object")
        return False
    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append(f"{where}: missing key(s): {', '.join(missing)}")
    if extra:
        errors.append(f"{where}: unrecognized key(s): {', '.join(extra)}")
    return not missing and not extra


def _parse_json_object(raw: bytes, where: str) -> Mapping[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AnalysisManifestError(f"{where}: invalid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, Mapping):
        raise AnalysisManifestError(f"{where}: top level must be an object")
    return value


def extract_analysis_plan_row(path: Path, plan_id: str = "AP-2") -> AnalysisPlanRow:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AnalysisManifestError(f"cannot read analysis plan {path}: {exc}") from exc
    lines = text.splitlines(keepends=True)
    heading = f"### {plan_id}"
    start = next(
        (
            i
            for i, line in enumerate(lines)
            if line.rstrip("\r\n") == heading
            or line.rstrip("\r\n").startswith(heading + ":")
        ),
        None,
    )
    if start is None:
        raise AnalysisManifestError(f"analysis plan has no {heading} section")
    table_start = None
    for index in range(start + 1, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("### "):
            break
        if stripped.startswith("| Field |"):
            table_start = index
            break
    if table_start is None or table_start + 2 >= len(lines):
        raise AnalysisManifestError(f"{heading} has no Field/Value table")
    end = table_start + 2
    while end < len(lines) and lines[end].lstrip().startswith("|"):
        end += 1
    section_text = "".join(lines[start:end])
    if not section_text.endswith("\n"):
        section_text += "\n"
    values: dict[str, str] = {}
    for line in lines[table_start + 2 : end]:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 2 or not cells[0]:
            raise AnalysisManifestError(f"malformed {heading} Field/Value row: {line.rstrip()}")
        if cells[0] in values:
            raise AnalysisManifestError(f"duplicate {heading} field: {cells[0]}")
        values[cells[0]] = cells[1]
    required = {"family_id", "claim_role", "selection_scope", "multiplicity_rule"}
    missing = sorted(required - set(values))
    if missing:
        raise AnalysisManifestError(f"{heading} missing field(s): {', '.join(missing)}")
    first_value = values.get("Plan ID / RQ consumer", "")
    if not first_value.startswith(f"{plan_id} /"):
        raise AnalysisManifestError(f"{heading} Plan ID row does not identify {plan_id}")
    return AnalysisPlanRow(path=path, raw_section=section_text.encode("utf-8"), values=values)


def validate_analysis_registry(
    value: Mapping[str, Any],
    *,
    ap_row: AnalysisPlanRow | None = None,
) -> list[str]:
    errors: list[str] = []
    if not _exact_keys(value, REGISTRY_KEYS, "registry", errors):
        return errors
    if value["schema_version"] != REGISTRY_SCHEMA_VERSION:
        errors.append(f"registry.schema_version: expected {REGISTRY_SCHEMA_VERSION!r}")
    if value["registry_id"] != "slice_2m_ap2_v1":
        errors.append("registry.registry_id: expected 'slice_2m_ap2_v1'")
    if value["plan_id"] != "AP-2":
        errors.append("registry.plan_id: expected 'AP-2'")
    if value["family_id"] != "FAM-2M-SHAPE-CONTRASTS":
        errors.append("registry.family_id: expected 'FAM-2M-SHAPE-CONTRASTS'")
    if value["claim_role"] != "primary":
        errors.append("registry.claim_role: expected 'primary'")
    multiplicity = value["multiplicity"]
    if _exact_keys(multiplicity, REGISTRY_MULTIPLICITY_KEYS, "registry.multiplicity", errors):
        if multiplicity != {"method": "holm", "alpha": 0.05, "q": None}:
            errors.append("registry.multiplicity: AP-2 v1 requires holm alpha=0.05 and q=null")
    metrics = value["metrics"]
    expected_metrics = (
        ("gross_request", "gross_energy_j", "request"),
        ("idle_request", "energy_request_j", "request"),
        ("gross_prefill", "phase_energy_j.prefill", "phase"),
        ("gross_decode", "phase_energy_j.decode", "phase"),
    )
    if not isinstance(metrics, list) or len(metrics) != 4:
        errors.append("registry.metrics: must contain the four frozen AP-2 metric rows")
    else:
        for index, (metric, expected) in enumerate(zip(metrics, expected_metrics, strict=True)):
            where = f"registry.metrics[{index}]"
            if _exact_keys(metric, METRIC_KEYS, where, errors):
                observed = (metric["metric_tag"], metric["name"], metric["window_class"])
                if observed != expected:
                    errors.append(f"{where}: unexpected metric identity/order {observed!r}")
                if metric["unit"] != "J" or metric["ratio_estimand"] is not None:
                    errors.append(f"{where}: AP-2 v1 requires unit J and ratio_estimand null")
    pairs = value["condition_pairs"]
    expected_pairs = (
        ("short_short", "long_short"),
        ("short_short", "short_long"),
        ("short_short", "mid_mid"),
        ("long_short", "short_long"),
        ("long_short", "mid_mid"),
        ("short_long", "mid_mid"),
    )
    if not isinstance(pairs, list) or len(pairs) != 6:
        errors.append("registry.condition_pairs: must contain the six frozen AP-2 pairs")
    else:
        for index, (pair, expected) in enumerate(zip(pairs, expected_pairs, strict=True)):
            where = f"registry.condition_pairs[{index}]"
            if _exact_keys(pair, REGISTRY_PAIR_KEYS, where, errors):
                observed = (pair["condition_a"], pair["condition_b"])
                if observed != expected:
                    errors.append(f"{where}: unexpected condition pair/order {observed!r}")
    if ap_row is not None:
        if value["plan_id"] != "AP-2":
            errors.append("registry.plan_id disagrees with AP-2")
        if value["family_id"] != ap_row.values["family_id"]:
            errors.append("registry.family_id disagrees with AP-2")
        if value["claim_role"] != ap_row.values["claim_role"]:
            errors.append("registry.claim_role disagrees with AP-2")
        if "holm" not in ap_row.values["multiplicity_rule"].lower():
            errors.append("registry multiplicity method disagrees with AP-2")
    return errors


def load_analysis_registry(path: Path, ap_path: Path) -> tuple[AnalysisRegistry, AnalysisPlanRow]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise AnalysisManifestError(f"cannot read analysis registry {path}: {exc}") from exc
    value = _parse_json_object(raw, str(path))
    ap_row = extract_analysis_plan_row(ap_path)
    errors = validate_analysis_registry(value, ap_row=ap_row)
    if errors:
        raise AnalysisManifestError("invalid analysis registry: " + "; ".join(errors))
    return AnalysisRegistry(path=path, raw_bytes=raw, value=value), ap_row


def _semantic_ids(model_tag: str, rep: int, workload: str, sentinel_position: str | None) -> dict[str, str]:
    rep_tag = f"r{rep:02d}"
    block_id = f"block-2m-{model_tag}-{rep_tag}"
    link_id = f"sentinel-2m-{model_tag}-{rep_tag}"
    if sentinel_position is None:
        return {
            "role": "condition",
            "condition_id": f"cond-2m-{workload}",
            "cell_id": f"cell-2m-{model_tag}-{workload}",
            "entry_id": f"entry-2m-{model_tag}-{rep_tag}-{workload}",
            "block_id": block_id,
            "sentinel_link_id": link_id,
        }
    return {
        "role": f"drift_sentinel_{sentinel_position}",
        "condition_id": f"cond-2m-drift-sentinel-{sentinel_position}",
        "cell_id": f"cell-2m-{model_tag}-drift-sentinel-{sentinel_position}",
        "entry_id": f"entry-2m-{model_tag}-{rep_tag}-drift-sentinel-{sentinel_position}",
        "block_id": block_id,
        "sentinel_link_id": link_id,
    }


def _build_entries(config_dir: Path, order: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = order.get("executed_order")
    if not isinstance(rows, list):
        raise AnalysisManifestError("order_manifest.executed_order must be an array")
    entries: list[dict[str, Any]] = []
    for row_index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise AnalysisManifestError(f"order_manifest.executed_order[{row_index}] must be an object")
        try:
            config_name = row["config"]
            model_tag = row["model_tag"]
            rep = row["rep"]
            workload = row["workload"]
            order_index = row["index"]
            position = row["position_in_block"]
        except KeyError as exc:
            raise AnalysisManifestError(f"order row {row_index} missing {exc.args[0]}") from exc
        sentinel_position = row.get("sentinel_position")
        ids = _semantic_ids(model_tag, rep, workload, sentinel_position)
        path = config_dir / config_name
        try:
            config_bytes = path.read_bytes()
            config = _parse_json_object(config_bytes, str(path))
        except OSError as exc:
            raise AnalysisManifestError(f"cannot read generated config {path}: {exc}") from exc
        entries.append(
            {
                "entry_id": ids["entry_id"],
                "config": config_name,
                "config_sha256": sha256_bytes(config_bytes),
                "run_id": config.get("run_id"),
                "model_tag": model_tag,
                "planned_rep_index": rep,
                "role": ids["role"],
                "condition_id": ids["condition_id"],
                "cell_id": ids["cell_id"],
                "block_id": ids["block_id"],
                "sentinel_link_id": ids["sentinel_link_id"],
                "order_index": order_index,
                "position_in_block": position,
            }
        )
    return entries


def _build_links(entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_block: dict[str, list[Mapping[str, Any]]] = {}
    for entry in entries:
        by_block.setdefault(entry["block_id"], []).append(entry)
    links: list[dict[str, Any]] = []
    for block_id in sorted(by_block):
        block = by_block[block_id]
        by_role = {entry["role"]: entry for entry in block}
        by_condition = {entry["condition_id"]: entry for entry in block}
        condition_ids = [f"cond-2m-{profile}" for profile in PROFILE_NAMES]
        try:
            start = by_role["drift_sentinel_start"]
            end = by_role["drift_sentinel_end"]
            linked = [by_condition[condition_id]["entry_id"] for condition_id in condition_ids]
        except KeyError as exc:
            raise AnalysisManifestError(f"{block_id} is missing required entry {exc.args[0]}") from exc
        links.append(
            {
                "sentinel_link_id": start["sentinel_link_id"],
                "block_id": block_id,
                "start_entry_id": start["entry_id"],
                "end_entry_id": end["entry_id"],
                "linked_condition_entry_ids": linked,
                "diagnostic": "end_minus_start",
            }
        )
    return links


def _build_families_and_contrasts(
    model_tags: Sequence[str],
    registry: Mapping[str, Any],
    planned_n_blocks: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    families: list[dict[str, Any]] = []
    contrasts: list[dict[str, Any]] = []
    for model_tag in sorted(model_tags):
        block_ids = [f"block-2m-{model_tag}-r{rep:02d}" for rep in range(1, planned_n_blocks + 1)]
        for metric in registry["metrics"]:
            metric_tag = metric["metric_tag"]
            family_instance_id = f"fam-2m-{model_tag}-{metric_tag}"
            family_contrast_ids: list[str] = []
            for pair in registry["condition_pairs"]:
                condition_a = pair["condition_a"]
                condition_b = pair["condition_b"]
                contrast_id = (
                    f"ctr-ap2-{model_tag}-{metric_tag}-{condition_b}-minus-{condition_a}"
                )
                family_contrast_ids.append(contrast_id)
                contrasts.append(
                    {
                        "contrast_id": contrast_id,
                        "plan_id": registry["plan_id"],
                        "family_instance_id": family_instance_id,
                        "claim_role": registry["claim_role"],
                        "metric": dict(metric),
                        "estimator": "paired_block_mean_difference_t_v1",
                        "condition_a_id": f"cond-2m-{condition_a}",
                        "condition_b_id": f"cond-2m-{condition_b}",
                        "cell_a_id": f"cell-2m-{model_tag}-{condition_a}",
                        "cell_b_id": f"cell-2m-{model_tag}-{condition_b}",
                        "block_ids": block_ids,
                        "hypothesized_direction": "two_sided",
                        "equivalence": None,
                        "mde": None,
                        "floor_selector": {
                            "backend": "from_bundle",
                            "metric": metric["name"],
                            "window_class": metric["window_class"],
                            "condition_family_ids": [
                                f"cond-2m-{condition_a}",
                                f"cond-2m-{condition_b}",
                            ],
                            "floor_field": "floor_gate_j",
                            "transport_rule_id": "same_stack_componentwise_worst_case.v1",
                        },
                    }
                )
            families.append(
                {
                    "family_id": registry["family_id"],
                    "family_instance_id": family_instance_id,
                    "plan_id": registry["plan_id"],
                    "claim_role": registry["claim_role"],
                    "metric_tag": metric_tag,
                    "multiplicity": {
                        **dict(registry["multiplicity"]),
                        "m": len(family_contrast_ids),
                    },
                    "contrast_ids": family_contrast_ids,
                }
            )
    return families, contrasts


def build_slice_2m_analysis_manifest(
    config_dir: Path,
    *,
    repository_root: Path = ROOT,
    registry_path: Path | None = None,
    ap_path: Path | None = None,
) -> dict[str, Any]:
    registry_path = registry_path or repository_root / REGISTRY_RELATIVE_PATH
    ap_path = ap_path or repository_root / AP_RELATIVE_PATH
    registry, ap_row = load_analysis_registry(registry_path, ap_path)
    order_path = config_dir / ORDER_MANIFEST_NAME
    try:
        order_bytes = order_path.read_bytes()
    except OSError as exc:
        raise AnalysisManifestError(f"cannot read order manifest {order_path}: {exc}") from exc
    order = _parse_json_object(order_bytes, str(order_path))
    if order.get("schema_version") != "joulewise.order_manifest.v1":
        raise AnalysisManifestError("order manifest schema_version is not joulewise.order_manifest.v1")
    entries = _build_entries(config_dir, order)
    model_tags = sorted({entry["model_tag"] for entry in entries})
    planned_n_blocks = 5
    families, contrasts = _build_families_and_contrasts(
        model_tags, registry.value, planned_n_blocks
    )
    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": "",
        "freeze_status": "frozen",
        "design": {
            "design_id": "slice_2m_ap2_v1",
            "analysis_plan_ids": ["AP-2"],
            "unit_of_analysis": "paired_block",
            "difference_orientation": "condition_b_minus_condition_a",
            "sampling_plan": {
                "design": "fixed_n",
                "planned_n_blocks": planned_n_blocks,
                "freeze_basis": "generator_design_before_bundle_execution",
                "allowed_replacement_reasons": [
                    "bundle_incomplete",
                    "run_failed",
                    "strict_invalid",
                    "unsupported_before_measurement",
                ],
            },
            "randomization": {
                "scheme": "deterministic_rotation",
                "exchangeability": "none",
                "seed": order.get("seed"),
            },
        },
        "source": {
            "generator": "scripts/generate_matrix.py",
            "registry_template": {
                "path": REGISTRY_RELATIVE_PATH.as_posix(),
                "sha256": sha256_bytes(registry.raw_bytes),
            },
            "order_manifest": {
                "path": ORDER_MANIFEST_NAME,
                "sha256": sha256_bytes(order_bytes),
            },
            "ap_rows": [
                {
                    "plan_id": "AP-2",
                    "path": AP_RELATIVE_PATH.as_posix(),
                    "section_sha256": sha256_bytes(ap_row.raw_section),
                    "family_id": ap_row.values["family_id"],
                    "claim_role": ap_row.values["claim_role"],
                    "selection_scope": ap_row.values["selection_scope"],
                    "multiplicity_rule": ap_row.values["multiplicity_rule"],
                }
            ],
        },
        "entries": entries,
        "sentinel_links": _build_links(entries),
        "families": families,
        "contrasts": contrasts,
    }
    manifest["manifest_id"] = calculate_manifest_id(manifest)
    errors = validate_analysis_manifest(
        manifest,
        manifest_dir=config_dir,
        repository_root=repository_root,
        registry_path=registry_path,
        ap_path=ap_path,
    )
    if errors:
        raise AnalysisManifestError("built analysis manifest is invalid: " + "; ".join(errors))
    return manifest


def _validate_entry_semantics(entry: Mapping[str, Any], index: int, errors: list[str]) -> None:
    where = f"entries[{index}]"
    if not _exact_keys(entry, ENTRY_KEYS, where, errors):
        return
    for key in ("entry_id", "model_tag", "condition_id", "cell_id", "block_id", "sentinel_link_id"):
        if not isinstance(entry[key], str) or not ID_RE.fullmatch(entry[key]):
            errors.append(f"{where}.{key}: must match [a-z0-9_-]+")
    if entry["role"] not in ENTRY_ROLES:
        errors.append(f"{where}.role: invalid role")
    rep = entry["planned_rep_index"]
    if isinstance(rep, bool) or not isinstance(rep, int) or rep < 1:
        errors.append(f"{where}.planned_rep_index: must be a positive integer")
        return
    sentinel_position = None
    if entry["role"].startswith("drift_sentinel_"):
        sentinel_position = entry["role"].removeprefix("drift_sentinel_")
    workload = entry["condition_id"].removeprefix("cond-2m-")
    if sentinel_position is not None:
        workload = SENTINEL_WORKLOAD
    expected = _semantic_ids(entry["model_tag"], rep, workload, sentinel_position)
    for key, expected_value in expected.items():
        if entry[key] != expected_value:
            errors.append(f"{where}.{key}: expected {expected_value!r}")
    if not isinstance(entry["config"], str) or Path(entry["config"]).name != entry["config"]:
        errors.append(f"{where}.config: must be a basename")
    if not isinstance(entry["config_sha256"], str) or not SHA256_RE.fullmatch(entry["config_sha256"]):
        errors.append(f"{where}.config_sha256: must be 64 lowercase hex chars")


def _validate_config_link(
    entry: Mapping[str, Any],
    order_row: Mapping[str, Any] | None,
    manifest_dir: Path,
    where: str,
    errors: list[str],
) -> None:
    config_name = entry.get("config")
    if not isinstance(config_name, str) or Path(config_name).name != config_name:
        return
    path = manifest_dir / config_name
    try:
        raw = path.read_bytes()
        config = _parse_json_object(raw, str(path))
    except (OSError, AnalysisManifestError) as exc:
        errors.append(f"{where}.config: {exc}")
        return
    if sha256_bytes(raw) != entry.get("config_sha256"):
        errors.append(f"{where}.config_sha256: does not match config bytes")
    if config.get("run_id") != entry.get("run_id"):
        errors.append(f"{where}.run_id: disagrees with config")
    workload = config.get("workload_profile")
    workload_name = workload.get("name") if isinstance(workload, Mapping) else None
    expected_workload = (
        SENTINEL_WORKLOAD if str(entry.get("role", "")).startswith("drift_sentinel_")
        else str(entry.get("condition_id", "")).removeprefix("cond-2m-")
    )
    if workload_name != expected_workload:
        errors.append(f"{where}: workload name disagrees with entry")
    tags = config.get("run_metadata", {}).get("tags", [])
    rep = entry.get("planned_rep_index")
    required_tags = {"2m", expected_workload, f"rep{rep}"}
    if str(entry.get("role", "")).startswith("drift_sentinel_"):
        position = str(entry["role"]).removeprefix("drift_sentinel_")
        required_tags.update({"drift_sentinel", f"sentinel_{position}"})
    if not isinstance(tags, list) or not required_tags.issubset(set(tags)):
        errors.append(f"{where}: config tags do not identify entry")
    if order_row is not None:
        comparisons = {
            "config": entry.get("config"),
            "run_id": entry.get("run_id"),
            "model_tag": entry.get("model_tag"),
            "rep": entry.get("planned_rep_index"),
            "index": entry.get("order_index"),
            "position_in_block": entry.get("position_in_block"),
        }
        for key, expected in comparisons.items():
            if order_row.get(key) != expected:
                errors.append(f"{where}: disagrees with order manifest field {key}")


def validate_analysis_manifest(
    value: Mapping[str, Any],
    *,
    manifest_dir: Path | None = None,
    repository_root: Path = ROOT,
    registry_path: Path | None = None,
    ap_path: Path | None = None,
) -> list[str]:
    """Return all structural/linkage errors for one manifest value."""
    errors: list[str] = []
    if not _exact_keys(value, TOP_KEYS, "manifest", errors):
        return errors
    if value["schema_version"] != SCHEMA_VERSION:
        errors.append(f"manifest.schema_version: expected {SCHEMA_VERSION!r}")
    if value["freeze_status"] != "frozen":
        errors.append("manifest.freeze_status: must be 'frozen'")
    if not isinstance(value["manifest_id"], str) or not MANIFEST_ID_RE.fullmatch(value["manifest_id"]):
        errors.append("manifest.manifest_id: must be am- followed by 64 lowercase hex chars")
    elif value["manifest_id"] != calculate_manifest_id(value):
        errors.append("manifest.manifest_id: canonical identity mismatch")

    design = value["design"]
    planned_n = None
    if _exact_keys(design, DESIGN_KEYS, "manifest.design", errors):
        expected_design = {
            "design_id": "slice_2m_ap2_v1",
            "analysis_plan_ids": ["AP-2"],
            "unit_of_analysis": "paired_block",
            "difference_orientation": "condition_b_minus_condition_a",
        }
        for key, expected in expected_design.items():
            if design[key] != expected:
                errors.append(f"manifest.design.{key}: expected {expected!r}")
        sampling = design["sampling_plan"]
        if _exact_keys(sampling, SAMPLING_KEYS, "manifest.design.sampling_plan", errors):
            planned_n = sampling["planned_n_blocks"]
            if sampling["design"] != "fixed_n" or planned_n != 5:
                errors.append("manifest.design.sampling_plan: Slice-2M requires fixed_n=5")
            if sampling["freeze_basis"] != "generator_design_before_bundle_execution":
                errors.append("manifest.design.sampling_plan.freeze_basis: invalid value")
            if sampling["allowed_replacement_reasons"] != [
                "bundle_incomplete",
                "run_failed",
                "strict_invalid",
                "unsupported_before_measurement",
            ]:
                errors.append("manifest.design.sampling_plan.allowed_replacement_reasons: invalid value/order")
        randomization = design["randomization"]
        if _exact_keys(randomization, RANDOMIZATION_KEYS, "manifest.design.randomization", errors):
            if randomization != {
                "scheme": "deterministic_rotation",
                "exchangeability": "none",
                "seed": 2000005,
            }:
                errors.append("manifest.design.randomization: invalid Slice-2M rotation")

    registry_path = registry_path or repository_root / REGISTRY_RELATIVE_PATH
    ap_path = ap_path or repository_root / AP_RELATIVE_PATH
    registry: AnalysisRegistry | None = None
    ap_row: AnalysisPlanRow | None = None
    try:
        registry, ap_row = load_analysis_registry(registry_path, ap_path)
    except AnalysisManifestError as exc:
        errors.append(str(exc))
    source = value["source"]
    order: Mapping[str, Any] | None = None
    order_rows: list[Mapping[str, Any]] = []
    if _exact_keys(source, SOURCE_KEYS, "manifest.source", errors):
        if source["generator"] != "scripts/generate_matrix.py":
            errors.append("manifest.source.generator: invalid value")
        registry_source = source["registry_template"]
        if _exact_keys(registry_source, SOURCE_FILE_KEYS, "manifest.source.registry_template", errors):
            if registry_source["path"] != REGISTRY_RELATIVE_PATH.as_posix():
                errors.append("manifest.source.registry_template.path: invalid value")
            if registry is not None and registry_source["sha256"] != sha256_bytes(registry.raw_bytes):
                errors.append("manifest.source.registry_template.sha256: source hash mismatch")
        order_source = source["order_manifest"]
        if _exact_keys(order_source, SOURCE_FILE_KEYS, "manifest.source.order_manifest", errors):
            if order_source["path"] != ORDER_MANIFEST_NAME:
                errors.append("manifest.source.order_manifest.path: invalid value")
            if manifest_dir is not None:
                order_path = manifest_dir / ORDER_MANIFEST_NAME
                try:
                    order_raw = order_path.read_bytes()
                    order = _parse_json_object(order_raw, str(order_path))
                    if order_source["sha256"] != sha256_bytes(order_raw):
                        errors.append("manifest.source.order_manifest.sha256: source hash mismatch")
                    rows = order.get("executed_order")
                    if isinstance(rows, list) and all(isinstance(row, Mapping) for row in rows):
                        order_rows = list(rows)
                    else:
                        errors.append("order_manifest.executed_order: must be an array of objects")
                except (OSError, AnalysisManifestError) as exc:
                    errors.append(f"manifest.source.order_manifest: {exc}")
        ap_rows = source["ap_rows"]
        if not isinstance(ap_rows, list) or len(ap_rows) != 1:
            errors.append("manifest.source.ap_rows: must contain exactly AP-2")
        elif _exact_keys(ap_rows[0], AP_ROW_KEYS, "manifest.source.ap_rows[0]", errors):
            snapshot = ap_rows[0]
            if snapshot["plan_id"] != "AP-2" or snapshot["path"] != AP_RELATIVE_PATH.as_posix():
                errors.append("manifest.source.ap_rows[0]: invalid AP identity/path")
            if ap_row is not None:
                expected_snapshot = {
                    "section_sha256": sha256_bytes(ap_row.raw_section),
                    "family_id": ap_row.values["family_id"],
                    "claim_role": ap_row.values["claim_role"],
                    "selection_scope": ap_row.values["selection_scope"],
                    "multiplicity_rule": ap_row.values["multiplicity_rule"],
                }
                for key, expected in expected_snapshot.items():
                    if snapshot[key] != expected:
                        errors.append(f"manifest.source.ap_rows[0].{key}: AP snapshot mismatch")

    entries = value["entries"]
    if not isinstance(entries, list):
        errors.append("manifest.entries: must be an array")
        entries = []
    entry_ids: set[Any] = set()
    configs: set[Any] = set()
    run_ids: set[Any] = set()
    blocks: dict[Any, list[Mapping[str, Any]]] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            errors.append(f"entries[{index}]: must be an object")
            continue
        _validate_entry_semantics(entry, index, errors)
        for key, seen in (("entry_id", entry_ids), ("config", configs), ("run_id", run_ids)):
            candidate = entry.get(key)
            if candidate in seen:
                errors.append(f"entries[{index}].{key}: duplicate value {candidate!r}")
            seen.add(candidate)
        blocks.setdefault(entry.get("block_id"), []).append(entry)
        if manifest_dir is not None:
            order_row = order_rows[index] if index < len(order_rows) else None
            _validate_config_link(entry, order_row, manifest_dir, f"entries[{index}]", errors)
    if order_rows and len(entries) != len(order_rows):
        errors.append("manifest.entries: count differs from order_manifest.executed_order")
    if manifest_dir is not None:
        json_names = {path.name for path in manifest_dir.glob("*.json")}
        expected_names = set(configs) | {ORDER_MANIFEST_NAME, ANALYSIS_MANIFEST_NAME}
        unexpected = sorted(json_names - expected_names)
        missing = sorted(set(configs) - json_names)
        if unexpected:
            errors.append(f"manifest.entries: unexpected JSON sidecar/config(s): {', '.join(unexpected)}")
        if missing:
            errors.append(f"manifest.entries: missing config(s): {', '.join(missing)}")
    condition_cell_blocks: dict[Any, set[Any]] = {}
    expected_roles = {"condition"} | {f"drift_sentinel_{position}" for position in ("start", "end")}
    for block_id, block in blocks.items():
        roles = [entry.get("role") for entry in block]
        conditions = [entry.get("condition_id") for entry in block if entry.get("role") == "condition"]
        if len(block) != 6 or set(roles) != expected_roles or roles.count("condition") != 4:
            errors.append(f"{block_id}: must have four conditions and exactly two sentinels")
        if set(conditions) != {f"cond-2m-{name}" for name in PROFILE_NAMES}:
            errors.append(f"{block_id}: baseline condition set is incomplete")
        for entry in block:
            if entry.get("role") == "condition":
                condition_cell_blocks.setdefault(entry.get("cell_id"), set()).add(block_id)
    if planned_n is not None:
        for cell_id, block_ids in condition_cell_blocks.items():
            if len(block_ids) != planned_n:
                errors.append(f"{cell_id}: expected {planned_n} distinct block IDs")

    links = value["sentinel_links"]
    if not isinstance(links, list):
        errors.append("manifest.sentinel_links: must be an array")
        links = []
    seen_link_ids: set[Any] = set()
    linked_blocks: set[Any] = set()
    entries_by_id = {entry.get("entry_id"): entry for entry in entries if isinstance(entry, Mapping)}
    for index, link in enumerate(links):
        where = f"sentinel_links[{index}]"
        if not _exact_keys(link, SENTINEL_LINK_KEYS, where, errors):
            continue
        if link["sentinel_link_id"] in seen_link_ids:
            errors.append(f"{where}.sentinel_link_id: duplicate value")
        seen_link_ids.add(link["sentinel_link_id"])
        linked_blocks.add(link["block_id"])
        block = blocks.get(link["block_id"], [])
        by_role = {entry.get("role"): entry for entry in block}
        if link["start_entry_id"] != by_role.get("drift_sentinel_start", {}).get("entry_id"):
            errors.append(f"{where}.start_entry_id: does not link this block's start sentinel")
        if link["end_entry_id"] != by_role.get("drift_sentinel_end", {}).get("entry_id"):
            errors.append(f"{where}.end_entry_id: does not link this block's end sentinel")
        expected_linked = []
        by_condition = {entry.get("condition_id"): entry for entry in block}
        for name in PROFILE_NAMES:
            entry = by_condition.get(f"cond-2m-{name}")
            if entry is not None:
                expected_linked.append(entry.get("entry_id"))
        if link["linked_condition_entry_ids"] != expected_linked:
            errors.append(f"{where}.linked_condition_entry_ids: invalid workload-order linkage")
        if link["diagnostic"] != "end_minus_start":
            errors.append(f"{where}.diagnostic: invalid value")
        for entry_id in [link["start_entry_id"], link["end_entry_id"], *link["linked_condition_entry_ids"]]:
            if entry_id not in entries_by_id:
                errors.append(f"{where}: references unknown entry {entry_id!r}")
    if linked_blocks != set(blocks):
        errors.append("manifest.sentinel_links: must contain exactly one link per block")

    families = value["families"]
    if not isinstance(families, list):
        errors.append("manifest.families: must be an array")
        families = []
    contrasts = value["contrasts"]
    if not isinstance(contrasts, list):
        errors.append("manifest.contrasts: must be an array")
        contrasts = []
    contrast_ids: list[Any] = []
    contrast_by_id: dict[Any, Mapping[str, Any]] = {}
    for index, contrast in enumerate(contrasts):
        where = f"contrasts[{index}]"
        if not _exact_keys(contrast, CONTRAST_KEYS, where, errors):
            continue
        contrast_id = contrast["contrast_id"]
        contrast_ids.append(contrast_id)
        if contrast_id in contrast_by_id:
            errors.append(f"{where}.contrast_id: duplicate value {contrast_id!r}")
        contrast_by_id[contrast_id] = contrast
        if not isinstance(contrast_id, str) or not ID_RE.fullmatch(contrast_id):
            errors.append(f"{where}.contrast_id: invalid identifier")
        metric = contrast["metric"]
        _exact_keys(metric, METRIC_KEYS, f"{where}.metric", errors)
        selector = contrast["floor_selector"]
        if _exact_keys(selector, FLOOR_SELECTOR_KEYS, f"{where}.floor_selector", errors):
            if selector["backend"] != "from_bundle":
                errors.append(f"{where}.floor_selector.backend: invalid value")
            if isinstance(metric, Mapping):
                if selector["metric"] != metric.get("name") or selector["window_class"] != metric.get("window_class"):
                    errors.append(f"{where}.floor_selector: metric/window mismatch")
            if selector["condition_family_ids"] != [contrast["condition_a_id"], contrast["condition_b_id"]]:
                errors.append(f"{where}.floor_selector.condition_family_ids: condition mismatch")
            if selector["floor_field"] != "floor_gate_j":
                errors.append(f"{where}.floor_selector.floor_field: must use P2-039 floor_gate_j")
            if selector["transport_rule_id"] != "same_stack_componentwise_worst_case.v1":
                errors.append(f"{where}.floor_selector.transport_rule_id: invalid P2-039 rule")
        model_tag = str(contrast.get("cell_a_id", "")).removeprefix("cell-2m-").removesuffix(
            "-" + str(contrast.get("condition_a_id", "")).removeprefix("cond-2m-")
        )
        expected_blocks = [f"block-2m-{model_tag}-r{rep:02d}" for rep in range(1, 6)]
        if contrast["block_ids"] != expected_blocks:
            errors.append(f"{where}.block_ids: invalid semantic block linkage")
        if contrast["estimator"] != "paired_block_mean_difference_t_v1":
            errors.append(f"{where}.estimator: invalid value")
        if contrast["hypothesized_direction"] != "two_sided":
            errors.append(f"{where}.hypothesized_direction: invalid value")
        if contrast["equivalence"] is not None or contrast["mde"] is not None:
            errors.append(f"{where}: AP-2 v1 equivalence and mde must be null")
    family_ids: set[Any] = set()
    referenced_contrast_ids: list[Any] = []
    for index, family in enumerate(families):
        where = f"families[{index}]"
        if not _exact_keys(family, FAMILY_KEYS, where, errors):
            continue
        instance_id = family["family_instance_id"]
        if instance_id in family_ids:
            errors.append(f"{where}.family_instance_id: duplicate value")
        family_ids.add(instance_id)
        multiplicity = family["multiplicity"]
        if _exact_keys(multiplicity, MULTIPLICITY_KEYS, f"{where}.multiplicity", errors):
            ids = family["contrast_ids"]
            if not isinstance(ids, list):
                errors.append(f"{where}.contrast_ids: must be an array")
                ids = []
            if multiplicity["m"] != len(ids):
                errors.append(f"{where}.multiplicity.m: does not equal contrast_ids length")
            if multiplicity != {"method": "holm", "alpha": 0.05, "q": None, "m": 6}:
                errors.append(f"{where}.multiplicity: AP-2 family must be Holm m=6")
            referenced_contrast_ids.extend(ids)
            for contrast_id in ids:
                contrast = contrast_by_id.get(contrast_id)
                if contrast is None:
                    errors.append(f"{where}: references unknown contrast {contrast_id!r}")
                elif contrast.get("family_instance_id") != instance_id:
                    errors.append(f"{where}: contrast {contrast_id!r} links another family")
    if len(referenced_contrast_ids) != len(set(referenced_contrast_ids)):
        errors.append("manifest.families: a contrast_id appears in more than one family")
    if set(referenced_contrast_ids) != set(contrast_ids):
        errors.append("manifest.families: contrast enumeration is incomplete or has extras")
    if registry is not None and planned_n == 5:
        model_tags = sorted(
            {entry.get("model_tag") for entry in entries if isinstance(entry.get("model_tag"), str)}
        )
        expected_families, expected_contrasts = _build_families_and_contrasts(
            model_tags, registry.value, planned_n
        )
        if families != expected_families:
            errors.append("manifest.families: differs from frozen registry enumeration")
        if contrasts != expected_contrasts:
            errors.append("manifest.contrasts: differs from frozen registry enumeration")
    return errors


def write_manifest_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=f".{path.name}.", delete=False)
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
