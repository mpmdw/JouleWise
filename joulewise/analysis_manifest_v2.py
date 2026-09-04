"""Registry-extensible validation layered over the frozen v1 manifest API.

The v1 module is evidence-pinned and deliberately retains its four literal
AP-2 metric rows.  This sibling preserves that validator unchanged while
allowing successor registry declarations whose metric/window identities are
authenticated by the frozen detection-floor closed-set registry.
"""

from __future__ import annotations

import itertools
import re
from collections.abc import Mapping
from typing import Any

from . import analysis_manifest as v1
from .analysis_manifest import AnalysisPlanRow, extract_analysis_plan_row
from .detection_floor_registry import default_detection_floor_closed_sets


def _exact_keys(
    value: Mapping[str, Any],
    expected: set[str],
    where: str,
    errors: list[str],
) -> bool:
    observed = set(value)
    if observed == expected:
        return True
    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    detail = []
    if missing:
        detail.append(f"missing {missing}")
    if extra:
        detail.append(f"unexpected {extra}")
    errors.append(f"{where}: {'; '.join(detail)}")
    return False


def _validate_registered_metrics(value: Any, errors: list[str]) -> None:
    closed_sets = default_detection_floor_closed_sets()
    if not isinstance(value, list) or not value:
        errors.append("registry.metrics: must contain at least one declared metric row")
        return

    metric_tags: list[str] = []
    metric_names: list[str] = []
    for index, metric in enumerate(value):
        where = f"registry.metrics[{index}]"
        if not isinstance(metric, Mapping):
            errors.append(f"{where}: expected an object")
            continue
        if not _exact_keys(metric, v1.METRIC_KEYS, where, errors):
            continue

        metric_tag = metric["metric_tag"]
        name = metric["name"]
        window_class = metric["window_class"]
        if not isinstance(metric_tag, str) or not v1.ID_RE.fullmatch(metric_tag):
            errors.append(f"{where}.metric_tag: invalid identifier")
        else:
            metric_tags.append(metric_tag)

        registered_window_class = (
            closed_sets.metric_window_classes.get(name)
            if isinstance(name, str)
            else None
        )
        if registered_window_class is None:
            errors.append(
                f"{where}.name: not declared by the authenticated detection-floor registry"
            )
        else:
            metric_names.append(name)
            if window_class != registered_window_class:
                errors.append(
                    f"{where}.window_class: expected {registered_window_class!r} "
                    "from the authenticated detection-floor registry"
                )
        if metric["unit"] != "J" or metric["ratio_estimand"] is not None:
            errors.append(f"{where}: AP-2 v1 requires unit J and ratio_estimand null")

    if len(metric_tags) != len(set(metric_tags)):
        errors.append("registry.metrics: duplicate metric_tag")
    if len(metric_names) != len(set(metric_names)):
        errors.append("registry.metrics: duplicate metric name")


def _validate_condition_pairs(
    value: Any,
    ap_row: AnalysisPlanRow | None,
    errors: list[str],
) -> None:
    observed_pairs: list[tuple[str, str]] = []
    if not isinstance(value, list) or not value:
        errors.append("registry.condition_pairs: must contain at least one declared pair")
        return

    for index, pair in enumerate(value):
        where = f"registry.condition_pairs[{index}]"
        if not isinstance(pair, Mapping):
            errors.append(f"{where}: expected an object")
            continue
        if not _exact_keys(pair, v1.REGISTRY_PAIR_KEYS, where, errors):
            continue
        condition_a = pair["condition_a"]
        condition_b = pair["condition_b"]
        if not isinstance(condition_a, str) or not v1.ID_RE.fullmatch(condition_a):
            errors.append(f"{where}.condition_a: invalid identifier")
        if not isinstance(condition_b, str) or not v1.ID_RE.fullmatch(condition_b):
            errors.append(f"{where}.condition_b: invalid identifier")
        if isinstance(condition_a, str) and condition_a == condition_b:
            errors.append(f"{where}: a condition cannot be paired with itself")
        if isinstance(condition_a, str) and isinstance(condition_b, str):
            observed_pairs.append((condition_a, condition_b))

    if len(observed_pairs) != len(set(observed_pairs)):
        errors.append("registry.condition_pairs: duplicate ordered pair")
    if ap_row is None:
        return

    selection_scope = ap_row.values["selection_scope"]
    scope_profiles = tuple(
        dict.fromkeys(re.findall(r"`([a-z0-9_]+)`", selection_scope))
    )
    if len(scope_profiles) != 4 or not selection_scope.startswith(
        "Frozen four-profile 2M matrix:"
    ):
        errors.append(
            "AP-2 selection_scope must declare the frozen four-profile 2M matrix"
        )
        return

    valid_pairs = [
        pair
        for pair in observed_pairs
        if pair[0] in scope_profiles
        and pair[1] in scope_profiles
        and pair[0] != pair[1]
    ]
    observed_profiles = {profile for pair in valid_pairs for profile in pair}
    if len(valid_pairs) != len(observed_pairs) or observed_profiles != set(scope_profiles):
        errors.append("registry.condition_pairs: profiles must match AP-2 selection_scope")

    observed_unordered = [frozenset(pair) for pair in valid_pairs]
    expected_unordered = {
        frozenset(pair) for pair in itertools.combinations(scope_profiles, 2)
    }
    if (
        len(observed_unordered) != len(set(observed_unordered))
        or set(observed_unordered) != expected_unordered
    ):
        errors.append(
            "registry.condition_pairs: must cover every pair in AP-2's "
            "frozen four-profile selection_scope exactly once"
        )


def validate_analysis_registry(
    value: Mapping[str, Any],
    *,
    ap_row: AnalysisPlanRow | None = None,
) -> list[str]:
    """Validate v1 declarations, extending only metric and pair enumeration.

    Exact frozen v1 declarations return directly from the frozen validator.
    Successor declarations retain every other v1 check; their metric identities
    are admitted only after the detection-floor registry authenticates them.
    """

    v1_errors = v1.validate_analysis_registry(value, ap_row=ap_row)
    if not v1_errors:
        return []
    if any(error.startswith("registry: ") for error in v1_errors):
        return v1_errors

    errors = [
        error
        for error in v1_errors
        if not error.startswith("registry.metrics")
        and not error.startswith("registry.condition_pairs")
    ]
    _validate_registered_metrics(value["metrics"], errors)
    _validate_condition_pairs(value["condition_pairs"], ap_row, errors)
    return errors


__all__ = [
    "AnalysisPlanRow",
    "extract_analysis_plan_row",
    "validate_analysis_registry",
]
