"""P2-037 contrast and claim engine public entry point."""

from __future__ import annotations

import copy
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from joulewise.detection_floor import (
    ATTRIBUTION_FLOOR_SOURCE,
    ATTRIBUTION_LIMIT_CLASS,
    attribution_single_count_discipline,
)

from .artifact import finalize_claim_verdicts, write_claim_verdicts_atomic
from .claims import evaluate_claim, ordered_reason_codes
from .estimators import (
    DeterministicBoundTerm,
    Interval,
    PairedEstimate,
    PairedObservation,
    StochasticVarianceTerm,
    tost_p_value,
)
from .inputs import (
    AnalysisInputError,
    BundleEvidence,
    declared_evidence_roots,
    FloorEvidenceBinding,
    FloorRequest,
    FloorResolution,
    LoadedAnalysisInputs,
    deterministic_bounds,
    floor_binding_reason_codes,
    floor_request_for_evidence,
    governed_stochastic_variance,
    load_analysis_inputs,
    metric_value,
    resolve_floor,
    token_provenance,
    unavailable_floor_resolution,
    window_evidence_precheck,
)
from .multiplicity import adjust_p_values
from .ratio import (
    convert_floor_to_ratio_units,
    estimate_manifest_observations,
    estimation_metric,
    ratio_collection_evidence_reasons,
    ratio_evidence_reasons,
    ratio_observation_from_evidence,
    validate_ratio_estimand,
)
from .sensitivity import (
    influence_triggers,
    randomization_check,
    randomization_design_for_blocks,
    summarize_loo,
)


_FloorRequestFactory = Callable[
    [Mapping[str, Any], str, Sequence[BundleEvidence], Mapping[str, Any]],
    FloorRequest | None,
]
_PairStochasticFactory = Callable[
    [BundleEvidence, BundleEvidence, Mapping[str, Any]],
    tuple[tuple[StochasticVarianceTerm, ...], tuple[str, ...]],
]

_FLOOR_POLICY_ID = "declared_exact_bundle_config_floor_v1"
_STOCHASTIC_POLICY_ID = "p2044_reducer_0_4_1_idle_variance_v1"
_COOLDOWN_POLICY_ID = "campaign_provenance_v1_hash_bound_per_member_v1"


def _private_factory_identity(factory: Callable[..., Any] | None, default: str) -> str:
    if factory is None:
        return default
    module = getattr(factory, "__module__", factory.__class__.__module__)
    qualname = getattr(factory, "__qualname__", factory.__class__.__qualname__)
    return f"private_test_seam:{module}.{qualname}"


def _validate_output_separation(
    output_path: Path,
    analysis_manifest_path: Path,
    runs_root: Path,
    floor_artifact_path: Path,
    evidence_roots: Mapping[str, Path] | None = None,
) -> None:
    """Keep the pure derivation output outside every immutable input lane."""

    floor_evidence_paths = tuple(
        Path(root) for root in (evidence_roots or {}).values()
    )
    try:
        if any(
            Path(value).is_symlink()
            for value in (
                output_path,
                analysis_manifest_path,
                runs_root,
                floor_artifact_path,
                *floor_evidence_paths,
            )
        ):
            raise AnalysisInputError(
                "claim-verdict path_resolution_refused: symlink input"
            )
        output = Path(output_path).resolve()
        manifest = Path(analysis_manifest_path).resolve()
        floor = Path(floor_artifact_path).resolve()
        runs = Path(runs_root).resolve()
        floor_evidence = tuple(path.resolve() for path in floor_evidence_paths)
    except AnalysisInputError:
        raise
    except (OSError, RuntimeError) as exc:
        raise AnalysisInputError(
            f"claim-verdict path_resolution_refused: {type(exc).__name__}"
        ) from exc
    if output in {manifest, floor}:
        raise AnalysisInputError("claim-verdict output aliases an immutable input")
    try:
        output.relative_to(runs)
    except ValueError:
        pass
    else:
        raise AnalysisInputError("claim-verdict output must be outside the runs root")
    for evidence_root in floor_evidence:
        try:
            output.relative_to(evidence_root)
        except ValueError:
            continue
        raise AnalysisInputError(
            "claim-verdict output must be outside floor evidence roots"
        )
    try:
        output.relative_to(manifest.parent)
    except ValueError:
        pass
    else:
        raise AnalysisInputError(
            "claim-verdict output must be outside the frozen manifest directory"
        )


def _interval_dict(value: Interval | None) -> dict[str, float] | None:
    if value is None:
        return None
    return {"lower": value.lower, "upper": value.upper}


def _empty_estimator(name: str, n: int) -> dict[str, Any]:
    return {
        "name": name,
        "n": n,
        "df": None,
        "estimate": None,
        "s_d": None,
        "SE_repeat": None,
        "SE_metrology": None,
        "SE_total": None,
        "t_critical_95": None,
        "repeat_point_CI95": None,
        "metrology_aware_CI95": None,
        "variance_contributions": [],
        "excluded_stochastic_terms": [],
        "raw_p": None,
    }


def _estimator_dict(result: PairedEstimate | None, name: str, n: int) -> dict[str, Any]:
    if result is None:
        return _empty_estimator(name, n)
    return {
        "name": result.estimator,
        "n": result.n,
        "df": result.df,
        "estimate": result.estimate,
        "s_d": result.sample_stddev,
        "SE_repeat": result.se_repeat,
        "SE_metrology": result.se_metrology,
        "SE_total": result.se_total,
        "t_critical_95": result.t_critical_95,
        "repeat_point_CI95": _interval_dict(result.repeat_point_ci95),
        "metrology_aware_CI95": _interval_dict(result.metrology_aware_ci95),
        "variance_contributions": [asdict(value) for value in result.variance_contributions],
        "excluded_stochastic_terms": list(result.excluded_stochastic_terms),
        "raw_p": result.raw_p,
    }


