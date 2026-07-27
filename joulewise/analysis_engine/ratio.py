"""Frozen manifest policy and evidence assembly for B8 ratio estimands.

The current P2-042 AP-2 manifest validator deliberately admits only
``ratio_estimand: null``.  This module is therefore a narrow public seam for
the already-adjudicated B8 contract: a future validator can admit the frozen
ratio object without making the analysis engine choose an estimand after
observing denominators.
"""

from __future__ import annotations

import copy
import json
import math
from collections.abc import Mapping, Sequence
from typing import Any

from joulewise.provenance import FIXED_BUDGET_EXACT, FIXED_BUDGET_INCOMPLETE

from .claims import ordered_reason_codes
from .estimators import (
    DeterministicBoundTerm,
    PairedEstimate,
    PairedObservation,
    RUNTIME_TOKEN_SOURCES,
    RatioObservation,
    StochasticVarianceTerm,
    estimate_mean_of_request_ratios,
    estimate_paired_blocks,
    estimate_ratio_of_totals,
)


RATIO_ESTIMAND_KEYS = frozenset(
    {
        "form",
        "numerator_metric",
        "denominator",
        "denominator_unit",
        "tokenizer_scope",
        "output_policy_scope",
    }
)
RATIO_FORMS = frozenset({"mean_of_request_ratios", "ratio_of_totals"})


def convert_floor_to_ratio_units(
    metric: Mapping[str, Any],
    observations: Sequence[RatioObservation],
    floor: Mapping[str, Any],
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Convert the two condition-specific joule floors to ``J/token``.

    Each selected floor resolution belongs to condition A or B in manifest
    order.  A mean-of-request-ratios floor applies the corresponding runtime
    denominator request by request; a ratio-of-totals floor applies the
    numerator floor to the condition total.  The two condition contributions
    add because either numerator can move the B-minus-A ratio contrast.
    """

    converted = copy.deepcopy(dict(floor))
    ratio = metric.get("ratio_estimand")
    if ratio is None or floor.get("status") != "resolved":
        return converted, ()
    frozen = validate_ratio_estimand(ratio)
    resolutions = converted.get("resolutions")
    if (
        not observations
        or not isinstance(resolutions, list)
        or len(resolutions) != 2
        or any(not isinstance(value, RatioObservation) for value in observations)
    ):
        return converted, ("ratio_floor_conversion_undefined",)
    tokens_a = [value.output_tokens_a for value in observations]
    tokens_b = [value.output_tokens_b for value in observations]
    if any(
        isinstance(value, bool) or not isinstance(value, int) or value <= 0
        for value in (*tokens_a, *tokens_b)
    ):
        return converted, ("ratio_floor_conversion_undefined",)

    if frozen["form"] == "mean_of_request_ratios":
        factors = (
            sum(1.0 / value for value in tokens_a) / len(tokens_a),
            sum(1.0 / value for value in tokens_b) / len(tokens_b),
        )
    else:
        factors = (
            len(tokens_a) / sum(tokens_a),
            len(tokens_b) / sum(tokens_b),
        )

    published_diagnostics = (
        {}
        if isinstance(converted.get("point_floor_diagnostics"), Mapping)
        else None
    )
    for resolution, factor in zip(resolutions, factors, strict=True):
        if not isinstance(resolution, dict):
            return converted, ("ratio_floor_conversion_undefined",)
        for key in ("floor_abs_j", "floor_cmp_j", "floor_gate_j"):
            value = resolution.get(key)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                or float(value) < 0.0
            ):
                return converted, ("ratio_floor_conversion_undefined",)
            resolution[key] = float(value) * factor
        diagnostics = resolution.get("point_floor_diagnostics")
        if diagnostics is not None:
            stack = [diagnostics]
            while stack:
                diagnostic = stack.pop()
                if not isinstance(diagnostic, dict):
                    return converted, ("ratio_floor_conversion_undefined",)
                for key, value in diagnostic.items():
                    if key in ("unguarded_floor_j", "guarded_floor_j"):
                        if value is None:
                            continue
                        if (
                            isinstance(value, bool)
                            or not isinstance(value, (int, float))
                            or not math.isfinite(float(value))
                            or float(value) < 0.0
                        ):
                            return converted, (
                                "ratio_floor_conversion_undefined",
                            )
                        diagnostic[key] = float(value) * factor
                    elif isinstance(value, dict):
                        stack.append(value)
            if published_diagnostics is not None:
                source_ids = resolution.get("source_cell_ids")
                if not isinstance(source_ids, list):
                    return converted, ("ratio_floor_conversion_undefined",)
                if resolution.get("status") == "transported":
                    published_diagnostics.update(copy.deepcopy(diagnostics))
                else:
                    for source_id in source_ids:
                        if not isinstance(source_id, str):
                            return converted, (
                                "ratio_floor_conversion_undefined",
                            )
                        published_diagnostics[source_id] = copy.deepcopy(
                            diagnostics
                        )

    converted["floor_abs_j"] = sum(
        float(value["floor_abs_j"]) for value in resolutions
    )
    converted["floor_cmp_j"] = sum(
        float(value["floor_cmp_j"]) for value in resolutions
    )
    converted["active_floor_j"] = max(
        converted["floor_abs_j"], converted["floor_cmp_j"]
    )
    if published_diagnostics is not None:
        converted["point_floor_diagnostics"] = published_diagnostics
    return converted, ()


def validate_ratio_estimand(value: object) -> Mapping[str, Any]:
    """Return one exact B8 ratio object or raise a fail-closed input error."""

    if not isinstance(value, Mapping) or set(value) != RATIO_ESTIMAND_KEYS:
        raise ValueError("ratio_estimand must be an exact adjudicated B8 object")
    if value.get("form") not in RATIO_FORMS:
        raise ValueError("ratio_estimand.form must be frozen before analysis")
    expected = {
        "numerator_metric": "energy_request_j",
        "denominator": "runtime_observed_output_tokens",
        "denominator_unit": "token",
        "tokenizer_scope": "same_identity_required",
        "output_policy_scope": "same_policy_required",
    }
    for key, required in expected.items():
        if value.get(key) != required:
            raise ValueError(f"ratio_estimand.{key} must equal {required!r}")
    return value


def estimation_metric(metric: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return the numerator metric used to gather ratio evidence.

    The original mapping remains the artifact metric.  Only evidence lookup,
    window gating, and energy-error propagation use this derived numerator
    view.
    """

    ratio = metric.get("ratio_estimand")
    if ratio is None:
        return metric
    frozen = validate_ratio_estimand(ratio)
    result = dict(metric)
    result["name"] = frozen["numerator_metric"]
    result["unit"] = "J"
    result["ratio_estimand"] = None
    return result


def _canonical_identity(value: object) -> str | None:
    if not isinstance(value, Mapping) or not value:
        return None
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError):
        return None


