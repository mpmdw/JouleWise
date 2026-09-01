#!/usr/bin/env python3
"""Registered dependence sensitivity for one ten-block ABBA contrast.

The command takes an authenticated JSON list of ten ordered B-minus-A block
deltas, the registered resolution floor, the stochastic-metrology standard
error carried by the analysis-engine artifact, and the deterministic-bound
total carried by that artifact.  It recomputes the registered composition
under three fixed dependence models.  It does not decide the two-contrast
Holm family procedure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.analysis_engine.distributions import (
    student_t_quantile,
    two_sided_student_t_p_value,
)


SCHEMA_VERSION = "joulewise.dependence_sensitivity.v1"
REGISTERED_ALPHA = 0.05
REGISTERED_N_BLOCKS = 10
EXAMPLE_FLOOR_J = 3.5
# These two values are invented solely for the arithmetic example.  Their
# field names match PairedEstimate.se_metrology and
# PairedEstimate.deterministic_bound_total in analysis_engine/estimators.py.
EXAMPLE_SE_METROLOGY_J = 0.2
EXAMPLE_DETERMINISTIC_BOUND_TOTAL_J = 4.0
# Mean 5 J, sample standard deviation 1.4 J, and centred lag-one slope 0.3
# exactly.
EXAMPLE_BLOCK_DELTAS_J = [
    5.0,
    7.6,
    5.5,
    4.2,
    4.7,
    6.8,
    5.5,
    3.6,
    3.9,
    3.2,
]


def _finite_number(value: object, name: str) -> float:
    """Return one finite real number, rejecting booleans and text."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number")
    return number


def _nonnegative_number(value: object, name: str) -> float:
    """Return one finite non-negative real number."""

    number = _finite_number(value, name)
    if number < 0.0:
        raise ValueError(f"{name} must be non-negative")
    return number


def _validated_deltas(block_deltas_j: object) -> list[float]:
    """Validate the registered ten-delta JSON payload before calculating."""

    if isinstance(block_deltas_j, (str, bytes)) or not isinstance(
        block_deltas_j, Sequence
    ):
        raise ValueError("block_deltas_j must be a JSON list")
    deltas = [
        _finite_number(value, f"block_deltas_j[{index}]")
        for index, value in enumerate(block_deltas_j)
    ]
    if len(deltas) != REGISTERED_N_BLOCKS:
        raise ValueError("exactly ten complete block deltas are required")
    return deltas


def estimate_ar1_rho(block_deltas_j: Sequence[float], mean_j: float) -> dict[str, float]:
    """Estimate adjacent-block relation with a centred preceding-to-following slope."""

    centred = [value - mean_j for value in block_deltas_j]
    numerator = math.fsum(
        centred[index] * centred[index - 1] for index in range(1, len(centred))
    )
    denominator = math.fsum(value * value for value in centred[:-1])
    if (
        not math.isfinite(numerator)
        or not math.isfinite(denominator)
        or denominator <= 0.0
    ):
        raise ValueError("AR(1) rho is undefined for this block-delta sequence")
    rho_hat = numerator / denominator
    if not math.isfinite(rho_hat) or abs(rho_hat) >= 1.0:
        raise ValueError("AR(1) rho must be finite and satisfy abs(rho) < 1")
    return {
        "numerator": numerator,
        "denominator": denominator,
        "rho_hat": rho_hat,
    }


def _ar1_variance_terms(n_blocks: int, rho: float) -> list[dict[str, float | int]]:
    """Return the finite-series terms that multiply the repeat variance."""

    if n_blocks < 2:
        raise ValueError("at least two blocks are required for an AR(1) multiplier")
    numeric_rho = _finite_number(rho, "rho")
    if abs(numeric_rho) >= 1.0:
        raise ValueError("AR(1) rho must be finite and satisfy abs(rho) < 1")
    return [
        {
            "lag": lag,
            "term": (1.0 - lag / n_blocks) * numeric_rho**lag,
        }
        for lag in range(1, n_blocks)
    ]


def ar1_variance_inflation_factor(n_blocks: int, rho: float) -> float:
    """Return the finite-n variance multiplier for an AR(1) sample mean."""

    terms = _ar1_variance_terms(n_blocks, rho)
    multiplier = 1.0 + 2.0 * math.fsum(float(row["term"]) for row in terms)
    # V*n = 1ᵀR1 > 0 because R is positive definite for |rho| < 1.
    return multiplier


def _degrees_of_freedom(n_blocks: int, effective_n: float) -> int:
    """Choose the registered conservative integral Student-t degree count."""

    if not math.isfinite(effective_n) or effective_n <= 0.0:
        raise ValueError("effective sample size is not positive and finite")
    degrees = min(n_blocks - 1, math.floor(effective_n) - 1)
    if degrees < 1:
        raise ValueError("effective sample size leaves fewer than two usable blocks")
    return degrees


def _interval(center: float, standard_error: float, critical: float) -> dict[str, float]:
    """Return one finite closed interval using the registered rounded critical."""

    half_width = critical * standard_error
    lower = center - half_width
    upper = center + half_width
    if not all(math.isfinite(value) for value in (half_width, lower, upper)):
        raise ValueError("interval is not finite")
    return {"lower": lower, "upper": upper}


