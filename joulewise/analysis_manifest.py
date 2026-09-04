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
DETERMINISTIC_RANDOMIZATION_KEYS = {"scheme", "exchangeability", "seed"}
STRATIFIED_RANDOMIZATION_KEYS = {"scheme", "exchangeability", "named_strata"}
NAMED_STRATUM_KEYS = {"stratum_id", "block_ids"}
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
RATIO_ESTIMAND_KEYS = {
    "form",
    "numerator_metric",
    "denominator",
    "denominator_unit",
    "tokenizer_scope",
    "output_policy_scope",
}
RATIO_ESTIMAND_FORMS = {"mean_of_request_ratios", "ratio_of_totals"}
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
    "freeze_status",
    "plan_id",
    "family_id",
    "claim_role",
    "sampling_plan",
    "multiplicity",
    "metrics",
    "condition_pairs",
}
REGISTRY_MULTIPLICITY_KEYS = {"method", "alpha", "q"}
REGISTRY_PAIR_KEYS = {"condition_a", "condition_b"}
REGISTRY_SAMPLING_KEYS = {"design", "planned_n_blocks", "freeze_basis"}
AUTHORIZED_PLANNED_N_BLOCKS = {5, 10}
REGISTRY_FREEZE_BASIS = "window_a_variance_mde_before_campaign_execution"


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


def _resolve_repository_paths(
    *,
    repository_root: Path | None,
    registry_path: Path | None,
    ap_path: Path | None,
) -> tuple[Path, Path]:
    if registry_path is not None and ap_path is not None:
        return registry_path, ap_path

    root = repository_root
    if root is None:
        expected_markers = (REGISTRY_RELATIVE_PATH, AP_RELATIVE_PATH)
        missing_markers = [path for path in expected_markers if not (ROOT / path).is_file()]
        if missing_markers:
            expected = ", ".join(repr(path.as_posix()) for path in expected_markers)
            missing = ", ".join(repr(path.as_posix()) for path in missing_markers)
            raise AnalysisManifestError(
                "cannot infer the JouleWise repository root from package location "
                f"{ROOT}: expected repository marker files {expected}; missing {missing}. "
                "Pass an explicit repository root with repository_root=Path(...)."
            )
        root = ROOT

    return (
        registry_path if registry_path is not None else root / REGISTRY_RELATIVE_PATH,
        ap_path if ap_path is not None else root / AP_RELATIVE_PATH,
    )


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


def _string_field(
    value: Mapping[str, Any],
    key: str,
    where: str,
    errors: list[str],
    *,
    identifier: bool = False,
) -> str | None:
    candidate = value.get(key)
    if not isinstance(candidate, str):
        errors.append(f"{where}.{key}: must be a string")
        return None
    if identifier and not ID_RE.fullmatch(candidate):
        errors.append(f"{where}.{key}: must match [a-z0-9_-]+")
        return None
    return candidate


def _string_array(value: Any, where: str, errors: list[str]) -> list[str] | None:
    if not isinstance(value, list):
        errors.append(f"{where}: must be an array")
        return None
    bad_indexes = [str(index) for index, item in enumerate(value) if not isinstance(item, str)]
    if bad_indexes:
        errors.append(f"{where}: item(s) {', '.join(bad_indexes)} must be strings")
        return None
    return value


def _validate_ratio_estimand(value: Any, where: str, errors: list[str]) -> bool:
    if not _exact_keys(value, RATIO_ESTIMAND_KEYS, where, errors):
        return False
    valid = True
    if not isinstance(value["form"], str) or value["form"] not in RATIO_ESTIMAND_FORMS:
        errors.append(
            f"{where}.form: must be 'mean_of_request_ratios' or 'ratio_of_totals'"
        )
        valid = False
    expected = {
        "numerator_metric": "energy_request_j",
        "denominator": "runtime_observed_output_tokens",
        "denominator_unit": "token",
        "tokenizer_scope": "same_identity_required",
        "output_policy_scope": "same_policy_required",
    }
    for key, required in expected.items():
        if value[key] != required:
            errors.append(f"{where}.{key}: expected {required!r}")
            valid = False
    return valid