def _floor_engine_reasons(resolutions: Sequence[FloorResolution]) -> list[str]:
    reasons: list[str] = []
    for resolution in resolutions:
        if resolution.floor_abs_j is None:
            reasons.append("floor_abs_missing")
        if resolution.floor_cmp_j is None:
            reasons.append("floor_cmp_missing")
        for reason in resolution.reason_codes:
            if reason == "cell_missing":
                reasons.append("floor_row_missing")
            elif reason == "cell_stale":
                reasons.append("floor_row_stale")
            elif reason == "transport_group_incomplete":
                reasons.append("floor_row_ambiguous")
            else:
                reasons.append("floor_transport_inapplicable")
    return ordered_reason_codes(reasons)


def _combined_floor(resolutions: Sequence[FloorResolution]) -> dict[str, Any]:
    if any(
        resolution.status == "exact" and len(resolution.source_cell_ids) != 1
        for resolution in resolutions
    ):
        raise AnalysisInputError(
            "exact floor resolution must name exactly one source cell"
        )
    usable = [resolution for resolution in resolutions if resolution.status in {"exact", "transported"}]
    all_usable = bool(resolutions) and len(usable) == len(resolutions)
    floor_abs = max((value.floor_abs_j for value in usable if value.floor_abs_j is not None), default=None)
    floor_cmp = max((value.floor_cmp_j for value in usable if value.floor_cmp_j is not None), default=None)
    floor_gate = max((value.floor_gate_j for value in usable if value.floor_gate_j is not None), default=None)
    if not all_usable:
        floor_abs = floor_cmp = floor_gate = None
    resolution_rows = []
    for value in resolutions:
        row = {
            "status": value.status,
            "source_cell_ids": list(value.source_cell_ids),
            "transport_group_id": value.transport_group_id,
            "transport_rule_id": value.transport_rule_id,
            "floor_abs_j": value.floor_abs_j,
            "floor_cmp_j": value.floor_cmp_j,
            "floor_gate_j": value.floor_gate_j,
            "reason_codes": list(value.reason_codes),
        }
        if (
            value.floor_limit_class == ATTRIBUTION_LIMIT_CLASS
            and value.floor_source == ATTRIBUTION_FLOOR_SOURCE
            and isinstance(value.point_floor_diagnostics, Mapping)
            and value.single_count_discipline
            == attribution_single_count_discipline()
        ):
            row.update(
                {
                    "floor_source": ATTRIBUTION_FLOOR_SOURCE,
                    "floor_limit_class": ATTRIBUTION_LIMIT_CLASS,
                    "point_floor_diagnostics": copy.deepcopy(
                        dict(value.point_floor_diagnostics)
                    ),
                    "single_count_discipline": (
                        attribution_single_count_discipline()
                    ),
                }
            )
        resolution_rows.append(row)
    result = {
        "status": "resolved" if all_usable else "refused",
        "floor_row_ids": sorted({cell for value in resolutions for cell in value.source_cell_ids}),
        "floor_abs_j": floor_abs,
        "floor_cmp_j": floor_cmp,
        "active_floor_j": floor_gate,
        "transport_verdict": (
            "exact"
            if all_usable and all(value.status == "exact" for value in usable)
            else "transported"
            if all_usable
            else "refused"
        ),
        "resolutions": resolution_rows,
    }
    limited = [
        value
        for value in usable
        if value.floor_limit_class == ATTRIBUTION_LIMIT_CLASS
        and value.floor_source == ATTRIBUTION_FLOOR_SOURCE
        and isinstance(value.point_floor_diagnostics, Mapping)
        and value.single_count_discipline
        == attribution_single_count_discipline()
    ]
    if all_usable and limited:
        diagnostics: dict[str, Any] = {}
        for value in limited:
            source_diagnostics = dict(value.point_floor_diagnostics or {})
            if value.status == "transported":
                diagnostics.update(copy.deepcopy(source_diagnostics))
            else:
                for source_cell_id in value.source_cell_ids:
                    diagnostics[source_cell_id] = copy.deepcopy(
                        source_diagnostics
                    )
        result.update(
            {
                "floor_source": ATTRIBUTION_FLOOR_SOURCE,
                "floor_limit_class": ATTRIBUTION_LIMIT_CLASS,
                "point_floor_diagnostics": diagnostics,
                "single_count_discipline": (
                    attribution_single_count_discipline()
                ),
            }
        )
    return result


def _entries_for_contrast(
    manifest: Mapping[str, Any], contrast: Mapping[str, Any]
) -> dict[tuple[str, str], Mapping[str, Any]]:
    wanted_cells = {contrast["cell_a_id"], contrast["cell_b_id"]}
    return {
        (entry["block_id"], entry["cell_id"]): entry
        for entry in manifest["entries"]
        if entry["role"] == "condition" and entry["cell_id"] in wanted_cells
    }


def _sentinel_entries_by_block(manifest: Mapping[str, Any]) -> dict[str, tuple[str, str]]:
    return {
        link["block_id"]: (link["start_entry_id"], link["end_entry_id"])
        for link in manifest["sentinel_links"]
    }


def _randomization_alpha(
    manifest: Mapping[str, Any], contrast: Mapping[str, Any]
) -> float:
    for family in manifest["families"]:
        if family["family_instance_id"] != contrast["family_instance_id"]:
            continue
        multiplicity = family["multiplicity"]
        for key in ("alpha", "q"):
            value = multiplicity.get(key)
            if (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(value)
                and 0.0 < float(value) < 1.0
            ):
                return float(value)
        break
    design = manifest["design"]["randomization"]
    if design.get("scheme") == "paired_label_swap_within_block":
        raise AnalysisInputError(
            "exchangeable randomization sensitivity requires a frozen family threshold"
        )
    # The threshold is unused for non-applicable deterministic designs.
    return 0.05