def _strict_direction(interval: dict[str, float]) -> str | None:
    """Return the strict common sign of both endpoints, if either has one."""

    if interval["lower"] > 0.0 and interval["upper"] > 0.0:
        return "positive"
    if interval["lower"] < 0.0 and interval["upper"] < 0.0:
        return "negative"
    return None


def _model_result(
    *,
    name: str,
    description: str,
    mean_j: float,
    sample_stddev_j: float,
    n_blocks: int,
    effective_n: float,
    variance_inflation_factor: float,
    se_metrology_j: float,
    deterministic_bound_total_j: float,
    floor_j: float,
) -> dict[str, Any]:
    """Build one fully composed registered interval under one repeat model."""

    degrees = _degrees_of_freedom(n_blocks, effective_n)
    se_repeat = sample_stddev_j / math.sqrt(effective_n)
    se_total = math.hypot(se_repeat, se_metrology_j)
    critical = round(student_t_quantile(1.0 - REGISTERED_ALPHA / 2.0, degrees), 3)
    repeat_only_interval = _interval(mean_j, se_repeat, critical)
    metrology_aware_interval = _interval(mean_j, se_total, critical)
    decision_interval = {
        "lower": metrology_aware_interval["lower"] - deterministic_bound_total_j,
        "upper": metrology_aware_interval["upper"] + deterministic_bound_total_j,
    }
    if not all(math.isfinite(value) for value in decision_interval.values()):
        raise ValueError(f"{name} decision interval is not finite")
    half_width = critical * se_total
    if se_total <= 0.0:
        raise ValueError("total standard error must be positive")
    statistic = mean_j / se_total
    raw_p = two_sided_student_t_p_value(statistic, degrees)
    metrology_direction = _strict_direction(metrology_aware_interval)
    decision_direction = _strict_direction(decision_interval)
    return {
        "model": name,
        "description": description,
        "effective_n": effective_n,
        "degrees_of_freedom": degrees,
        "variance_inflation_factor": variance_inflation_factor,
        "se_repeat_j": se_repeat,
        "repeat_only_interval_j": repeat_only_interval,
        "se_metrology_j": se_metrology_j,
        "se_total_j": se_total,
        "t_critical_95": critical,
        "half_width_j": half_width,
        "metrology_aware_interval_j": metrology_aware_interval,
        "deterministic_bound_total_j": deterministic_bound_total_j,
        "decision_interval_j": decision_interval,
        "t_statistic": statistic,
        "raw_two_sided_p": raw_p,
        "floor_gate": {
            "rule": "abs(mean_j) > registered_floor_j",
            "registered_floor_j": floor_j,
            "passes": abs(mean_j) > floor_j,
        },
        "direction_gate": {
            "rule": "both endpoints of both fully composed intervals have the same strict sign",
            "metrology_aware_direction": metrology_direction,
            "decision_direction": decision_direction,
            "passes": metrology_direction is not None
            and metrology_direction == decision_direction,
        },
    }


def _canonical_json(value: object) -> str:
    """Return the artifact's fixed UTF-8 JSON representation for hashing."""

    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