def _validate_randomization(
    value: Any,
    where: str,
    errors: list[str],
) -> set[str] | None:
    if not isinstance(value, Mapping):
        errors.append(f"{where}: must be an object")
        return None
    scheme = value.get("scheme")
    if scheme == "deterministic_rotation":
        if not _exact_keys(value, DETERMINISTIC_RANDOMIZATION_KEYS, where, errors):
            return None
        if value != {
            "scheme": "deterministic_rotation",
            "exchangeability": "none",
            "seed": 2000005,
        }:
            errors.append(f"{where}: invalid Slice-2M rotation")
        return None
    if scheme != "stratified_paired_label_swap":
        errors.append(f"{where}.scheme: unsupported randomization design")
        return None
    if not _exact_keys(value, STRATIFIED_RANDOMIZATION_KEYS, where, errors):
        return None
    if value["exchangeability"] != "within_named_strata":
        errors.append(
            f"{where}.exchangeability: stratified paired swaps require "
            "'within_named_strata'"
        )
    strata = value["named_strata"]
    if not isinstance(strata, list) or not strata:
        errors.append(f"{where}.named_strata: must be a nonempty array")
        return set()
    assigned: list[str] = []
    stratum_ids: set[str] = set()
    for index, stratum in enumerate(strata):
        stratum_where = f"{where}.named_strata[{index}]"
        if not _exact_keys(stratum, NAMED_STRATUM_KEYS, stratum_where, errors):
            continue
        stratum_id = _string_field(
            stratum,
            "stratum_id",
            stratum_where,
            errors,
            identifier=True,
        )
        block_ids = _string_array(
            stratum["block_ids"],
            f"{stratum_where}.block_ids",
            errors,
        )
        if stratum_id is not None:
            if stratum_id in stratum_ids:
                errors.append(f"{stratum_where}.stratum_id: duplicate value")
            stratum_ids.add(stratum_id)
        if block_ids is None:
            continue
        if not block_ids:
            errors.append(f"{stratum_where}.block_ids: must be nonempty")
            continue
        for block_index, block_id in enumerate(block_ids):
            if not ID_RE.fullmatch(block_id):
                errors.append(
                    f"{stratum_where}.block_ids[{block_index}]: "
                    "must match [a-z0-9_-]+"
                )
        if len(block_ids) != len(set(block_ids)):
            errors.append(f"{stratum_where}.block_ids: contains duplicate values")
        assigned.extend(block_ids)
    if len(assigned) != len(set(assigned)):
        errors.append(f"{where}.named_strata: a block appears in more than one stratum")
    return set(assigned)