def _resolve_contrast_floor(
    inputs: LoadedAnalysisInputs,
    contrast: Mapping[str, Any],
    included: Mapping[str, Sequence[BundleEvidence]],
    request_factory: _FloorRequestFactory | None,
) -> list[FloorResolution]:
    resolutions: list[FloorResolution] = []
    for condition_id in contrast["floor_selector"]["condition_family_ids"]:
        evidence = included.get(condition_id, ())
        request = (
            request_factory(contrast, condition_id, evidence, inputs.floor_artifact)
            if request_factory is not None
            else floor_request_for_evidence(
                inputs.floor_artifact,
                inputs.floor_binding,
                contrast,
                condition_id,
                evidence,
            )
        )
        if request is None or (
            request.metric != contrast["floor_selector"]["metric"]
            or request.window_class != contrast["floor_selector"]["window_class"]
            or request.condition_family_id != condition_id
        ):
            if request_factory is None and (
                inputs.floor_binding.global_problems
                or any(inputs.floor_binding.problems_by_cell.values())
            ):
                binding_reasons = floor_binding_reason_codes(inputs.floor_binding)
                resolutions.append(
                    FloorResolution(
                        status="refused",
                        artifact_id=str(inputs.floor_artifact.get("artifact_id", "")),
                        artifact_sha256=inputs.floor_sha256,
                        source_cell_ids=(),
                        transport_group_id=None,
                        transport_rule_id=None,
                        floor_abs_j=None,
                        floor_cmp_j=None,
                        floor_gate_j=None,
                        reason_codes=("artifact_schema_invalid", *binding_reasons),
                    )
                )
            else:
                resolutions.append(
                    unavailable_floor_resolution(inputs.floor_artifact, inputs.floor_sha256)
                )
        else:
            binding = inputs.floor_binding
            if request_factory is not None:
                # The underscored injection remains a test-only pure-resolver
                # seam. Production CLI calls never supply it; they always use
                # the byte/metric/order binding loaded above.
                cell_ids = frozenset(
                    str(cell["cell_id"])
                    for cell in inputs.floor_artifact.get("cells", [])
                    if isinstance(cell, Mapping) and isinstance(cell.get("cell_id"), str)
                )
                binding = FloorEvidenceBinding(
                    bound_cell_ids=cell_ids,
                    cell_scientific_identity_sha256={},
                    cell_stack_identity_sha256={},
                    bound_bundle_sha256s=frozenset(),
                    problems_by_cell={},
                    global_problems=(),
                )
            resolutions.append(
                resolve_floor(
                    inputs.floor_artifact,
                    inputs.floor_sha256,
                    request,
                    evidence_binding=binding,
                )
            )
    return resolutions