def _output_policy_identity(value: object) -> str | None:
    if not isinstance(value, Mapping):
        return None
    name = value.get("name")
    requested = value.get("requested_tokens")
    emitted = value.get("emitted_tokens")
    sampler = value.get("sampler")
    if (
        not isinstance(name, str)
        or not name
        or isinstance(requested, bool)
        or not isinstance(requested, int)
        or requested <= 0
        or isinstance(emitted, bool)
        or not isinstance(emitted, int)
        or emitted < 0
        or (sampler is not None and not isinstance(sampler, Mapping))
    ):
        return None
    return _canonical_identity(
        {
            "name": name,
            "requested_tokens": requested,
            "sampler": dict(sampler) if isinstance(sampler, Mapping) else None,
        }
    )


def ratio_evidence_reasons(
    provenance_a: Mapping[str, Any],
    provenance_b: Mapping[str, Any],
) -> tuple[str, ...]:
    """Map unusable token evidence to the exact frozen B14 vocabulary."""

    reasons: list[str] = []
    for provenance in (provenance_a, provenance_b):
        tokens = provenance.get("output_tokens")
        source = provenance.get("token_count_source")
        if (
            isinstance(tokens, bool)
            or not isinstance(tokens, int)
            or tokens <= 0
            or source not in RUNTIME_TOKEN_SOURCES
        ):
            reasons.append("runtime_token_denominator_required")
        stop_reason = provenance.get("stop_reason")
        if not isinstance(stop_reason, str) or not stop_reason:
            reasons.append("stop_reason_required")
        if _output_policy_identity(provenance.get("output_policy")) is None:
            reasons.append("output_policy_required")
        reasons.extend(_realized_output_reasons(provenance))
        if _canonical_identity(provenance.get("tokenizer_identity")) is None:
            reasons.append("tokenizer_identity_mismatch")

    sources = {
        provenance.get("token_count_source")
        for provenance in (provenance_a, provenance_b)
        if provenance.get("token_count_source") in RUNTIME_TOKEN_SOURCES
    }
    if len(sources) > 1:
        reasons.append("runtime_token_denominator_required")

    policy_a = _output_policy_identity(provenance_a.get("output_policy"))
    policy_b = _output_policy_identity(provenance_b.get("output_policy"))
    if policy_a is not None and policy_b is not None and policy_a != policy_b:
        reasons.append("output_policy_required")
    tokenizer_a = _canonical_identity(provenance_a.get("tokenizer_identity"))
    tokenizer_b = _canonical_identity(provenance_b.get("tokenizer_identity"))
    if (
        tokenizer_a is not None
        and tokenizer_b is not None
        and tokenizer_a != tokenizer_b
    ):
        reasons.append("tokenizer_identity_mismatch")
    return tuple(ordered_reason_codes(reasons))