def _is_adjudicated_ratio_variant(
    observed: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> bool:
    if set(observed) != METRIC_KEYS or set(expected) != METRIC_KEYS:
        return False
    ratio = observed.get("ratio_estimand")
    if not isinstance(ratio, Mapping) or set(ratio) != RATIO_ESTIMAND_KEYS:
        return False
    if not isinstance(ratio.get("form"), str) or ratio.get("form") not in RATIO_ESTIMAND_FORMS:
        return False
    if ratio != {
        "form": ratio["form"],
        "numerator_metric": "energy_request_j",
        "denominator": "runtime_observed_output_tokens",
        "denominator_unit": "token",
        "tokenizer_scope": "same_identity_required",
        "output_policy_scope": "same_policy_required",
    }:
        return False
    return (
        expected.get("name") == "energy_request_j"
        and observed.get("name") == expected.get("name")
        and observed.get("metric_tag") == expected.get("metric_tag")
        and observed.get("window_class") == expected.get("window_class")
        and observed.get("unit") == "J/token"
    )


def _contrast_matches_registry(
    observed: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> bool:
    if observed == expected:
        return True
    observed_without_metric = dict(observed)
    expected_without_metric = dict(expected)
    observed_metric = observed_without_metric.pop("metric", None)
    expected_metric = expected_without_metric.pop("metric", None)
    return (
        observed_without_metric == expected_without_metric
        and isinstance(observed_metric, Mapping)
        and isinstance(expected_metric, Mapping)
        and _is_adjudicated_ratio_variant(observed_metric, expected_metric)
    )


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
        raw = path.read_bytes()
    except OSError as exc:
        raise AnalysisManifestError(f"cannot read analysis plan {path}: {exc}") from exc
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AnalysisManifestError(f"analysis plan {path}: invalid UTF-8: {exc}") from exc
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
    if value["freeze_status"] != "frozen":
        errors.append("registry.freeze_status: expected 'frozen'")
    if value["plan_id"] != "AP-2":
        errors.append("registry.plan_id: expected 'AP-2'")
    if value["family_id"] != "FAM-2M-SHAPE-CONTRASTS":
        errors.append("registry.family_id: expected 'FAM-2M-SHAPE-CONTRASTS'")
    if value["claim_role"] != "primary":
        errors.append("registry.claim_role: expected 'primary'")
    sampling = value["sampling_plan"]
    if _exact_keys(sampling, REGISTRY_SAMPLING_KEYS, "registry.sampling_plan", errors):
        planned_n = sampling["planned_n_blocks"]
        if sampling["design"] != "fixed_n":
            errors.append("registry.sampling_plan.design: expected 'fixed_n'")
        if (
            isinstance(planned_n, bool)
            or not isinstance(planned_n, int)
            or planned_n not in AUTHORIZED_PLANNED_N_BLOCKS
        ):
            errors.append("registry.sampling_plan.planned_n_blocks: expected frozen n of 5 or 10")
        if sampling["freeze_basis"] != REGISTRY_FREEZE_BASIS:
            errors.append(
                "registry.sampling_plan.freeze_basis: expected Window-A variance/MDE freeze before campaign execution"
            )
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
    repository_root: Path | None = None,
    registry_path: Path | None = None,
    ap_path: Path | None = None,
) -> dict[str, Any]:
    registry_path, ap_path = _resolve_repository_paths(
        repository_root=repository_root,
        registry_path=registry_path,
        ap_path=ap_path,
    )
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
    planned_n_blocks = registry.value["sampling_plan"]["planned_n_blocks"]
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
                "freeze_basis": registry.value["sampling_plan"]["freeze_basis"],
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
    strings = {
        key: _string_field(
            entry,
            key,
            where,
            errors,
            identifier=key
            in {"entry_id", "model_tag", "condition_id", "cell_id", "block_id", "sentinel_link_id"},
        )
        for key in (
            "entry_id",
            "config",
            "config_sha256",
            "run_id",
            "model_tag",
            "role",
            "condition_id",
            "cell_id",
            "block_id",
            "sentinel_link_id",
        )
    }
    if any(candidate is None for candidate in strings.values()):
        return
    role = strings["role"]
    assert role is not None
    if role not in ENTRY_ROLES:
        errors.append(f"{where}.role: invalid role")
        return
    rep = entry["planned_rep_index"]
    if isinstance(rep, bool) or not isinstance(rep, int) or rep < 1:
        errors.append(f"{where}.planned_rep_index: must be a positive integer")
        return
    for key in ("order_index", "position_in_block"):
        candidate = entry[key]
        if isinstance(candidate, bool) or not isinstance(candidate, int) or candidate < 1:
            errors.append(f"{where}.{key}: must be a positive integer")
    sentinel_position = None
    if role.startswith("drift_sentinel_"):
        sentinel_position = role.removeprefix("drift_sentinel_")
    condition_id = strings["condition_id"]
    model_tag = strings["model_tag"]
    assert condition_id is not None and model_tag is not None
    workload = condition_id.removeprefix("cond-2m-")
    if sentinel_position is not None:
        workload = SENTINEL_WORKLOAD
    expected = _semantic_ids(model_tag, rep, workload, sentinel_position)
    for key, expected_value in expected.items():
        if entry[key] != expected_value:
            errors.append(f"{where}.{key}: expected {expected_value!r}")
    expected_run_id = f"{model_tag}-r{rep}-{workload}"
    if sentinel_position is not None:
        expected_run_id += f"-{sentinel_position}"
    if entry["run_id"] != expected_run_id:
        errors.append(f"{where}.run_id: expected semantic run_id {expected_run_id!r}")
    if Path(entry["config"]).name != entry["config"]:
        errors.append(f"{where}.config: must be a basename")
    if not SHA256_RE.fullmatch(entry["config_sha256"]):
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
    run_metadata = config.get("run_metadata")
    tags = run_metadata.get("tags", []) if isinstance(run_metadata, Mapping) else []
    rep = entry.get("planned_rep_index")
    required_tags = {"2m", expected_workload, f"rep{rep}"}
    if str(entry.get("role", "")).startswith("drift_sentinel_"):
        position = str(entry["role"]).removeprefix("drift_sentinel_")
        required_tags.update({"drift_sentinel", f"sentinel_{position}"})
    if (
        not isinstance(tags, list)
        or not all(isinstance(tag, str) for tag in tags)
        or not required_tags.issubset(set(tags))
    ):
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
    repository_root: Path | None = None,
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
    else:
        try:
            expected_manifest_id = calculate_manifest_id(value)
        except (TypeError, ValueError) as exc:
            errors.append(f"manifest: fields must use JSON-compatible types: {exc}")
        else:
            if value["manifest_id"] != expected_manifest_id:
                errors.append("manifest.manifest_id: canonical identity mismatch")

    design = value["design"]
    planned_n = None
    named_strata_block_ids: set[str] | None = None
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
            if sampling["design"] != "fixed_n":
                errors.append("manifest.design.sampling_plan.design: must be 'fixed_n'")
            if (
                isinstance(planned_n, bool)
                or not isinstance(planned_n, int)
                or planned_n not in AUTHORIZED_PLANNED_N_BLOCKS
            ):
                errors.append("manifest.design.sampling_plan.planned_n_blocks: expected frozen n of 5 or 10")
            if sampling["freeze_basis"] != REGISTRY_FREEZE_BASIS:
                errors.append("manifest.design.sampling_plan.freeze_basis: invalid value")
            if sampling["allowed_replacement_reasons"] != [
                "bundle_incomplete",
                "run_failed",
                "strict_invalid",
                "unsupported_before_measurement",
            ]:
                errors.append("manifest.design.sampling_plan.allowed_replacement_reasons: invalid value/order")
        named_strata_block_ids = _validate_randomization(
            design["randomization"],
            "manifest.design.randomization",
            errors,
        )

    registry: AnalysisRegistry | None = None
    ap_row: AnalysisPlanRow | None = None
    try:
        registry_path, ap_path = _resolve_repository_paths(
            repository_root=repository_root,
            registry_path=registry_path,
            ap_path=ap_path,
        )
        registry, ap_row = load_analysis_registry(registry_path, ap_path)
    except AnalysisManifestError as exc:
        errors.append(str(exc))
    if registry is not None and planned_n != registry.value["sampling_plan"]["planned_n_blocks"]:
        errors.append(
            "manifest.design.sampling_plan.planned_n_blocks: post-freeze n mutation differs from frozen registry"
        )
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
                    if order.get("planned_n_blocks") != planned_n:
                        errors.append(
                            "order_manifest.planned_n_blocks: inconsistent frozen block authority"
                        )
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
            if not isinstance(candidate, str):
                continue
            if candidate in seen:
                errors.append(f"entries[{index}].{key}: duplicate value {candidate!r}")
            seen.add(candidate)
        block_id = entry.get("block_id")
        if isinstance(block_id, str):
            blocks.setdefault(block_id, []).append(entry)
        if manifest_dir is not None:
            order_row = order_rows[index] if index < len(order_rows) else None
            _validate_config_link(entry, order_row, manifest_dir, f"entries[{index}]", errors)
    if order_rows and len(entries) != len(order_rows):
        errors.append("manifest.entries: count differs from order_manifest.executed_order")
    if (
        isinstance(planned_n, int)
        and not isinstance(planned_n, bool)
        and planned_n in AUTHORIZED_PLANNED_N_BLOCKS
    ):
        expected_rep_indexes = set(range(1, planned_n + 1))
        rep_indexes_by_model: dict[str, set[int]] = {}
        for entry in entries:
            if not isinstance(entry, Mapping):
                continue
            model_tag = entry.get("model_tag")
            rep_index = entry.get("planned_rep_index")
            if (
                isinstance(model_tag, str)
                and isinstance(rep_index, int)
                and not isinstance(rep_index, bool)
            ):
                rep_indexes_by_model.setdefault(model_tag, set()).add(rep_index)
        if any(rep_indexes != expected_rep_indexes for rep_indexes in rep_indexes_by_model.values()):
            errors.append(
                "manifest.entries: mixed n=5/n=10 or inconsistent frozen block authority"
            )
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
        roles = [entry.get("role") for entry in block if isinstance(entry.get("role"), str)]
        conditions = [
            entry.get("condition_id")
            for entry in block
            if entry.get("role") == "condition" and isinstance(entry.get("condition_id"), str)
        ]
        if len(block) != 6 or set(roles) != expected_roles or roles.count("condition") != 4:
            errors.append(f"{block_id}: must have four conditions and exactly two sentinels")
        if set(conditions) != {f"cond-2m-{name}" for name in PROFILE_NAMES}:
            errors.append(f"{block_id}: baseline condition set is incomplete")
        for entry in block:
            if entry.get("role") == "condition":
                cell_id = entry.get("cell_id")
                if isinstance(cell_id, str):
                    condition_cell_blocks.setdefault(cell_id, set()).add(block_id)
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
    entries_by_id = {
        entry_id: entry
        for entry in entries
        if isinstance(entry, Mapping)
        and isinstance((entry_id := entry.get("entry_id")), str)
    }
    for index, link in enumerate(links):
        where = f"sentinel_links[{index}]"
        if not _exact_keys(link, SENTINEL_LINK_KEYS, where, errors):
            continue
        link_strings = {
            key: _string_field(
                link,
                key,
                where,
                errors,
                identifier=key != "diagnostic",
            )
            for key in (
                "sentinel_link_id",
                "block_id",
                "start_entry_id",
                "end_entry_id",
                "diagnostic",
            )
        }
        linked_entry_ids = _string_array(
            link["linked_condition_entry_ids"],
            f"{where}.linked_condition_entry_ids",
            errors,
        )
        if any(candidate is None for candidate in link_strings.values()) or linked_entry_ids is None:
            continue
        link_id = link_strings["sentinel_link_id"]
        block_id = link_strings["block_id"]
        assert link_id is not None and block_id is not None
        if link_id in seen_link_ids:
            errors.append(f"{where}.sentinel_link_id: duplicate value")
        seen_link_ids.add(link_id)
        linked_blocks.add(block_id)
        block = blocks.get(block_id, [])
        by_role = {
            role: entry
            for entry in block
            if isinstance((role := entry.get("role")), str)
        }
        if link["start_entry_id"] != by_role.get("drift_sentinel_start", {}).get("entry_id"):
            errors.append(f"{where}.start_entry_id: does not link this block's start sentinel")
        if link["end_entry_id"] != by_role.get("drift_sentinel_end", {}).get("entry_id"):
            errors.append(f"{where}.end_entry_id: does not link this block's end sentinel")
        expected_linked = []
        by_condition = {
            condition_id: entry
            for entry in block
            if isinstance((condition_id := entry.get("condition_id")), str)
        }
        for name in PROFILE_NAMES:
            entry = by_condition.get(f"cond-2m-{name}")
            if entry is not None:
                expected_linked.append(entry.get("entry_id"))
        if link["linked_condition_entry_ids"] != expected_linked:
            errors.append(f"{where}.linked_condition_entry_ids: invalid workload-order linkage")
        if link["diagnostic"] != "end_minus_start":
            errors.append(f"{where}.diagnostic: invalid value")
        for entry_id in [link["start_entry_id"], link["end_entry_id"], *linked_entry_ids]:
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
        contrast_strings = {
            key: _string_field(
                contrast,
                key,
                where,
                errors,
                identifier=key
                in {
                    "contrast_id",
                    "family_instance_id",
                    "condition_a_id",
                    "condition_b_id",
                    "cell_a_id",
                    "cell_b_id",
                },
            )
            for key in (
                "contrast_id",
                "plan_id",
                "family_instance_id",
                "claim_role",
                "estimator",
                "condition_a_id",
                "condition_b_id",
                "cell_a_id",
                "cell_b_id",
                "hypothesized_direction",
            )
        }
        block_ids = _string_array(contrast["block_ids"], f"{where}.block_ids", errors)
        if any(candidate is None for candidate in contrast_strings.values()) or block_ids is None:
            continue
        contrast_id = contrast_strings["contrast_id"]
        assert contrast_id is not None
        contrast_ids.append(contrast_id)
        if contrast_id in contrast_by_id:
            errors.append(f"{where}.contrast_id: duplicate value {contrast_id!r}")
        contrast_by_id[contrast_id] = contrast
        metric = contrast["metric"]
        metric_valid = _exact_keys(metric, METRIC_KEYS, f"{where}.metric", errors)
        if metric_valid:
            for key in ("name", "metric_tag", "window_class", "unit"):
                if _string_field(metric, key, f"{where}.metric", errors) is None:
                    metric_valid = False
            ratio_estimand = metric["ratio_estimand"]
            if ratio_estimand is not None:
                if not _validate_ratio_estimand(
                    ratio_estimand,
                    f"{where}.metric.ratio_estimand",
                    errors,
                ):
                    metric_valid = False
                if metric["unit"] != "J/token":
                    errors.append(f"{where}.metric.unit: ratio estimands require 'J/token'")
                    metric_valid = False
        selector = contrast["floor_selector"]
        if _exact_keys(selector, FLOOR_SELECTOR_KEYS, f"{where}.floor_selector", errors):
            selector_valid = all(
                _string_field(selector, key, f"{where}.floor_selector", errors) is not None
                for key in ("backend", "metric", "window_class", "floor_field", "transport_rule_id")
            )
            condition_family_ids = _string_array(
                selector["condition_family_ids"],
                f"{where}.floor_selector.condition_family_ids",
                errors,
            )
            if not selector_valid or condition_family_ids is None:
                continue
            if selector["backend"] != "from_bundle":
                errors.append(f"{where}.floor_selector.backend: invalid value")
            if metric_valid:
                if selector["metric"] != metric.get("name") or selector["window_class"] != metric.get("window_class"):
                    errors.append(f"{where}.floor_selector: metric/window mismatch")
            if selector["condition_family_ids"] != [contrast["condition_a_id"], contrast["condition_b_id"]]:
                errors.append(f"{where}.floor_selector.condition_family_ids: condition mismatch")
            if selector["floor_field"] != "floor_gate_j":
                errors.append(f"{where}.floor_selector.floor_field: must use P2-039 floor_gate_j")
            if selector["transport_rule_id"] != "same_stack_componentwise_worst_case.v1":
                errors.append(f"{where}.floor_selector.transport_rule_id: invalid P2-039 rule")
        model_tag = contrast["cell_a_id"].removeprefix("cell-2m-").removesuffix(
            "-" + contrast["condition_a_id"].removeprefix("cond-2m-")
        )
        expected_blocks = (
            [f"block-2m-{model_tag}-r{rep:02d}" for rep in range(1, planned_n + 1)]
            if isinstance(planned_n, int) and not isinstance(planned_n, bool)
            else []
        )
        if contrast["block_ids"] != expected_blocks:
            errors.append(f"{where}.block_ids: invalid semantic block linkage")
        if named_strata_block_ids is not None and set(block_ids) != named_strata_block_ids:
            errors.append(
                f"{where}.block_ids: named strata must cover every frozen block exactly once"
            )
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
        family_strings = {
            key: _string_field(
                family,
                key,
                where,
                errors,
                identifier=key == "family_instance_id",
            )
            for key in ("family_id", "family_instance_id", "plan_id", "claim_role", "metric_tag")
        }
        ids = _string_array(family["contrast_ids"], f"{where}.contrast_ids", errors)
        if any(candidate is None for candidate in family_strings.values()) or ids is None:
            continue
        instance_id = family_strings["family_instance_id"]
        assert instance_id is not None
        if instance_id in family_ids:
            errors.append(f"{where}.family_instance_id: duplicate value")
        family_ids.add(instance_id)
        multiplicity = family["multiplicity"]
        if _exact_keys(multiplicity, MULTIPLICITY_KEYS, f"{where}.multiplicity", errors):
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
            family_metrics = [
                contrast_by_id[contrast_id].get("metric")
                for contrast_id in ids
                if contrast_id in contrast_by_id
            ]
            if family_metrics and any(metric != family_metrics[0] for metric in family_metrics[1:]):
                errors.append(f"{where}: contrasts must use one estimand-local metric")
    if len(referenced_contrast_ids) != len(set(referenced_contrast_ids)):
        errors.append("manifest.families: a contrast_id appears in more than one family")
    if set(referenced_contrast_ids) != set(contrast_ids):
        errors.append("manifest.families: contrast enumeration is incomplete or has extras")
    if (
        registry is not None
        and isinstance(planned_n, int)
        and not isinstance(planned_n, bool)
        and planned_n in AUTHORIZED_PLANNED_N_BLOCKS
    ):
        model_tags = sorted(
            {entry.get("model_tag") for entry in entries if isinstance(entry.get("model_tag"), str)}
        )
        expected_families, expected_contrasts = _build_families_and_contrasts(
            model_tags, registry.value, planned_n
        )
        if families != expected_families:
            errors.append("manifest.families: differs from frozen registry enumeration")
        if len(contrasts) != len(expected_contrasts) or any(
            not isinstance(observed, Mapping)
            or not _contrast_matches_registry(observed, expected)
            for observed, expected in zip(contrasts, expected_contrasts)
        ):
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