def _prepare_contrast(
    inputs: LoadedAnalysisInputs,
    contrast: Mapping[str, Any],
    sentinel_entries: Mapping[str, tuple[str, str]],
    request_factory: _FloorRequestFactory | None,
    pair_stochastic_factory: _PairStochasticFactory | None,
    *,
    evidence_class: str,
) -> dict[str, Any]:
    entries = _entries_for_contrast(inputs.manifest, contrast)
    evidence_metric = estimation_metric(contrast["metric"])
    ratio_estimand = contrast["metric"].get("ratio_estimand")
    block_rows: list[dict[str, Any]] = []
    observation_parts: list[dict[str, Any]] = []
    global_reasons: list[str] = []
    included_by_condition: dict[str, list[BundleEvidence]] = {
        contrast["condition_a_id"]: [],
        contrast["condition_b_id"]: [],
    }

    for block_id in contrast["block_ids"]:
        entry_a = entries.get((block_id, contrast["cell_a_id"]))
        entry_b = entries.get((block_id, contrast["cell_b_id"]))
        reasons: list[str] = []
        if entry_a is None or entry_b is None:
            reasons.append("paired_block_incomplete")
            block_rows.append(
                {
                    "block_id": block_id,
                    "bundle_a_id": None,
                    "bundle_b_id": None,
                    "included": False,
                    "reason_codes": ordered_reason_codes(reasons),
                }
            )
            continue
        evidence_a = inputs.effective[entry_a["entry_id"]]
        evidence_b = inputs.effective[entry_b["entry_id"]]
        reasons.extend(evidence_a.base_reason_codes)
        reasons.extend(evidence_b.base_reason_codes)
        for sentinel_entry_id in sentinel_entries.get(block_id, ()):
            sentinel = inputs.effective.get(sentinel_entry_id)
            if sentinel is None:
                reasons.append("bundle_missing")
            elif not sentinel.included:
                reasons.extend(sentinel.base_reason_codes)

        value_a = metric_value(evidence_a.summary or {}, evidence_metric)
        value_b = metric_value(evidence_b.summary or {}, evidence_metric)
        if value_a is None or value_b is None:
            reasons.append("metric_missing_or_nonfinite")

        precheck_a = window_evidence_precheck(evidence_a, evidence_metric)
        precheck_b = window_evidence_precheck(evidence_b, evidence_metric)
        reasons.extend(precheck_a["reasons"])
        reasons.extend(precheck_b["reasons"])

        if pair_stochastic_factory is None:
            governed_a, stochastic_reasons_a = governed_stochastic_variance(
                evidence_a, evidence_metric
            )
            governed_b, stochastic_reasons_b = governed_stochastic_variance(
                evidence_b, evidence_metric
            )
            stochastic_reasons = (*stochastic_reasons_a, *stochastic_reasons_b)
            by_name_a = {str(term["name"]): term for term in governed_a}
            by_name_b = {str(term["name"]): term for term in governed_b}
            if not stochastic_reasons and set(by_name_a) != set(by_name_b):
                stochastic_reasons = ("required_error_term_unknown",)
            stochastic_terms = (
                tuple(
                    StochasticVarianceTerm(
                        name=name,
                        variance_a=float(by_name_a[name]["variance"]),
                        variance_b=float(by_name_b[name]["variance"]),
                        covariance_ab=None,
                        correlation_scope="independent_run",
                    )
                    for name in sorted(by_name_a)
                )
                if not stochastic_reasons
                else ()
            )
        else:
            stochastic_terms, stochastic_reasons = pair_stochastic_factory(
                evidence_a, evidence_b, evidence_metric
            )
            if not isinstance(stochastic_terms, tuple) or any(
                not isinstance(term, StochasticVarianceTerm) for term in stochastic_terms
            ):
                raise AnalysisInputError(
                    "pair stochastic factory must return StochasticVarianceTerm values"
                )
        reasons.extend(stochastic_reasons)
        bounds_a, bound_reasons_a = deterministic_bounds(evidence_a, evidence_metric)
        bounds_b, bound_reasons_b = deterministic_bounds(evidence_b, evidence_metric)
        reasons.extend(bound_reasons_a)
        reasons.extend(bound_reasons_b)

        provenance_a = token_provenance(evidence_a)
        provenance_b = token_provenance(evidence_b)
        usable_numeric_pair = (
            evidence_a.included
            and evidence_b.included
            and value_a is not None
            and value_b is not None
        )
        if usable_numeric_pair and ratio_estimand is not None:
            ratio_reasons = ratio_evidence_reasons(provenance_a, provenance_b)
            reasons.extend(ratio_reasons)
            usable_numeric_pair = not ratio_reasons
        block_rows.append(
            {
                "block_id": block_id,
                "bundle_a_id": evidence_a.bundle_id,
                "bundle_b_id": evidence_b.bundle_id,
                "included": usable_numeric_pair,
                "reason_codes": ordered_reason_codes(reasons),
            }
        )
        if usable_numeric_pair:
            included_by_condition[contrast["condition_a_id"]].append(evidence_a)
            included_by_condition[contrast["condition_b_id"]].append(evidence_b)
            observation_parts.append(
                {
                    "block_id": block_id,
                    "value_a": value_a,
                    "value_b": value_b,
                    "evidence_a": evidence_a,
                    "evidence_b": evidence_b,
                    "bounds_a": bounds_a,
                    "bounds_b": bounds_b,
                    "stochastic_terms": stochastic_terms,
                    "provenance_a": provenance_a,
                    "provenance_b": provenance_b,
                    "reason_codes": ordered_reason_codes(reasons),
                }
            )

    if ratio_estimand is not None and observation_parts:
        collection_reasons = ratio_collection_evidence_reasons(
            tuple(
                (part["provenance_a"], part["provenance_b"])
                for part in observation_parts
            )
        )
        if collection_reasons:
            global_reasons.extend(collection_reasons)
            for row in block_rows:
                if row["included"]:
                    row["included"] = False
                    row["reason_codes"] = ordered_reason_codes(
                        (*row["reason_codes"], *collection_reasons)
                    )
            observation_parts.clear()
            for evidence in included_by_condition.values():
                evidence.clear()

    complete_blocks = len(observation_parts)
    planned_n = inputs.manifest["design"]["sampling_plan"]["planned_n_blocks"]
    if complete_blocks < 2:
        global_reasons.append("insufficient_complete_blocks")
    if complete_blocks < planned_n:
        global_reasons.append("fixed_n_plan_incomplete")
    if any(not row["included"] for row in block_rows):
        global_reasons.append("paired_block_incomplete")

    deterministic_names: set[str] = set()
    if observation_parts:
        deterministic_names = set(observation_parts[0]["bounds_a"]) & set(
            observation_parts[0]["bounds_b"]
        )
        for part in observation_parts[1:]:
            deterministic_names &= set(part["bounds_a"]) & set(part["bounds_b"])

    # The clock-anchor-shift bound is REQUIRED on the anchor-envelope wires and
    # is consumed by the decision interval.  Term-name intersection silently
    # drops it whenever ONE side of a pair carries it and the other does not
    # (e.g. an anchor-era 0.5.1 bundle paired against a pre-anchor bundle that
    # additively records no such term).  A required bound that any observation
    # carries but the intersection would erase is under-bounding, exactly the
    # unsound direction the audit targets: refuse the whole contrast rather
    # than let the intersection hide it.
    anchor_term = "E_clock_anchor_shift_bound_j"
    anchor_present = any(
        anchor_term in part["bounds_a"] or anchor_term in part["bounds_b"]
        for part in observation_parts
    )
    if anchor_present and anchor_term not in deterministic_names:
        global_reasons.append("anchor_energy_envelope_unrecorded")
        for row in block_rows:
            if row["included"]:
                row["included"] = False
                row["reason_codes"] = ordered_reason_codes(
                    (*row["reason_codes"], "anchor_energy_envelope_unrecorded")
                )
        observation_parts.clear()
        for evidence in included_by_condition.values():
            evidence.clear()
    if ratio_estimand is None:
        observations = tuple(
            PairedObservation(
                block_id=part["block_id"],
                value_a=part["value_a"],
                value_b=part["value_b"],
                stochastic_terms=part["stochastic_terms"],
                deterministic_terms=tuple(
                    DeterministicBoundTerm(
                        name=name,
                        bound_a=part["bounds_a"][name],
                        bound_b=part["bounds_b"][name],
                    )
                    for name in sorted(deterministic_names)
                ),
            )
            for part in observation_parts
        )
    else:
        ratio_observations = []
        for part in observation_parts:
            observation, reasons = ratio_observation_from_evidence(
                block_id=part["block_id"],
                energy_a_j=part["value_a"],
                energy_b_j=part["value_b"],
                provenance_a=part["provenance_a"],
                provenance_b=part["provenance_b"],
                stochastic_terms=part["stochastic_terms"],
                deterministic_terms=tuple(
                    DeterministicBoundTerm(
                        name=name,
                        bound_a=part["bounds_a"][name],
                        bound_b=part["bounds_b"][name],
                    )
                    for name in sorted(deterministic_names)
                ),
            )
            if observation is None:
                raise AnalysisInputError(
                    "ratio evidence changed after eligibility check: " + ", ".join(reasons)
                )
            ratio_observations.append(observation)
        observations = tuple(ratio_observations)
    estimate = (
        estimate_manifest_observations(contrast["metric"], observations)
        if len(observations) >= 2
        else None
    )

    resolutions = _resolve_contrast_floor(
        inputs, contrast, included_by_condition, request_factory
    )
    floor = _combined_floor(resolutions)
    if ratio_estimand is not None:
        floor, floor_conversion_reasons = convert_floor_to_ratio_units(
            contrast["metric"], observations, floor
        )
        global_reasons.extend(floor_conversion_reasons)

    affected_entry_ids = {
        entry["entry_id"]
        for entry in inputs.manifest["entries"]
        if entry["cell_id"] in {contrast["cell_a_id"], contrast["cell_b_id"]}
    }
    affected_entry_ids.update(
        sentinel_entry_id
        for block_id in contrast["block_ids"]
        for sentinel_entry_id in sentinel_entries.get(block_id, ())
    )
    demoted = bool(affected_entry_ids & inputs.top_up_entry_ids)
    confirmatory_status = "demoted_exploratory" if demoted else "confirmatory"
    if demoted:
        global_reasons.append("outcome_dependent_top_up")
    if evidence_class == "legacy_l1":
        global_reasons.append("legacy_l1_mechanics_only")

    randomization = randomization_check(
        estimate.paired_values if estimate is not None else (),
        inputs.manifest["design"]["randomization"],
        alpha=_randomization_alpha(inputs.manifest, contrast),
        block_ids=(
            tuple(observation.block_id for observation in observations)
            if estimate is not None
            else ()
        ),
    )

    return {
        "manifest": contrast,
        "block_rows": block_rows,
        "observation_parts": observation_parts,
        "observations": observations,
        "estimate": estimate,
        "floor": floor,
        "floor_resolutions": tuple(resolutions),
        "global_reason_codes": ordered_reason_codes(global_reasons),
        "confirmatory_status": confirmatory_status,
        "randomization_check": randomization,
        "evidence_class": evidence_class,
    }