def _realized_output_reasons(provenance: Mapping[str, Any]) -> list[str]:
    """Fail closed unless configured, observed, and token evidence agree."""

    reasons: list[str] = []
    tokens = provenance.get("output_tokens")
    policy = provenance.get("output_policy")
    emitted = policy.get("emitted_tokens") if isinstance(policy, Mapping) else None
    if (
        isinstance(emitted, bool)
        or not isinstance(emitted, int)
        or emitted < 0
        or emitted != tokens
    ):
        reasons.append("runtime_token_denominator_required")
    if not isinstance(policy, Mapping):
        return reasons

    items = policy.get("realized_items")
    if items is None:
        name = policy.get("name")
        if name in {FIXED_BUDGET_EXACT, FIXED_BUDGET_INCOMPLETE} and (
            name != FIXED_BUDGET_EXACT
            or policy.get("requested_tokens") != emitted
            or provenance.get("stop_reason") != "requested_tokens_emitted"
        ):
            reasons.append("output_policy_required")
        return reasons

    if not isinstance(items, (list, tuple)) or not items:
        return reasons + ["runtime_token_denominator_required", "stop_reason_required"]
    item_total = 0
    for item in items:
        if not isinstance(item, Mapping):
            reasons.append("runtime_token_denominator_required")
            continue
        # Suite item records and item-end markers are independently persisted
        # views of the same realized outcome.  Neither may silently override a
        # conflicting peer: policy admission fails closed on any disagreement.
        if item.get("record_marker_agreement") is not True:
            reasons.append("output_policy_required")
        item_requested = item.get("requested_tokens")
        item_emitted = item.get("emitted_tokens")
        item_stop = item.get("stop_reason")
        if (
            isinstance(item_requested, bool)
            or not isinstance(item_requested, int)
            or item_requested <= 0
            or isinstance(item_emitted, bool)
            or not isinstance(item_emitted, int)
            or item_emitted < 0
            or item.get("token_evidence_count") != item_emitted
            or (
                item.get("emitted_token_ids_count") is not None
                and item.get("emitted_token_ids_count") != item_emitted
            )
        ):
            reasons.append("runtime_token_denominator_required")
            continue
        item_total += item_emitted
        if not isinstance(item_stop, str) or not item_stop:
            reasons.append("stop_reason_required")
        item_policy = item.get("output_policy")
        if item_policy == FIXED_BUDGET_EXACT and (
            item.get("status") != "succeeded"
            or item_requested != item_emitted
            or item_stop != "requested_tokens_emitted"
        ):
            reasons.append("output_policy_required")
        elif item_policy not in {FIXED_BUDGET_EXACT, "natural_eos"}:
            reasons.append("output_policy_required")
        if item.get("status") not in {"succeeded", "capped"}:
            reasons.append("runtime_token_denominator_required")
    if item_total != emitted:
        reasons.append("runtime_token_denominator_required")
    return reasons