def _sha256_text(value: str) -> str:
    """Return the hexadecimal SHA-256 digest of one UTF-8 string."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def analyze_deltas(
    block_deltas_j: object,
    *,
    floor_j: object,
    se_metrology_j: object,
    deterministic_bound_total_j: object,
) -> dict[str, Any]:
    """Compute the three registered dependence models for exactly ten blocks."""

    deltas = _validated_deltas(block_deltas_j)
    registered_floor = _nonnegative_number(floor_j, "floor_j")
    se_metrology = _nonnegative_number(se_metrology_j, "se_metrology_j")
    deterministic_total = _nonnegative_number(
        deterministic_bound_total_j, "deterministic_bound_total_j"
    )

    n_blocks = len(deltas)
    total_j = math.fsum(deltas)
    mean_j = total_j / n_blocks
    squared_deviations_sum_j2 = math.fsum((value - mean_j) ** 2 for value in deltas)
    sample_stddev_j = math.sqrt(squared_deviations_sum_j2 / (n_blocks - 1))
    if not math.isfinite(sample_stddev_j):
        raise ValueError("sample standard deviation is not finite")
    rho = estimate_ar1_rho(deltas, mean_j)
    ar1_terms = _ar1_variance_terms(n_blocks, rho["rho_hat"])
    variance_inflation = ar1_variance_inflation_factor(n_blocks, rho["rho_hat"])
    ar1_effective_n = n_blocks / variance_inflation
    half_effective_n = n_blocks / 2.0

    models = {
        "independent_blocks": _model_result(
            name="independent_blocks",
            description="registered composition with n_eff = n",
            mean_j=mean_j,
            sample_stddev_j=sample_stddev_j,
            n_blocks=n_blocks,
            effective_n=float(n_blocks),
            variance_inflation_factor=1.0,
            se_metrology_j=se_metrology,
            deterministic_bound_total_j=deterministic_total,
            floor_j=registered_floor,
        ),
        "ar1_estimated_rho": _model_result(
            name="ar1_estimated_rho",
            description="finite-n AR(1) repeat-variance sensitivity",
            mean_j=mean_j,
            sample_stddev_j=sample_stddev_j,
            n_blocks=n_blocks,
            effective_n=ar1_effective_n,
            variance_inflation_factor=variance_inflation,
            se_metrology_j=se_metrology,
            deterministic_bound_total_j=deterministic_total,
            floor_j=registered_floor,
        ),
        "fixed_effective_n_halving": _model_result(
            name="fixed_effective_n_halving",
            description="fixed effective-n halving (a named pessimistic scenario, not a bound)",
            mean_j=mean_j,
            sample_stddev_j=sample_stddev_j,
            n_blocks=n_blocks,
            effective_n=half_effective_n,
            variance_inflation_factor=2.0,
            se_metrology_j=se_metrology,
            deterministic_bound_total_j=deterministic_total,
            floor_j=registered_floor,
        ),
    }
    direction_outcomes = [row["direction_gate"]["passes"] for row in models.values()]
    block_deltas_json = _canonical_json(deltas)
    metrology_inputs = {
        "se_metrology_j": se_metrology,
        "deterministic_bound_total_j": deterministic_total,
    }
    metrology_inputs_json = _canonical_json(metrology_inputs)
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "registered_dependence_sensitivity",
        "input_authentication": {
            "canonical_json": "UTF-8 JSON with ensure_ascii=false and separators=(',', ':')",
            "block_deltas_json_sha256": _sha256_text(block_deltas_json),
            "metrology_inputs": metrology_inputs,
            "metrology_inputs_json_sha256": _sha256_text(metrology_inputs_json),
        },
        "input": {
            "block_deltas_j": deltas,
            "registered_floor_j": registered_floor,
            "registered_alpha": REGISTERED_ALPHA,
            **metrology_inputs,
        },
        "summary": {
            "n_blocks": n_blocks,
            "sum_j": total_j,
            "mean_j": mean_j,
            "squared_deviations_sum_j2": squared_deviations_sum_j2,
            "sample_stddev_j": sample_stddev_j,
        },
        "ar1_rho_estimator": {
            "method": "centred_conditional_least_squares_lag1_v1",
            "formula": "sum((d_i-mean)*(d_i_minus_1-mean), i=2..n) / sum((d_i_minus_1-mean)^2, i=2..n)",
            **rho,
        },
        "ar1_variance_terms": ar1_terms,
        "models": models,
        "comparison": {
            "direction_gate_outcomes_agree": len(set(direction_outcomes)) == 1,
        },
    }


def _json_list_from_text(text: str, source: str) -> object:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{source} is not valid JSON: {exc.msg}") from exc
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--block-deltas", help="JSON list of ten complete ABBA block deltas in joules"
    )
    source.add_argument(
        "--block-deltas-file", type=Path, help="UTF-8 file containing that JSON list"
    )
    parser.add_argument("--floor", type=float, help="registered non-negative floor in joules")
    parser.add_argument(
        "--se-metrology",
        type=float,
        help="registered stochastic-metrology standard error in joules",
    )
    parser.add_argument(
        "--deterministic-bound-total",
        type=float,
        help="registered deterministic-bound total in joules",
    )
    parser.add_argument("--example", action="store_true", help="print the worked example")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.example:
        if (
            args.block_deltas is not None
            or args.block_deltas_file is not None
            or args.floor is not None
            or args.se_metrology is not None
            or args.deterministic_bound_total is not None
        ):
            parser.error(
                "--example cannot be combined with input, --floor, --se-metrology, "
                "or --deterministic-bound-total"
            )
        deltas: object = EXAMPLE_BLOCK_DELTAS_J
        floor = EXAMPLE_FLOOR_J
        se_metrology = EXAMPLE_SE_METROLOGY_J
        deterministic_total = EXAMPLE_DETERMINISTIC_BOUND_TOTAL_J
    else:
        if args.block_deltas is None and args.block_deltas_file is None:
            parser.error(
                "one of --block-deltas or --block-deltas-file is required unless --example is used"
            )
        if (
            args.floor is None
            or args.se_metrology is None
            or args.deterministic_bound_total is None
        ):
            parser.error(
                "--floor, --se-metrology, and --deterministic-bound-total are required unless --example is used"
            )
        try:
            if args.block_deltas_file is not None:
                deltas = _json_list_from_text(
                    args.block_deltas_file.read_text(encoding="utf-8"),
                    str(args.block_deltas_file),
                )
            else:
                assert args.block_deltas is not None
                deltas = _json_list_from_text(args.block_deltas, "--block-deltas")
        except OSError as exc:
            parser.error(f"cannot read block-delta JSON: {exc}")
        except (ValueError, OverflowError) as exc:
            parser.error(str(exc))
        floor = args.floor
        se_metrology = args.se_metrology
        deterministic_total = args.deterministic_bound_total
    try:
        result = analyze_deltas(
            deltas,
            floor_j=floor,
            se_metrology_j=se_metrology,
            deterministic_bound_total_j=deterministic_total,
        )
    except (ValueError, OverflowError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