def _base_reasons(prepared: Mapping[str, Any], *, omit_block: str | None = None) -> list[str]:
    reasons = list(prepared["global_reason_codes"])
    for row in prepared["block_rows"]:
        if row["block_id"] != omit_block:
            reasons.extend(row["reason_codes"])
    if omit_block is not None:
        reasons = [reason for reason in reasons if reason != "fixed_n_plan_incomplete"]
    if prepared.get("estimate") is not None:
        # A missing metric in one excluded slot is preserved in that block's
        # audit, but >=2 complete pairs still support the B4 descriptive
        # estimate.  The fixed-n failure is not_resolvable, not not_estimable.
        reasons = [reason for reason in reasons if reason != "metric_missing_or_nonfinite"]
    return ordered_reason_codes(reasons)


def _interpolation_reasons(estimate: PairedEstimate | None, floor: Mapping[str, Any]) -> list[str]:
    if estimate is None or floor["active_floor_j"] is None:
        return []
    interpolation = next(
        (
            term.bound
            for term in estimate.deterministic_bounds
            if term.name == "E_interpolation_joint_edge_bound_j"
        ),
        None,
    )
    if interpolation is None:
        return ["interpolation_bound_unrecorded"]
    reasons: list[str] = []
    if interpolation >= floor["active_floor_j"]:
        reasons.append("interpolation_bound_exceeds_floor")
    if interpolation >= 0.5 * abs(estimate.estimate):
        reasons.append("interpolation_bound_exceeds_half_effect")
    return reasons


def _subset_floor(
    inputs: LoadedAnalysisInputs,
    prepared: Mapping[str, Any],
    request_factory: _FloorRequestFactory | None,
    *,
    omit_block: str,
) -> tuple[dict[str, Any], tuple[FloorResolution, ...]]:
    contrast = prepared["manifest"]
    included: dict[str, list[BundleEvidence]] = {
        contrast["condition_a_id"]: [],
        contrast["condition_b_id"]: [],
    }
    for part in prepared["observation_parts"]:
        if part["block_id"] == omit_block:
            continue
        included[contrast["condition_a_id"]].append(part["evidence_a"])
        included[contrast["condition_b_id"]].append(part["evidence_b"])
    resolutions = tuple(
        _resolve_contrast_floor(inputs, contrast, included, request_factory)
    )
    floor = _combined_floor(resolutions)
    metric = contrast.get("metric")
    if not isinstance(metric, Mapping) or metric.get("ratio_estimand") is None:
        return floor, resolutions
    observations = tuple(
        observation
        for observation in prepared["observations"]
        if observation.block_id != omit_block
    )
    converted, _ = convert_floor_to_ratio_units(
        metric, observations, floor
    )
    return converted, resolutions


def _analysis_reasons(
    prepared: Mapping[str, Any],
    estimate: PairedEstimate | None,
    floor: Mapping[str, Any],
    floor_resolutions: Sequence[FloorResolution],
    randomization: Mapping[str, Any],
    *,
    omit_block: str | None = None,
) -> list[str]:
    reasons = _base_reasons(prepared, omit_block=omit_block)
    reasons.extend(_floor_engine_reasons(floor_resolutions))
    reasons.extend(_interpolation_reasons(estimate, floor))
    if randomization.get("reason") is not None:
        reasons.append(randomization["reason"])
    return ordered_reason_codes(reasons)