def ratio_collection_evidence_reasons(
    provenance_pairs: Sequence[tuple[Mapping[str, Any], Mapping[str, Any]]],
) -> tuple[str, ...]:
    """Reject source, tokenizer, or policy drift across otherwise valid blocks."""

    reasons: list[str] = []
    sources: set[object] = set()
    policies: set[str] = set()
    tokenizers: set[str] = set()
    for provenance_a, provenance_b in provenance_pairs:
        reasons.extend(ratio_evidence_reasons(provenance_a, provenance_b))
        sources.update(
            provenance.get("token_count_source")
            for provenance in (provenance_a, provenance_b)
            if provenance.get("token_count_source") in RUNTIME_TOKEN_SOURCES
        )
        for provenance in (provenance_a, provenance_b):
            policy = _output_policy_identity(provenance.get("output_policy"))
            tokenizer = _canonical_identity(provenance.get("tokenizer_identity"))
            if policy is not None:
                policies.add(policy)
            if tokenizer is not None:
                tokenizers.add(tokenizer)
    if len(sources) > 1:
        reasons.append("runtime_token_denominator_required")
    if len(policies) > 1:
        reasons.append("output_policy_required")
    if len(tokenizers) > 1:
        reasons.append("tokenizer_identity_mismatch")
    return tuple(ordered_reason_codes(reasons))


def ratio_observation_from_evidence(
    *,
    block_id: str,
    energy_a_j: float,
    energy_b_j: float,
    provenance_a: Mapping[str, Any],
    provenance_b: Mapping[str, Any],
    stochastic_terms: tuple[StochasticVarianceTerm, ...] = (),
    deterministic_terms: tuple[DeterministicBoundTerm, ...] = (),
) -> tuple[RatioObservation | None, tuple[str, ...]]:
    """Build one ratio block, preserving missing evidence as reason codes."""

    reasons = ratio_evidence_reasons(provenance_a, provenance_b)
    if reasons:
        return None, reasons
    policy_a = _output_policy_identity(provenance_a["output_policy"])
    policy_b = _output_policy_identity(provenance_b["output_policy"])
    tokenizer_a = _canonical_identity(provenance_a["tokenizer_identity"])
    tokenizer_b = _canonical_identity(provenance_b["tokenizer_identity"])
    assert policy_a is not None and policy_b is not None
    assert tokenizer_a is not None and tokenizer_b is not None
    return (
        RatioObservation(
            block_id=block_id,
            energy_a_j=energy_a_j,
            energy_b_j=energy_b_j,
            output_tokens_a=provenance_a["output_tokens"],
            output_tokens_b=provenance_b["output_tokens"],
            token_count_source_a=provenance_a["token_count_source"],
            token_count_source_b=provenance_b["token_count_source"],
            stop_reason_a=provenance_a["stop_reason"],
            stop_reason_b=provenance_b["stop_reason"],
            output_policy_a=policy_a,
            output_policy_b=policy_b,
            tokenizer_identity_a=tokenizer_a,
            tokenizer_identity_b=tokenizer_b,
            energy_stochastic_terms=stochastic_terms,
            energy_deterministic_terms=deterministic_terms,
        ),
        (),
    )


def estimate_manifest_observations(
    metric: Mapping[str, Any],
    observations: Sequence[PairedObservation] | Sequence[RatioObservation],
) -> PairedEstimate:
    """Dispatch only the form prospectively frozen in ``metric``."""

    ratio = metric.get("ratio_estimand")
    if ratio is None:
        if any(not isinstance(value, PairedObservation) for value in observations):
            raise ValueError("a non-ratio metric requires PairedObservation values")
        return estimate_paired_blocks(observations)  # type: ignore[arg-type]

    frozen = validate_ratio_estimand(ratio)
    if any(not isinstance(value, RatioObservation) for value in observations):
        raise ValueError("a ratio metric requires RatioObservation values")
    if frozen["form"] == "mean_of_request_ratios":
        return estimate_mean_of_request_ratios(observations)  # type: ignore[arg-type]
    if frozen["form"] == "ratio_of_totals":
        return estimate_ratio_of_totals(observations)  # type: ignore[arg-type]
    raise AssertionError("validated ratio form was not dispatchable")


__all__ = [
    "RATIO_ESTIMAND_KEYS",
    "RATIO_FORMS",
    "convert_floor_to_ratio_units",
    "estimate_manifest_observations",
    "estimation_metric",
    "ratio_collection_evidence_reasons",
    "ratio_evidence_reasons",
    "ratio_observation_from_evidence",
    "validate_ratio_estimand",
]
