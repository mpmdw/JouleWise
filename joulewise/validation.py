"""Shared validation primitives with no JouleWise-internal dependencies."""

from __future__ import annotations

import math
from typing import Any


def is_finite_number(value: Any) -> bool:
    """Return True for real finite JSON/Python numbers; bool is not numeric."""
    return (
        not isinstance(value, bool)
        and isinstance(value, int | float)
        and math.isfinite(value)
    )


def finite_float(value: Any, field_name: str) -> float:
    """Convert ``value`` to float and reject bool, NaN, and infinities."""
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a finite number: {value!r}")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a finite number: {value!r}") from exc
    if not math.isfinite(result):
        raise ValueError(f"{field_name} must be a finite number: {value!r}")
    return result