def _evaluation(
    prepared: Mapping[str, Any],
    estimate: PairedEstimate | None,
    multiplicity: Mapping[str, Any],
    reasons: Sequence[str],
    *,
    sensitivity_blocking: bool = False,
    floor: Mapping[str, Any] | None = None,
    randomization: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    all_reasons = list(reasons)
    active_floor = prepared["floor"] if floor is None else floor
    active_randomization = (
        prepared["randomization_check"] if randomization is None else randomization
    )
    if (
        active_randomization["status"] == "clean"
        and active_randomization["rejects"] is not None
        and bool(active_randomization["rejects"]) != bool(multiplicity["rejected"])
    ):
        all_reasons.append("randomization_sensitivity_disagrees")
        sensitivity_blocking = True
    floor_metadata = (
        {
            "floor_source": active_floor["floor_source"],
            "floor_limit_class": active_floor["floor_limit_class"],
            "point_floor_diagnostics": active_floor[
                "point_floor_diagnostics"
            ],
            "single_count_discipline": active_floor[
                "single_count_discipline"
            ],
        }
        if active_floor.get("floor_limit_class")
        == ATTRIBUTION_LIMIT_CLASS
        else None
    )
    return evaluate_claim(
        estimate=estimate.estimate if estimate is not None else None,
        metrology_aware_ci95=(
            _interval_dict(estimate.metrology_aware_ci95) if estimate is not None else None
        ),
        decision_interval=(
            _interval_dict(estimate.decision_interval) if estimate is not None else None
        ),
        floor_gate_j=active_floor["active_floor_j"],
        adjusted_rejected=bool(multiplicity["rejected"]),
        base_reason_codes=ordered_reason_codes(all_reasons),
        equivalence=prepared["manifest"].get("equivalence"),
        claim_role=prepared["manifest"]["claim_role"],
        confirmatory_status=prepared["confirmatory_status"],
        evidence_class=prepared["evidence_class"],
        sensitivity_blocking=sensitivity_blocking,
        floor_metadata=floor_metadata,
    )


def _claim_raw_p(prepared: Mapping[str, Any], estimate: PairedEstimate | None) -> float | None:
    if estimate is None:
        return None
    if "fixed_n_plan_incomplete" in prepared.get("global_reason_codes", ()):
        # The descriptive complete-case estimate remains visible, but the
        # missing confirmatory hypothesis stays an explicit None in the
        # frozen-m family rather than influencing another contrast's order.
        return None
    equivalence = prepared["manifest"].get("equivalence")
    if equivalence is None:
        return estimate.raw_p
    if (
        not isinstance(equivalence, Mapping)
        or equivalence.get("method") != "tost_v1"
        or isinstance(equivalence.get("margin"), bool)
        or not isinstance(equivalence.get("margin"), (int, float))
    ):
        return None
    return tost_p_value(
        estimate.estimate,
        estimate.se_total,
        estimate.df,
        float(equivalence["margin"]),
    )[2]


def _family_adjustments(
    manifest: Mapping[str, Any], prepared_by_id: Mapping[str, Mapping[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    family_rows: list[dict[str, Any]] = []
    adjusted_by_id: dict[str, dict[str, Any]] = {}
    for family in manifest["families"]:
        multiplicity = family["multiplicity"]
        raw = {
            contrast_id: (
                _claim_raw_p(
                    prepared_by_id[contrast_id],
                    prepared_by_id[contrast_id]["estimate"],
                )
            )
            for contrast_id in family["contrast_ids"]
        }
        adjusted = adjust_p_values(
            raw,
            method=multiplicity["method"],
            m=multiplicity["m"],
            alpha=multiplicity["alpha"],
            q=multiplicity["q"],
        )
        adjusted_by_id.update(adjusted)
        raw_ordering = [
            contrast_id
            for _, contrast_id in sorted(
                (p_value, contrast_id)
                for contrast_id, p_value in raw.items()
                if p_value is not None
            )
        ]
        family_rows.append(
            {
                "family_instance_id": family["family_instance_id"],
                "plan_id": family["plan_id"],
                "claim_role": family["claim_role"],
                "method": multiplicity["method"],
                "alpha": multiplicity["alpha"],
                "q": multiplicity["q"],
                "m": multiplicity["m"],
                "contrast_ids": list(family["contrast_ids"]),
                "finite_test_count": sum(value is not None for value in raw.values()),
                "raw_ordering": raw_ordering,
                "adjusted_p_values": {
                    contrast_id: adjusted[contrast_id]["adjusted_p"]
                    for contrast_id in family["contrast_ids"]
                },
                "missing_test_ids": sorted(
                    contrast_id for contrast_id, value in raw.items() if value is None
                ),
                "structural_status": "complete",
            }
        )
    return family_rows, adjusted_by_id


def _loo_family(
    inputs: LoadedAnalysisInputs,
    family: Mapping[str, Any],
    prepared_by_id: Mapping[str, Mapping[str, Any]],
    full_adjusted: Mapping[str, Mapping[str, Any]],
    full_evaluations: Mapping[str, Mapping[str, Any]],
    request_factory: _FloorRequestFactory | None,
) -> dict[str, list[dict[str, Any]]]:
    contrast_ids = family["contrast_ids"]
    complete_ids = {
        contrast_id
        for contrast_id in contrast_ids
        if len(prepared_by_id[contrast_id]["observations"])
        == len(prepared_by_id[contrast_id]["manifest"]["block_ids"])
    }
    if not complete_ids:
        return {contrast_id: [] for contrast_id in contrast_ids}
    block_ids = list(prepared_by_id[contrast_ids[0]]["manifest"]["block_ids"])
    if len(block_ids) > 10:
        return {contrast_id: [] for contrast_id in contrast_ids}
    rows: dict[str, list[dict[str, Any]]] = {contrast_id: [] for contrast_id in contrast_ids}
    multiplicity = family["multiplicity"]
    for omitted_block in block_ids:
        estimates: dict[str, PairedEstimate | None] = {}
        floors: dict[str, dict[str, Any]] = {}
        floor_resolutions: dict[str, tuple[FloorResolution, ...]] = {}
        randomizations: dict[str, Mapping[str, Any]] = {}
        raw: dict[str, float | None] = {}
        for contrast_id in contrast_ids:
            observations = tuple(
                observation
                for observation in prepared_by_id[contrast_id]["observations"]
                if observation.block_id != omitted_block
            )
            estimate = (
                estimate_manifest_observations(
                    prepared_by_id[contrast_id]["manifest"]["metric"], observations
                )
                if len(observations) >= 2
                else None
            )
            estimates[contrast_id] = estimate
            floor, resolutions = _subset_floor(
                inputs,
                prepared_by_id[contrast_id],
                request_factory,
                omit_block=omitted_block,
            )
            floors[contrast_id] = floor
            floor_resolutions[contrast_id] = resolutions
            randomizations[contrast_id] = randomization_check(
                estimate.paired_values if estimate is not None else (),
                randomization_design_for_blocks(
                    inputs.manifest["design"]["randomization"],
                    tuple(observation.block_id for observation in observations),
                ),
                alpha=_randomization_alpha(
                    inputs.manifest,
                    prepared_by_id[contrast_id]["manifest"],
                ),
                block_ids=(
                    tuple(observation.block_id for observation in observations)
                    if estimate is not None
                    else ()
                ),
            )
            raw[contrast_id] = _claim_raw_p(prepared_by_id[contrast_id], estimate)
        adjusted = adjust_p_values(
            raw,
            method=multiplicity["method"],
            m=multiplicity["m"],
            alpha=multiplicity["alpha"],
            q=multiplicity["q"],
        )
        for contrast_id in contrast_ids:
            if contrast_id not in complete_ids:
                continue
            prepared = prepared_by_id[contrast_id]
            estimate = estimates[contrast_id]
            floor = floors[contrast_id]
            reasons = _analysis_reasons(
                prepared,
                estimate,
                floor,
                floor_resolutions[contrast_id],
                randomizations[contrast_id],
                omit_block=omitted_block,
            )
            evaluation = _evaluation(
                prepared,
                estimate,
                adjusted[contrast_id],
                reasons,
                floor=floor,
                randomization=randomizations[contrast_id],
            )
            active_threshold = prepared["manifest"].get("mde")
            if not isinstance(active_threshold, (int, float)) or isinstance(active_threshold, bool):
                active_threshold = floor["active_floor_j"]
            full_estimate = prepared["estimate"]
            assert full_estimate is not None and estimate is not None
            floor_status = (
                "above_floor"
                if floor["active_floor_j"] is not None
                and abs(estimate.estimate) > floor["active_floor_j"]
                else "not_above_floor"
            )
            full_floor_status = (
                "above_floor"
                if prepared["floor"]["active_floor_j"] is not None
                and abs(full_estimate.estimate) > prepared["floor"]["active_floor_j"]
                else "not_above_floor"
            )
            comparison = {
                "estimate": estimate.estimate,
                "floor_status": floor_status,
                "adjusted_rejection": adjusted[contrast_id]["rejected"],
                "outcome": evaluation["outcome"],
            }
            triggers = influence_triggers(
                {
                    "estimate": full_estimate.estimate,
                    "floor_status": full_floor_status,
                    "adjusted_rejection": full_adjusted[contrast_id]["rejected"],
                    "outcome": full_evaluations[contrast_id]["outcome"],
                },
                comparison,
                active_threshold=(
                    float(active_threshold) if active_threshold is not None else None
                ),
            )
            rows[contrast_id].append(
                {
                    "omitted_block_id": omitted_block,
                    "n_blocks": estimate.n,
                    "df": estimate.df,
                    "estimate": estimate.estimate,
                    "metrology_aware_ci95": _interval_dict(estimate.metrology_aware_ci95),
                    "decision_interval": _interval_dict(estimate.decision_interval),
                    "floor_status": floor_status,
                    "raw_p": _claim_raw_p(prepared, estimate),
                    "adjusted_p": adjusted[contrast_id]["adjusted_p"],
                    "outcome": evaluation["outcome"],
                    "influence_triggers": triggers,
                }
            )
    return rows


def _contrast_row(
    prepared: Mapping[str, Any],
    multiplicity: Mapping[str, Any],
    evaluation: Mapping[str, Any],
    loo_rows: Sequence[Mapping[str, Any]],
    sensitivity_status: str,
) -> dict[str, Any]:
    contrast = prepared["manifest"]
    estimate = prepared["estimate"]
    included_bundle_ids = sorted(
        {
            bundle_id
            for row in prepared["block_rows"]
            if row["included"]
            for bundle_id in (row["bundle_a_id"], row["bundle_b_id"])
            if bundle_id is not None
        }
    )
    deterministic = {
        "terms": (
            [asdict(value) for value in estimate.deterministic_bounds]
            if estimate is not None
            else []
        ),
        "total": estimate.deterministic_bound_total if estimate is not None else None,
        "decision_interval": _interval_dict(estimate.decision_interval) if estimate else None,
    }
    return {
        "contrast_id": contrast["contrast_id"],
        "plan_id": contrast["plan_id"],
        "family_instance_id": contrast["family_instance_id"],
        "claim_role": contrast["claim_role"],
        "metric": dict(contrast["metric"]),
        "conditions": {
            "condition_a_id": contrast["condition_a_id"],
            "condition_b_id": contrast["condition_b_id"],
            "cell_a_id": contrast["cell_a_id"],
            "cell_b_id": contrast["cell_b_id"],
            "difference_orientation": "condition_b_minus_condition_a",
        },
        "hypothesized_direction": contrast.get("hypothesized_direction"),
        "equivalence": (
            dict(contrast["equivalence"])
            if isinstance(contrast.get("equivalence"), Mapping)
            else None
        ),
        "mde": contrast.get("mde"),
        "bundle_blocks": {
            "planned_block_ids": list(contrast["block_ids"]),
            "included_bundle_ids": included_bundle_ids,
            "blocks": list(prepared["block_rows"]),
        },
        "sampling": {
            "confirmatory_status": prepared["confirmatory_status"],
            "planned_n": len(contrast["block_ids"]),
            "observed_complete_n": len(prepared["observations"]),
        },
        "estimator": _estimator_dict(estimate, contrast["estimator"], len(prepared["observations"])),
        "deterministic_bounds": deterministic,
        "floor": dict(prepared["floor"]),
        "multiplicity": {
            "raw_p": multiplicity["raw_p"],
            "adjusted_p": multiplicity["adjusted_p"],
            "rejected": multiplicity["rejected"],
        },
        "randomization_check": dict(prepared["randomization_check"]),
        "loo": {
            "status": "not_required" if len(prepared["observations"]) > 10 else (
                "not_run" if not loo_rows else "complete"
            ),
            "rows": list(loo_rows),
        },
        "sensitivity_status": sensitivity_status,
        "claim_evaluation": dict(evaluation),
    }


def analyze_claims(
    analysis_manifest_path: Path,
    runs_root: Path,
    floor_artifact_path: Path,
    *,
    strict_validator: Any,
    evidence_roots: Mapping[str, Path] | None = None,
    output_path: Path | None = None,
    legacy_l1_mechanics: bool = False,
    legacy_allowlist: frozenset[tuple[str, str]] | None = None,
    _floor_request_factory: _FloorRequestFactory | None = None,
    _pair_stochastic_factory: _PairStochasticFactory | None = None,
) -> dict[str, Any]:
    """Derive a deterministic verdict artifact from frozen inputs.

    Invalid manifest/floor/strict input structure raises
    :class:`AnalysisInputError`.  Scientific negative/null outcomes remain a
    successful derivation and are encoded in the returned artifact.
    """

    if output_path is not None:
        _validate_output_separation(
            Path(output_path),
            Path(analysis_manifest_path),
            Path(runs_root),
            Path(floor_artifact_path),
            declared_evidence_roots(
                Path(floor_artifact_path),
                evidence_roots,
            ),
        )

    inputs = load_analysis_inputs(
        Path(analysis_manifest_path),
        Path(runs_root),
        Path(floor_artifact_path),
        strict_validator=strict_validator,
        evidence_roots=evidence_roots,
    )
    evidence_class = "legacy_l1" if legacy_l1_mechanics else "current"
    if legacy_l1_mechanics:
        if legacy_allowlist is None:
            raise AnalysisInputError("legacy mechanics requires the frozen legacy allowlist")
        observed = {
            (evidence.bundle_id, evidence.config_sha256)
            for evidence in (*inputs.registered.values(), *inputs.extra_audits)
            if evidence.path.is_dir()
        }
        if observed != legacy_allowlist:
            raise AnalysisInputError(
                "legacy mechanics requires exactly the frozen six-bundle allowlist"
            )

    sentinel_entries = _sentinel_entries_by_block(inputs.manifest)
    prepared_by_id = {
        contrast["contrast_id"]: _prepare_contrast(
            inputs,
            contrast,
            sentinel_entries,
            _floor_request_factory,
            _pair_stochastic_factory,
            evidence_class=evidence_class,
        )
        for contrast in inputs.manifest["contrasts"]
    }
    family_rows, adjusted_by_id = _family_adjustments(inputs.manifest, prepared_by_id)
    full_evaluations: dict[str, dict[str, Any]] = {}
    for contrast_id, prepared in prepared_by_id.items():
        reasons = _analysis_reasons(
            prepared,
            prepared["estimate"],
            prepared["floor"],
            prepared["floor_resolutions"],
            prepared["randomization_check"],
        )
        full_evaluations[contrast_id] = _evaluation(
            prepared,
            prepared["estimate"],
            adjusted_by_id[contrast_id],
            ordered_reason_codes(reasons),
        )

    loo_by_id: dict[str, list[dict[str, Any]]] = {
        contrast_id: [] for contrast_id in prepared_by_id
    }
    for family in inputs.manifest["families"]:
        family_rows_by_id = _loo_family(
            inputs,
            family,
            prepared_by_id,
            adjusted_by_id,
            full_evaluations,
            _floor_request_factory,
        )
        for contrast_id, rows in family_rows_by_id.items():
            loo_by_id[contrast_id].extend(rows)

    contrast_rows: list[dict[str, Any]] = []
    for contrast in inputs.manifest["contrasts"]:
        contrast_id = contrast["contrast_id"]
        prepared = prepared_by_id[contrast_id]
        rows = loo_by_id[contrast_id]
        _, verdict_influential, magnitude_only = summarize_loo(rows)
        emitted_loo_status = (
            "not_required"
            if len(prepared["observations"]) > 10
            else "not_run"
            if not rows
            else "complete"
        )
        reasons = list(full_evaluations[contrast_id]["reason_codes"])
        sensitivity_blocking = False
        if verdict_influential:
            reasons.append("loo_verdict_influential")
            sensitivity_blocking = True
        elif magnitude_only:
            reasons.append("loo_magnitude_influential")
        evaluation = _evaluation(
            prepared,
            prepared["estimate"],
            adjusted_by_id[contrast_id],
            ordered_reason_codes(reasons),
            sensitivity_blocking=sensitivity_blocking,
        )
        randomization_status = prepared["randomization_check"]["status"]
        sensitivity_status = (
            "concern"
            if verdict_influential
            or magnitude_only
            or "randomization_sensitivity_disagrees" in evaluation["reason_codes"]
            else "not_run"
            if randomization_status == "not_run" or emitted_loo_status == "not_run"
            else "clean"
            if rows or randomization_status == "clean"
            else "not_required"
        )
        contrast_rows.append(
            _contrast_row(
                prepared,
                adjusted_by_id[contrast_id],
                evaluation,
                rows,
                sensitivity_status,
            )
        )

    all_audits = list(inputs.registered.values()) + list(inputs.extra_audits)
    demoted_ids = sorted(
        row["contrast_id"]
        for row in contrast_rows
        if row["sampling"]["confirmatory_status"] == "demoted_exploratory"
    )
    registered_blocks = sorted(
        {
            entry["block_id"]
            for entry in inputs.manifest["entries"]
            if entry["role"] == "condition"
        }
    )
    body = {
        "schema_version": "joulewise.claim_verdicts.v1",
        "claim_verdicts_id": "",
        "engine": {
            "implementation": "joulewise.analysis_engine",
            "algorithm_version": "1",
            "difference_orientation": "condition_b_minus_condition_a",
            "policy_identity": {
                "floor_resolution": _private_factory_identity(
                    _floor_request_factory, _FLOOR_POLICY_ID
                ),
                "stochastic_variance": _private_factory_identity(
                    _pair_stochastic_factory, _STOCHASTIC_POLICY_ID
                ),
                "campaign_cooldown": _COOLDOWN_POLICY_ID,
            },
        },
        "inputs": {
            "analysis_manifest": {
                "manifest_id": inputs.manifest["manifest_id"],
                "file_sha256": inputs.manifest_sha256,
            },
            "floor_artifact": {
                "artifact_id": inputs.floor_artifact["artifact_id"],
                "file_sha256": inputs.floor_sha256,
            },
            "runs_root_label": Path(runs_root).name or "runs",
            "evidence_class": evidence_class,
            "limitations": ["legacy_l1_mechanics_only"] if legacy_l1_mechanics else [],
        },
        "bundle_audit": [
            evidence.audit_row()
            for evidence in sorted(
                all_audits, key=lambda value: (str(value.entry.get("entry_id")), value.bundle_id)
            )
        ],
        "sampling_audit": {
            "design": inputs.manifest["design"]["sampling_plan"]["design"],
            "planned_n_blocks": inputs.manifest["design"]["sampling_plan"]["planned_n_blocks"],
            "registered_blocks": registered_blocks,
            "valid_replacements": list(inputs.valid_replacements),
            "unregistered_matching_bundles": list(inputs.unregistered_matching),
            "top_up_detected": bool(inputs.unregistered_matching),
            "demoted_contrast_ids": demoted_ids,
        },
        "families": family_rows,
        "contrasts": contrast_rows,
    }
    artifact = finalize_claim_verdicts(body)
    if output_path is not None:
        write_claim_verdicts_atomic(Path(output_path), artifact)
    return artifact


__all__ = [
    "AnalysisInputError",
    "analyze_claims",
    "estimate_manifest_observations",
    "estimation_metric",
    "ratio_collection_evidence_reasons",
    "ratio_evidence_reasons",
    "ratio_observation_from_evidence",
    "validate_ratio_estimand",
]
